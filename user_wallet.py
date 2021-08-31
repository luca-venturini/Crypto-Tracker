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

class UserWallet:

    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.cryptos = set()

    def add_crypto(self, ticker):
        self.cryptos.add(ticker)

    def remove_crypto(self, ticker):
        self.cryptos.discard(ticker)

    def get_percentages(self):
        data = []
        for crypto in self.cryptos:
            try:
                h24, day, hour = get_percentage_info(crypto)
            except Exception as e:
                h24 = "Crypto not found"
                day = hour = "-"
            data.append([crypto, h24, day, hour])
        return data

    def is_chat_id(self, id):
        return chat_id == id
