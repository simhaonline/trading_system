from get_data import GetData
import pandas as pd


class FormatData(GetData):
    """
    - Functions that reformat the data from Binance into more convenient formats for various functions.
    """
    
    def __init__(self):
        super(FormatData, self).__init__()

    def return_formatted_tick_sizes(self):
        """Standard list of formatted tick_sizes"""
        tick_sizes = self.return_tick_sizes()
        formatted_tick_sizes = []
        for tick_size in tick_sizes:
            if tick_size[1:] == 'm':
                formatted_tick_size = tick_size[:1] + 'min'
            else:
                formatted_tick_size = tick_size
            formatted_tick_sizes.append(formatted_tick_size)    
        return formatted_tick_sizes
    
        
    def format_tick_size(self, tick_size):
        """Take a tick size and return it formatted."""
        if tick_size[1:] == 'm':
            formatted_tick_size = tick_size[:1] + 'min'
#        elif tick_size[1:] == 'M':
#            formatted_tick_size = tick_size[:1] + 'MON'            
        else:
            formatted_tick_size = tick_size
        return formatted_tick_size
    
    
    def ohlc_format_data(self, ohlc_data):
        """With the ohlc data from Binance, format into DataFrames that are useful"""
        column_headers = self.ohlc_return_column_headers()
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