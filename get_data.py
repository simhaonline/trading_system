from ref_info import RefInfo

class GetData(RefInfo):
    """
    - Functions that retrieve market data from the Binance exchange.
    """
    def __init__(self):
        super(GetData, self).__init__()
        
    
    def ohlc_get_data(self, pair, tick_size, start, end, limit=1000):
        """Kline/candlestick bars for a symbol. Klines (ohlc candlesticks) are uniquely identified by their open time."""
        ohlc_data = self.client.get_historical_klines(pair, tick_size, start, end, limit)
        return ohlc_data
    
    
    def get_earliest_valid_timestamp(self, pair, tick_size):
        """get earliest valid timestamp for pair from Binance."""
        kline = self.client.get_klines(
            symbol=pair,
            interval=tick_size,
            limit=1,
            startTime=0
            #endTime=None
        )
        return kline[0][0]   
    
    
    def get_all_pairs(self):
        """Generates a list of all possible trading pairs"""
        info = self.client.get_exchange_info()
        pairs_dic = info['symbols']
        all_pairs = []
        for dic in pairs_dic:
            if dic['symbol'] not in all_pairs and dic['symbol'] != '123456': #123456 is a Binance test symbol
                all_pairs.append(dic['symbol'])
        return all_pairs
