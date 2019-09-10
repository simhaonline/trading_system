from format_data import FormatData

import numpy as np
import time

class Calculations(FormatData):
    """
    - Functions always require data as a parameter
    - Functions that perform calculations on provided data, returning new data (not reformatted)
    """
    
    def __init__(self):
        super(Calculations, self).__init__()
        
        
####### Database


        
    def return_strategy_headers(self, strategy_name):
        strat_dict = self.return_strategy_dict()
        for strategy, headers in strat_dict.items():
            if strategy == strategy_name:
                return headers
        
    def timestamps_on_binance(self, pair, tick_size):
        """return the amount of timestamps theoretically available on Binance for a pair/ tick size"""
        first_ts = self.get_earliest_valid_timestamp(pair, tick_size) # gather first trading timestamp for symbol, the timestamp now, the milliseconds between each timestamp
        last_ts  = int(time.time())*1000 # times 1000 as binance uses milliseconds
        tick_in_ms = self.return_tick_in_ms(tick_size)
        db_ticks = self.calc_db_ticks(first_ts, last_ts, tick_in_ms) # calculate ticks number of ticks from the first timestamp traded up to now
        timestamps_on_binance = np.array([(first_ts + (tick_in_ms*i)) for i in range(0,db_ticks)], dtype='int64') # create an array of all the timestamps that data is expected for
        return timestamps_on_binance    
            
            
    def return_tick_in_ms(self, tick_size):
        """Return the seconds per tick
        - May update in the future with removal of month sized ticks
        """
#            seconds_per_unit = {
#        "m": 60,
#        "h": 60 * 60,
#        "d": 24 * 60 * 60,
#        "w": 7 * 24 * 60 * 60
#    }
        conversion = {'m': 60000, 'h': 3600000, 'd': 86400000, 'w': 604800000, 'M': 2629746000}
        for tick, conv in conversion.items():
            if tick_size[1:] == tick:
                tick_in_ms = conv
        return tick_in_ms    
    
    
    def calc_chunks(self, start, end, tick_in_ms):
        """Count the intervals between first timestamp and now, for a given tick size"""
        chunks = int(np.ceil((end - start)/tick_in_ms))
        return chunks
    
    
    def calc_db_ticks(self, start, end, tick_in_ms):
        """Calculate how many ticks (timestamps) a database will be created with."""
        db_ticks = int(np.floor((end - start)/tick_in_ms))
        return db_ticks
        
    
    def return_table_name(self, pair, tick_size):
        """Take a pair and tick size and return the table name in the DB"""
        formatted_tick_size = self.format_tick_size(tick_size)
        table_name = pair+'_'+formatted_tick_size
        return table_name
    
            
    def split_combo(self, combination):
        """Split combo to pair and tick size"""
        pair, tick_size = combination.split('_', 2)
        return pair, tick_size
         
        
    def reverse_tick_size_formatting(self, formatted_tick_size):
        """Take a formatted tick size and return it unformatted"""
        if formatted_tick_size[1:] == 'min':
            tick_size = formatted_tick_size[:1] + 'm'
        else:
            tick_size = formatted_tick_size
        return tick_size    
