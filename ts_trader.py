# Documentation
# Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
# Python-Binance master document              https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
# Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
# More useful information                     https://python-binance.readthedocs.io/en/latest/binance.html

from ts_account import Account
from binance.client import Client
import pandas as pd
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import dateparser as dp


class Trader(Account):
    """Trading functions"""
    def __init__(self, pair, tick_size, start, end):
        super().__init__()
        self.pair = pair
        self.tick_size = tick_size
        self.start = start
        self.end = end
        self.update_symbols()        
        
        
    def ohlc_return_column_headers(self):
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
            'Ignore']
        return column_headers
    
    
    def ohlc_get_data(self, pair, tick_size, start, end, limit=1000):
        """Kline/candlestick bars for a symbol. Klines (ohlc candlesticks) are uniquely identified by their open time."""
        ohlc_data = self.client.get_historical_klines(pair, tick_size, start, end, limit)
        return ohlc_data
        
    
    def ohlc_format_data(self, ohlc_data):    
        """With the ohlc data from Binance, format into DataFrames that are useful"""
        column_headers = Trader.ohlc_return_column_headers(self)
        df = pd.DataFrame(ohlc_data, columns=column_headers)
        float_columns = column_headers[1:6] + column_headers[7:11]
        open_datetime = pd.to_datetime(df['Open time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, "Open datetime", open_datetime)
        close_datetime = pd.to_datetime(df['Close time'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(7, "Close datetime", close_datetime)
        df.drop('Ignore', axis='columns', inplace=True)
        for fl_col in float_columns:
            df['{}'.format(fl_col)] = pd.to_numeric(df['{}'.format(fl_col)], downcast='float', errors='coerce')
        return df
        
    
    def ohlc_save_data(self, ohlc_formatted, pair, tick_size):
        filepath = self.symbol_history_file        
        if not os.path.exists("{}/{}".format(filepath, pair)):
            os.makedirs("{}/{}".format(filepath, pair))                       
        ohlc_formatted.to_csv("{}/{}/{}_{}.csv".format(filepath, pair, pair, tick_size), index=False)
        print("{}_{}".format(pair, tick_size) + " has been updated.")  
        
        
    def ohlc(self, pair, tick_size, start, end):
        print("Get new data for {} ({})...".format(pair, tick_size))
        ohlc_data = self.ohlc_get_data(pair, tick_size, start, end)
        formatted_data = self.ohlc_format_data(ohlc_data)
        self.ohlc_save_data(formatted_data, pair, tick_size)
        

    def update_symbols(self):
        """Generates a list of all symbols on Binance"""
        info = self.client.get_exchange_info()
        filepath_symbols = self.symbol_history_file
        symbols_dic = info['symbols']
        all_symbols = []
        for dic in symbols_dic:         #extracting symbols data for Binance API
            if dic['baseAsset'] not in all_symbols:
                all_symbols.append(dic['baseAsset'])
        if not os.path.exists(filepath_symbols):   #create folder to save data if not already existing
            os.makedirs(filepath_symbols)
        with open('{}/all_symbols.csv'.format(filepath_symbols), 'w') as f_obj:      #save data to symbols file
            wr = csv.writer(f_obj, delimiter='\n')
            wr.writerow(all_symbols)
        print("Symbols have been updated.")
        self.all_symbols = all_symbols
        return all_symbols
    
    
    def get_all_symbols(self):
        pass
        
    
    def get_all_pairs(self):
        """Generates a list of all possible trading pairs"""
        info = self.client.get_exchange_info()
        pairs_dic = info['symbols']
        all_pairs = []
        for dic in pairs_dic:
            if dic['symbol'] not in all_pairs:
                all_pairs.append(dic['symbol'])
        self.all_pairs = all_pairs
        return all_pairs
     
        
    def files_update_pairs_folders(self):
        """After appending new data to file, timestamp is recorded and used as start time for next data download so that data isn't added twice."""
        filepath = self.symbol_history_file
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


    def latest_timestamp_ohlc(self, pair=None, tick_size=None):
        """Return the lastest timestamp for the data already on file for a given pair and tick size"""
        filepath = self.symbol_history_file
        if pair is None:
            pair = self.pair
            print("pair not provided so last pair ({}) was used.".format(self.pair))
        if tick_size is None:
            tick_size = self.tick_size
            print("tick_size not provided so last tick size ({}) was used.".format(self.tick_size))  
        try:
            with open('{}/{}/{}_{}.csv'.format(filepath,pair, pair, tick_size),'rb') as f:    #open csv and read last line
                lines = f.readlines()
                last_line = np.genfromtxt(lines[-1:],delimiter=',')
                return last_line[1]
        except FileNotFoundError:
            print("No data on file for {}_{}.".format(pair, tick_size))
            