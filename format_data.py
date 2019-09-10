from gets_checks import GetsChecks
import pandas as pd


class FormatData(GetsChecks):
    """
    - Functions always require data as a parameter
    - Data is passed to these functions and returned in an adjusted format.
    """
    
    def __init__(self):
        super(FormatData, self).__init__()

####### Database   
        
    def format_remove_unusual_timestamps(self, data, pair, tick_size):
        """
        - Get list of expected timestamps, compare timestamps downloaded to this list.
        - Where a downloaded timestamp is unexpected, delete that row from the DataFrame
        """
        allowed_timestamps = self.timestamps_on_binance(pair, tick_size)
        adj_data = data[data['Unix_Open'].isin(allowed_timestamps)]
        return adj_data


####### OHLC 
        
    def format_ohlc_data(self, ohlc_data):
        """With the ohlc data from Binance, format into DataFrames."""
        column_headers = self.return_ohlc_headers()
        df = pd.DataFrame(ohlc_data, columns=column_headers)
        float_columns = column_headers[1:6] + column_headers[7:11]
        open_datetime = pd.to_datetime(df['Unix_Open'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(0, "UTC_Open", open_datetime)
        close_datetime = pd.to_datetime(df['Unix_Close'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
        df.insert(7, "UTC_Close", close_datetime)
        df.drop('Ignore', axis='columns', inplace=True)
        for fl_col in float_columns:
            df[f'{fl_col}'] = pd.to_numeric(df[f'{fl_col}'], downcast='float', errors='coerce')
        return df
        
####### Strings, Lists etc.       
        
    def format_tick_size(self, tick_size):
        """Take a tick size and return it formatted."""
        if tick_size[1:] == 'm':
            formatted_tick_size = tick_size[:1] + 'min'
#        elif tick_size[1:] == 'M':
#            formatted_tick_size = tick_size[:1] + 'MON'            
        else:
            formatted_tick_size = tick_size
        return formatted_tick_size
    
    

