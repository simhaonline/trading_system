# Documentation
# Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
# Python-Binance master document  https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
# Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
# More useful information (quick reference)     https://python-binance.readthedocs.io/en/latest/binance.html

from binance.client import Client
import json
import pandas as pd
import os
import numpy as np




class Account():
    """Account functions"""

    def __init__(self, file):
        self.login(file)

    def login(self, file):
        """Creates Binance client"""
        with open(file) as f_obj:
            lines = [line.rstrip('\n') for line in f_obj]
            api_key = lines[0]
            api_secret = lines[1]
            self.client = Client(api_key, api_secret)

    def my_trades(self, symbol):
        """Returns current BTC/USD price"""
        trades = self.client.get_my_trades(symbol=symbol)
        return trades
    

class Trader(Account):
    """Trading functions"""
    def __init__(self, file, pair, tick_size, start, end):
        super().__init__(file)
        self.pair = pair
        self.tick_size = tick_size
        self.start = start
        self.end = end
        self.request = self.pair, self.tick_size, self.start, self.end
    
    def ohlc_data_download(self, pair, tick_size, start, end, limit=1000, filepath='D:/Python/symbol_history'):
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time."""
        klines = self.client.get_historical_klines(pair, tick_size, start, end, limit)
        # formatting table
        column_headers = [
            'Open time',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Close time',
            'Quote asset volume',
            'Number of trades',
            'Taker buy base asset volume',
            'Taker buy quote asset volume',
            'Ignore'
        ]
        df = pd.DataFrame(klines, columns=column_headers)
        float_columns = column_headers[1:6] + column_headers[7:11]
        open_datetime = pd.to_datetime(df['Open time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, "Open datetime", open_datetime)
        close_datetime = pd.to_datetime(df['Close time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(7, "Close datetime", close_datetime)
        df.drop('Ignore', axis='columns', inplace=True)
        for fl_col in float_columns:
            df['{}'.format(fl_col)] = pd.to_numeric(df['{}'.format(fl_col)], downcast='float', errors='coerce')
        # saving table
        if not os.path.exists("{}/{}".format(filepath, pair)):
            os.makedirs("{}/{}".format(filepath, pair))                       
        df.to_csv("{}/{}/{}_{}.csv".format(filepath, pair, pair, tick_size), index=False)
        with open("{}/{}/{}_{}.json".format(filepath, pair, pair, tick_size), 'w') as f_obj:
            df_json = df.to_json()
            json.dump(df_json, f_obj)
        print("Data for {}_{}".format(pair, tick_size) + " has been updated.")  

    def get_all_symbols(self):
        """Generates a list of all symbols on Binance"""
        info = self.client.get_exchange_info()
        symbols_dic = info['symbols']
        all_symbols = []
        for dic in symbols_dic:
            if dic['baseAsset'] not in all_symbols:
                all_symbols.append(dic['baseAsset'])
        self.all_symbols = all_symbols 
        
        # return all_trading_pairs
    def get_all_pairs(self):
        """Generates a list of all possible trading pairs"""
        info = self.client.get_exchange_info()
        pairs_dic = info['symbols']
        all_pairs = []
        for dic in pairs_dic:
            if dic['symbol'] not in all_pairs:
                all_pairs.append(dic['symbol'])
        self.all_pairs = all_pairs
     
    def files_update_pairs_folders(self):
        """After appending new data to file, timestamp is recorded and used as start time for next data download so that data isn't added twice."""
        filepath = "D:/Python/symbol_history"
        new_folders = []
        for pair in self.all_pairs:
            if not os.path.exists("{}/{}".format(filepath, pair)):
                os.makedirs("{}/{}".format(filepath, pair))
                new_folders.append(pair)
        print("New folders added: " + str(len(new_folders)))
        if new_folders:
            print("\nThere is no stored data for the following pairs:")
            for pair in new_folders:
                print("-" + pair)                

    def latest_timestamp_ohlc(self, pair, tick_size, filepath='D:/Python/symbol_history'):
        """Return the lastest timestamp for the data already on file for a given pair and tick size"""
        try:
            with open('{}/{}/{}_{}.csv'.format(filepath,pair, pair, tick_size),'rb') as f:
                lines = f.readlines()
                last_line = np.genfromtxt(lines[-1:],delimiter=',')
                return last_line[1]
        except FileNotFoundError:
            print("No data on file for {}_{}".format(pair, tick_size))
                
        

        
    
    





     





# login
file = 'c:/python/python_work/credentials.txt'

# Provide strategy details
pair = 'ETHBTC'

tick_size = "1w"
start = "1 Jan, 2019"
end = "now"


# downloading data - want to append new lines of data to old csv files, can know where the last stopped by creating a python file that records the last updated time.  


# strategy details
#tx_fee = 0.01

# backtesting


# Code to run
trader = Trader(file, pair, tick_size, start, end)
#trader.ohlc_data_download(pair, tick_size, start, end)
#trader.get_all_pairs()
#trader.get_all_symbols()
#trader.latest_timestamp_ohlc(pair, tick_size)
#trader.files_update_pairs_folders()
print(trader.request)
print(trader.pair)
