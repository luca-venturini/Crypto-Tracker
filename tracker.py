import requests
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import datetime


CURRENCY = "EUR"

def get_prices(coin):
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}".format(coin, CURRENCY)).json()["DISPLAY"][coin][CURRENCY]
    data = {
        "ticker": coin,
        "price": crypto_data["PRICE"],
        "change_day": crypto_data["CHANGEDAY"],
        "change_hour": crypto_data["CHANGEHOUR"],
        "market_cap": crypto_data["MKTCAP"],
        "volume_day": crypto_data["VOLUMEDAYTO"],
        "day_open": crypto_data["OPENDAY"],
        "day_high": crypto_data["HIGHDAY"],
        "day_low": crypto_data["LOWDAY"]
    }

    return data

def get_percentage_info(coin):
    try:
        crypto_data = requests.get("https://min-api.cryptocompare.com/data/pricemultifull?fsyms={}&tsyms={}".format(coin, CURRENCY)).json()["DISPLAY"][coin][CURRENCY]
    except:
        raise Exception("Crypto not found!")

    return crypto_data['CHANGEPCT24HOUR'], crypto_data['CHANGEPCTDAY'], crypto_data['CHANGEPCTHOUR']


def get_graph_info(rate,coin):
    crypto_data = requests.get(
        "https://min-api.cryptocompare.com/data/v2/histo{}?fsym={}&tsym={}&limit=10".format(rate,coin,CURRENCY)).json()
    data = {}
    times = []
    price = []
    for i in range(1, 11):
        t = (crypto_data['Data']['Data'][i]['time'])
        timestamp = datetime.datetime.fromtimestamp(t)
        times.append(timestamp)
        price.append(crypto_data['Data']['Data'][i]['close'])

    data['time'] = times
    data['price'] = price
    fig, ax = plt.subplots(figsize=(8, 8))
    plt.xticks(rotation=30)

    plt.title('{} Close prices for the last 10 {}s'.format(coin,rate))
    plt.xlabel('Time')
    if rate == "hour":
        label = "Hourly"
    elif rate == "day":
        label = "Daily"
    elif rate == "minute":
        label = "Minute"
    plt.ylabel('{} Close Prices'.format(label))

    plt.plot_date(times, price)
    plt.plot(times,price)
    ax = plt.gca()
    ax.set_facecolor((0.84,0.84,0.84))

    date_form = DateFormatter("%d-%m %H:%M")
    ax.xaxis.set_major_formatter(date_form)
    path = "graphs/{}.png".format(coin)
    plt.savefig(path)

    return path

def get_top_coins(count):
    crypto_coins = requests.get(f"https://min-api.cryptocompare.com/data/top/mktcapfull?limit={count}&tsym={CURRENCY}").json()["Data"]
    coins = [{} for i in range(int(count))]
    for i in range(len(crypto_coins)):
        data = {
            "ticker": crypto_coins[i]["CoinInfo"]["Name"],
            "name": crypto_coins[i]["CoinInfo"]["FullName"],
            "price": crypto_coins[i]["DISPLAY"][CURRENCY]["PRICE"],
            "market_cap": crypto_coins[i]["DISPLAY"][CURRENCY]["MKTCAP"],
            "volume_day": crypto_coins[i]["DISPLAY"][CURRENCY]["VOLUMEDAYTO"],
            "day_open": crypto_coins[i]["DISPLAY"][CURRENCY]["OPENDAY"],
            "day_high": crypto_coins[i]["DISPLAY"][CURRENCY]["HIGHDAY"],
            "day_low": crypto_coins[i]["DISPLAY"][CURRENCY]["LOWDAY"],
            "perc_24_hrs": crypto_coins[i]["DISPLAY"][CURRENCY]["CHANGEPCT24HOUR"],
            "perc_today": crypto_coins[i]["DISPLAY"][CURRENCY]["CHANGEPCTDAY"],
            "perc_hour": crypto_coins[i]["DISPLAY"][CURRENCY]["CHANGEPCTHOUR"]
        }
        coins[i] = data

    return coins
