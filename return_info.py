#Documentation
#Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
#Python-Binance master document              https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
#Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
#More useful information                     https://python-binance.readthedocs.io/en/latest/binance.html

from account import Account

class ReturnInfo(Account):
    """
     - Functions do not require data
     - Any constants, including lists and dictionaries, are contained here for calling as and when they are needed
    """
    
    def __init__(self):
        super(ReturnInfo, self).__init__()


    def return_master_symbols(self):
        """Update db and then create a list of all the symbols in the master symbol table. """
        self.update_master_symbols_table()
        self.c.execute("""SELECT Master_pair_list FROM master_symbols""")
        all_symbols = self.c.fetchall()
        all_symbols = [_[0] for _ in all_symbols]   #turns list of tuples into a list
        return all_symbols
    
    def return_pairs_ticks_combinations(self):
        """Create each combination of pair/ tick_size"""
        fts = self.return_formatted_tick_sizes()
        all_pairs = self.return_master_symbols()
        pairs_ticks = [pair+"_"+fts for pair, fts in product(all_pairs, fts)]
        return pairs_ticks        


    def return_tick_sizes(self):
        """List all tick sizes that Binance accepts"""
        tick_sizes = ['1m','1h','1d','1w','1M']
        #tick_sizes = ['m','h','d','w']
        return tick_sizes
    
    def return_exchange_pairs(self):
        """Generates a list of all possible trading pairs"""
        info = self.client.get_exchange_info()
        pairs_dic = info['symbols']
        exchange_pairs = []
        for dic in pairs_dic:
            if dic['symbol'] not in exchange_pairs and dic['symbol'] != '123456': #123456 is a Binance test symbol
                exchange_pairs.append(dic['symbol'])
        return exchange_pairs

    
    def return_ticks_in_ms(self):
        """return ms per tick"""
        ms_per_tick ={
                'm': 60*1000,
                'h': 60*60*1000,
                'd': 24*60*60*1000,
                'w': 7*24*60*60*1000
                }
        return ms_per_tick
    

    def return_all_tables(self):
        """ """
        pass
    
    
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
    

    def return_tick_categories(self):
        """integer to tick conversion"""
        tick_categories = {0:'m', 1:'h', 2:'d', 3:'w'}
        return tick_categories
    
    
    def return_ohlc_headers(self):
        """Column headers for the data arriving from Binance"""
        column_headers = [
            'Unix_Open',
            'Open',
            'High',
            'Low',
            'Close',
            'Volume',
            'Unix_Close',
            'Quote_asset_volume',
            'Number_of_trades',
            'Taker_buy_base_asset_volume',
            'Taker_buy_quote_asset_volume',
            'Ignore']
        return column_headers
    
    
    def return_db_headers(self):
        """Return the ohlc headers for the pair - tick size tables"""
        column_headers = [
            'UTC_Open',
            'Unix_Open',
            'Open',
            'High',
            'Low',
            'Close', 
            'Volume',
            'UTC_Close',
            'Unix_Close',
            'Quote_Asset_Volume',
            'Number_of_Trades',
            'Taker_Buy_Base_Asset_Volume',
            'Taker_Buy_Quote_Asset_Volume'
            ]        
        return column_headers
    
    
    def return_strategy_dict(self):
        """For a given strategy name, return the required headers"""
        db_headers = self.return_db_headers()
        strat_dict  = {
                'rolling_avg2':db_headers[1,2,3]                
                }
        return strat_dict
        
        
        
        
        
        
        