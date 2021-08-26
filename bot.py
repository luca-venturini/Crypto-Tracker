import requests
import telegram
import _thread as thread
import os
import time
import json
from telegram.ext import *
from telegram import *
from tracker import get_prices, get_top_coins, get_graph_info, get_percentage_info
from dotenv import load_dotenv
import os

load_dotenv()
PORT = int(os.environ.get('PORT', 8443))

bot = Bot(os.getenv('BOT_TOKEN'))
updater = Updater(token=os.getenv('BOT_TOKEN'), use_context=True)
dispatcher = updater.dispatcher
MAX_ALERT_LIMIT = 1000
alerts_count = 0

def get(update, context):
    chat_id = update.effective_chat.id
    text = ""
    try:
        text = update.message.text
    except Exception as exc:
        print(exc)
    coin = text.split()[1] # gets type of coin
    try:
        message = f"Ticker: {coin}"
        keyboard = [
            [
                InlineKeyboardButton("Price", callback_data=json.dumps({'action': "price", 'coin': coin}) ),
                InlineKeyboardButton("Hour Change", callback_data=json.dumps({'action': "hourChange", 'coin': coin}) ),
            ],
            [
                InlineKeyboardButton("Day Change", callback_data=json.dumps({'action': "dayChange", 'coin': coin}) ),
                InlineKeyboardButton("Market Cap", callback_data=json.dumps({'action': "marketCap", 'coin': coin}) ),
            ],
            [
                InlineKeyboardButton("Volume Traded Today", callback_data=json.dumps({'action': "volumeTraded", 'coin': coin}) ),
                InlineKeyboardButton("Day Opening Price", callback_data=json.dumps({'action': "dayOpening", 'coin': coin}) ),

            ],
            [
                InlineKeyboardButton("Day High", callback_data=json.dumps({'action': "dayHigh", 'coin': coin}) ),
                InlineKeyboardButton("Day Low", callback_data=json.dumps({'action': "dayLow", 'coin': coin}) ),
            ],
            [
                InlineKeyboardButton("Percentage", callback_data=json.dumps({'action': "percentage", 'coin': coin}) ),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text=message)
        update.message.reply_text('Please choose the data you are interested in:', reply_markup=reply_markup)

    except: # request had an error

        context.bot.send_message(chat_id=chat_id, text="The specified coin was not found in our API. Please check that you have the correct ticker symbol")

def graph(update, context):
    text = update.message.text
    try:
        chat_id = update.effective_chat.id
        text = update.message.text
        coin = text.split()[1] # gets type of coin
        keyboard = [
            [
                InlineKeyboardButton("Minute", callback_data=json.dumps({'action': "min", 'coin': coin}) ),
                InlineKeyboardButton("Hour", callback_data=json.dumps({'action': "hour", 'coin': coin}) ),
                InlineKeyboardButton("Day", callback_data=json.dumps({'action': "day", 'coin': coin}) ),
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Please choose the interval:', reply_markup=reply_markup)

    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id, text="Error while generating graph")

# returns top X coins by market cap
def top(update,context):
    chat_id = update.effective_chat.id

    try:
        coins = get_top_coins(10)
        message = ""
        for coin in coins:
            message +=  f"Name: {coin['name']}\nTicker Symbol: {coin['ticker']}\nCurrent Price: {coin['price']}\nMarket Cap: {coin['market_cap']}\nVolume Traded Today: {coin['volume_day']}\nDay Opening Price: {coin['day_open']}\nDay High: {coin['day_high']}\nDay Low: {coin['day_low']}\nPerc 24 hours: {coin['perc_24_hrs']}%\nPerc today: {coin['perc_today']}%\nPerc last hour: {coin['perc_hour']}%\n\n"

        context.bot.send_message(chat_id=chat_id,text=message)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id,text="Unknown error. Please try again later")

# polling function to be ran on a seperate thread
def thread_poller(chat_id,context,alert):
    # Time in seconds to delay thread
    alerts_count = 0
    DELAY = 60
    while True:

        coin,isAbove,threshold_price = alert
        data = get_prices(coin)
        currentPrice = float(data["price"][1:].replace(',','')) # First character is the dollar sign
        if isAbove:
            if currentPrice > threshold_price:
                message = f"Price of {data['ticker']} is now at {data['price']} and above your threshold price of ${threshold_price}"
                context.bot.send_message(chat_id=chat_id,text=message)
                context.bot.send_message(chat_id=chat_id,text="Alert removed from the system")
                alerts_count -= 1
                break
        elif currentPrice < threshold_price:
            message = f"Price of {data['ticker']} is now at {data['price']} and below your threshold price of ${threshold_price}"
            context.bot.send_message(chat_id=chat_id,text=message)
            context.bot.send_message(chat_id=chat_id,text="Alert is now removed from the system")
            alerts_count -= 1
            break

        time.sleep(DELAY)

def alert(update,context):
    alerts_count = 0
    chat_id = update.effective_chat.id
    text = update.message.text.split()
    try:
        if text[2].lower() == "above":
            isAbove = True
        elif text[2].lower() == "below":
            isAbove = False
        else:
            raise ValueError

        threshold_price = float(text[3])

        alert=(text[1],isAbove,threshold_price)
        if alerts_count + 1 < MAX_ALERT_LIMIT:
            alerts_count += 1
            context.bot.send_message(chat_id= chat_id, text= "Alert successfully set")
            thread.start_new_thread(thread_poller,(chat_id,context,alert))
        else:
            context.bot.send_message(chat_id= chat_id, text= "There are too many alerts currently running on our system. Please try again later")

    except Exception as e:
        print(e)
        context.bot.send_message(chat_id=chat_id,text="Invalid input format")

def help(update, context):
    chat_id = update.effective_chat.id
    text = update.message.text
    message = f'Hello. Thanks for using the CryptoAlert Bot 🤖 \n\nCommands available:\n/get <coin> -- Retrieve pricing data 💰 for a specific coin\n<coin> -- Ticker symbol of a coin\n\n/top -- Retrieve data for the largest 10 🎖 cyptocurrencies by market cap.\n\n/graph <coin> -- Plots a line graph 📈 of closing price for a particular coin over 10 counts of the selected interval \n<coin> -- Ticker symbol of a coin\n\n/alert <coin> <direction> <threshold> -- Sets an alert ⏰ that triggers when the price of the coin crosses the specified threshold \n<coin> -- Ticker symbol of a coin\n<direction> -- Either "above" or "below"\n<threshold> -- Price to cross'
    update.message.reply_text(message)


def create_message(update, context, message, attribute):
    query : CallbackQuery = update.callback_query
    chat_id = update.effective_chat.id

    data = json.loads(query.data)
    coin = data['coin']
    action = data['action']
    crypto_data = get_prices(coin)

    message = f"{message} is: {crypto_data[attribute]}"
    context.bot.send_message(chat_id=chat_id, text=message)



def price(update, context):
    create_message(update, context, 'Price', 'price')

def change_hour(update, context):
    create_message(update, context, 'Hourly change', 'change_hour')

def change_day(update, context):
    create_message(update, context, 'Daily change', 'change_day')

def market_cap(update, context):
    create_message(update, context, 'Market cap', 'market_cap')

def volume_day(update, context):
    create_message(update, context, 'Volume Traded Today', 'volume_day')

def volume_day(update, context):
    create_message(update, context, 'Volume Traded Today', 'volume_day')

def day_open(update, context):
    create_message(update, context, 'Day opening price', 'day_open')

def day_high(update, context):
    create_message(update, context, 'Day high price', 'day_high')

def day_low(update, context):
    create_message(update, context, 'Day low price', 'day_low')

def percentage(update, context):
    query : CallbackQuery = update.callback_query
    chat_id = update.effective_chat.id

    data = json.loads(query.data)
    coin = data['coin']
    action = data['action']
    crypto_data = get_prices(coin)
    last24hours, today, hour = get_percentage_info(coin)
    message = f"{coin} percentage: \n\nPercentage last 24hrs: {last24hours} % \nPercentage today: {today} % \nPercentage last hour: {hour} % \n"
    context.bot.send_message(chat_id=chat_id, text=message)

def minute(update, context):
    query : CallbackQuery = update.callback_query
    chat_id = update.effective_chat.id

    data = json.loads(query.data)
    coin = data['coin']
    action = data['action']
    crypto_data = get_prices(coin)
    path = get_graph_info("minute",coin)
    context.bot.send_photo(chat_id, photo=open(path, 'rb')) # sends a photo according to path

def day(update, context):
    query : CallbackQuery = update.callback_query
    chat_id = update.effective_chat.id

    data = json.loads(query.data)
    coin = data['coin']
    action = data['action']
    crypto_data = get_prices(coin)
    path = get_graph_info("day",coin)
    context.bot.send_photo(chat_id, photo=open(path, 'rb')) # sends a photo according to path

def hour(update, context):
    query : CallbackQuery = update.callback_query
    chat_id = update.effective_chat.id

    data = json.loads(query.data)
    coin = data['coin']
    action = data['action']
    crypto_data = get_prices(coin)
    path = get_graph_info("hour",coin)
    context.bot.send_photo(chat_id, photo=open(path, 'rb')) # sends a photo according to path


dispatcher.add_handler(CommandHandler("help", help)) # links /help and /start with the help function
dispatcher.add_handler(CommandHandler("start", help)) # links /help and /start with the help function
dispatcher.add_handler(CommandHandler("get", get)) # links /get with the get function
dispatcher.add_handler(CommandHandler("top", top))
dispatcher.add_handler(CommandHandler("graph", graph))
dispatcher.add_handler(CommandHandler("alert", alert))



updater.dispatcher.add_handler(CallbackQueryHandler(price, pattern='{"action": "price"'))
updater.dispatcher.add_handler(CallbackQueryHandler(change_hour, pattern='{"action": "hourChange"'))
updater.dispatcher.add_handler(CallbackQueryHandler(change_day, pattern='{"action": "dayChange"'))
updater.dispatcher.add_handler(CallbackQueryHandler(market_cap, pattern='{"action": "marketCap"'))
updater.dispatcher.add_handler(CallbackQueryHandler(volume_day, pattern='{"action": "volumeTraded"'))
updater.dispatcher.add_handler(CallbackQueryHandler(day_open, pattern='{"action": "dayOpening"'))
updater.dispatcher.add_handler(CallbackQueryHandler(day_high, pattern='{"action": "dayHigh"'))
updater.dispatcher.add_handler(CallbackQueryHandler(day_low, pattern='{"action": "dayLow"'))
updater.dispatcher.add_handler(CallbackQueryHandler(percentage, pattern='{"action": "percentage"'))
updater.dispatcher.add_handler(CallbackQueryHandler(minute, pattern='{"action": "minute"'))
updater.dispatcher.add_handler(CallbackQueryHandler(hour, pattern='{"action": "hour"'))
updater.dispatcher.add_handler(CallbackQueryHandler(day, pattern='{"action": "day"'))

updater.start_polling()
updater.idle()
