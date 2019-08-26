from get_data import GetData


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