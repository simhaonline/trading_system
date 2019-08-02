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



class Account():
    """Account functions"""   
    
    def __init__(self, login_file = 'c:/python/python_work/credentials.txt'):
        self.login_file = login_file
        self.symbol_history_file = 'D:/Python/python_work/trading_system/symbol_history'
        self.login()
        plt.style.use('seaborn-deep')
        

    def login(self):
        """Creates Binance client"""
        file = self.login_file
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

    def __init__(self, login_file = 'c:/python/python_work/credentials.txt', **kwargs):
        super().__init__(login_file)
        for key, value in kwargs.items():   #Pass in any information that may be useful
            setattr(self, key, value)
        print("Starting trader...")
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
        
    
    def ohlc_data_download(self, pair, tick_size, start, end, limit=1000):
        """Kline/candlestick bars for a symbol. Klines are uniquely identified by their open time."""
        filepath = self.symbol_history_file
        klines = self.client.get_historical_klines(pair, tick_size, start, end, limit)
        # formatting table
        column_headers = Trader.ohlc_return_column_headers(self)

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
        print("Data for {}_{}".format(pair, tick_size) + " has been updated.")  
        

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
        print("Symbols successfully updated.")
        self.all_symbols = all_symbols
        return all_symbols
    
    
    def get_all_symbols(self):
        pass
        
    
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
        #If pair, tick_size are not provided when calling function, set default values to current attribute values.
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
                

class Strategy(Trader):
    """Strategies available to Trader. Strategies should output an array of signals that can be read by the backtesting function."""

    def __init__(self, login_file = 'c:/python/python_work/credentials.txt', **kwargs):
        super().__init__(login_file)
        for key, value in kwargs.items():   #Pass in any information that may be useful
            setattr(self, key, value)

    
    def roll_avg(self,pair=None, tick_size=None, start=None, end=None):
        """Apply rolling average strategy.
        -The function applies a rolling average strategy to a historic data set to generate theoretical buy/sell signals.
        -The buy/sell signals are returned at the end for use in a function that calculates the returns.
        -Creating a sequence of buy/sell orders will be a standardised practice for strategies.  
        """
        filepath = self.symbol_history_file
        if pair is None:        #if variables aren't provided when calling function, use the instance variables
            pair = self.pair
            print("pair not provided so last pair ({}) was used.".format(self.pair))
        if tick_size is None:
            tick_size = self.tick_size
            print("tick_size not provided so last tick size ({}) was used.".format(self.tick_size))  
        if start is None:
            start = self.start
            print("start not provided so last start time ({}) was used.".format(self.start))
        if end is None:
            end = self.end
            print("end not provided so last end time ({}) was used.".format(self.end))  
        #create dataframe
        column_headers = Trader.ohlc_return_column_headers(self)
        try:
            data = pd.read_csv("{}/{}/{}_{}.csv".format(filepath, pair, pair, tick_size))
        except FileNotFoundError:
            print("No data on file for {}_{}.".format(pair, tick_size))
        else:
            #SMA Long must have more ticks than SMA Short
            SMA_L_hm_ticks_to_average = 5
            SMA_S_hm_ticks_to_average = 3
            data['SMA_L'] = data['Close'].rolling(window=SMA_L_hm_ticks_to_average).mean() #SMA1 is longer moving average
            data['SMA_S'] = data['Close'].rolling(window=SMA_S_hm_ticks_to_average).mean() #SMA2 is shorter moving average
            data.dropna(inplace=True)
            data['Signal'] = np.where(data['SMA_S']>data['SMA_L'],1,-1)    # 1 for BUY(long), -1 for SELL(short)
            #return data as plot
            ax = data[['Close','SMA_S','SMA_L','Signal']].plot(figsize=(10,6),secondary_y='Signal')
            ax.get_legend().set_bbox_to_anchor((0.25,0.85))
        
    
#    def strategy_returns(self,pair_df, start,end='now'):
#        """Takes a dataframe of buy/sell signals and calculates the return after holding for n days"""
#        data = filepath
#        frame = pd.DataFrame(data)
#        return_days = 10
#        pair_df['event'] = 'event'
#        start_pos = start #start timestamp
#        end = end #end timestamp 
#        return_period = frame.loc[[end_pos - start_pos], 'close price'] #grabs the dates of interest along with the price
#        for timestamp in range_of_timestamps:
#            # calculate return n days after timestamp
#            return_days_return = (timestamp['close price'] - (timestamp + return_days)['close price'])/(timestamp + return_days)['close price']
            

# Provide details for downloading data
pair = 'NEOBTC'
tick_size = "1w"
start = "1 Jan, 2018"
end = "now"


# Code to run
trader = Strategy(pair=pair, tick_size=tick_size, start=start, end=end)
trader.ohlc_data_download(pair, tick_size, start, end)
#trader.get_all_pairs()
#trader.update_symbols()
#print(trader.latest_timestamp_ohlc(pair = pair, tick_size=tick_size))
#print(trader.pair)
#print(trader.tick_size)
#print(trader.start)
#print(trader.end)
#print(trader.all_symbols)
data = trader.roll_avg()
