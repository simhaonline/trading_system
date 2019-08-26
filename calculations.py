from get_data import GetData
from format_data import FormatData

import numpy as np

class Calculations(FormatData):
    """
    - Functions that perform calculations on input data, often returning the result as an output
    """
    
    def __init__(self):
        super(Calculations, self).__init__()

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
