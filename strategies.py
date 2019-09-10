
# https://towardsdatascience.com/trading-strategy-technical-analysis-with-python-ta-lib-3ce9d6ce5614

from operations import Operations

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import dateparser as dp



class Strategy(Operations):
    """Strategies available to Trader. Strategies should output an array of signals that can be read by the backtesting function.
    
    Each strategy should apply various logics to a standardised data input, generate buy/ sell signals accordingly and then output
    a standardised array of signals of equal length to the input data. Each data point (tick) will either be have the strategy of
    buy or sell, taking the form of 1 for buy and -1 for sell. Buying/ selling occurs at points of fluctuation between 1 and -1.

    """
    def __init__(self):
        super(Strategy, self).__init__()
        plt.style.use('seaborn-deep')


    def rolling_avg2(self, pair, tick_size):
        """
        WIP
        Standardised method for rolling average
        """
        trader.operator_update(pair, tick_size) # add new data to file
        columns = self.return_strategy_headers('rolling_avg2') #
        data = self.load_data(pair, tick_size, columns) # load data as dataframe    

    
    def rolling_avg(self,pair, tick_size, start, end):
        """Apply rolling average strategy.
        """
        filepath = self.symbol_history_file
        #create dataframe
        try:
            data = pd.read_csv(f'{filepath}/{pair}/{pair}_{tick_size}.csv',index_col=None)
            drfreq = self.generate_index(tick_size)
            periods = len(pd.period_range(start=dp.parse(start), end=dp.parse(end), freq=drfreq))
            print(periods)
            data.set_index(pd.date_range(start=start,periods=periods,freq=drfreq),inplace=True)
        except FileNotFoundError:
            print(f'No data on file for {pair}_{tick_size}.')
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

    def find_downtrend_slope(self):
        """
        - Take the lows of the last X ticks, produce a linear of lowest lows of last n points, to show where they expect the next local low
        - Repeat for X last lows, average results to make a trajectory?
        
        """
        
    def calc_ma_target(self):
        """
        moving averages are used as targets, calculate moving averages of various time spans.
        """


#    def strategy_returns(self,pair_df, start,end='now'):
            #pseudocode
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

