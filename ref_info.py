from account import Account

class RefInfo(Account):
    """
     - Any constants, including lists and dictionaries, are contained here for calling as and when they are needed
    
    
    Documentation
    Kline interval date parser "1 day ago UTC"  https://dateparser.readthedocs.io/en/latest/
    Python-Binance master document              https://buildmedia.readthedocs.org/media/pdf/python-binance/latest/python-binance.pdf
    Python-Binance quick reference document     https://python-binance.readthedocs.io/en/latest/market_data.html#id6
    More useful information                     https://python-binance.readthedocs.io/en/latest/binance.html
    """
    
    def __init__(self):
        super(RefInfo, self).__init__()


    def return_tick_sizes(self):
        """List all tick sizes that Binance accepts"""
        tick_sizes = ['1m','1h','1d','1w','1M']
        return tick_sizes
        
    def ohlc_return_column_headers(self):
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
        
        
        
        
        
        
        