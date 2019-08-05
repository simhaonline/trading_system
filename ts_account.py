# Documentation
# Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
# Python-Binance master document  https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
# Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
# More useful information (quick reference)     https://python-binance.readthedocs.io/en/latest/binance.html

from binance.client import Client
import pandas as pd
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import dateparser as dp


class Account():
    """Account functions"""   
    def __init__(self):
        self.symbol_history_file = 'D:/Python/python_work/trading_system/symbol_history'
        self.login()
        plt.style.use('seaborn-deep')
        

    def login(self):
        """Creates Binance client"""
        file = 'c:/python/python_work/credentials.txt'
        with open(file) as f_obj:
            lines = [line.rstrip('\n') for line in f_obj]
            api_key = lines[0]
            api_secret = lines[1]
            self.client = Client(api_key, api_secret)


    def my_trades(self, symbol):
        """Returns current BTC/USD price"""
        trades = self.client.get_my_trades(symbol=symbol)
        return trades
    