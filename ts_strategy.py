# Documentation
# Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
# Python-Binance master document  https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
# Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
# More useful information (quick reference)     https://python-binance.readthedocs.io/en/latest/binance.html

from ts_account import Account
from ts_trader import Trader
from binance.client import Client
import pandas as pd
import os
import numpy as np
import csv
import matplotlib.pyplot as plt
import dateparser as dp


class Strategy(Trader):
    """Strategies available to Trader. Strategies should output an array of signals that can be read by the backtesting function."""
    def __init__(self, pair, tick_size, start, end):
        super().__init__(pair, tick_size, start, end)
        self.pair = pair
        self.tick_size = tick_size
        self.start = start
        self.end = end


    def generate_index(self, tick_size):
        binance_intervals_to_date_range_freq = {'m':'T','h':'H','d':'D','w':'W','M':'M'}
        for key, value in binance_intervals_to_date_range_freq.items():
            if tick_size[-1] == key:
                drfreq = value
        self.drfreq = drfreq
        return drfreq
        
    
    def format_start(self, start):
        """format the start variable that is passed to binance into datetime"""
        # may delete
        pass
    
    
    def format_end(self, end):
        """format the end variable that is passed to binance into datetime"""
        #may delete
        pass

    
    def rolling_avg(self,pair=None, tick_size=None, start=None, end=None):
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
        try:
            data = pd.read_csv("{}/{}/{}_{}.csv".format(filepath, pair, pair, tick_size),index_col=None)
            drfreq = self.generate_index(tick_size)
            periods = len(pd.period_range(start=dp.parse(start), end=dp.parse(end), freq=drfreq))
            data.set_index(pd.date_range(start=start,periods=periods,freq=drfreq),inplace=True)              
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
            ax = data[['Close','SMA_S','SMA_L','Signal']].plot(figsize=(15,6),secondary_y='Signal')
            ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
            return data
    
    
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
            