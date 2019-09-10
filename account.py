from binance.client import Client


class Account():
    """
    - Initialise the trading system by logging into Binance.
    - Provide functionality for Binance account functions, such as getting information relating to an account or to the Binnance exchange.
    """   
    
    def __init__(self):
        super(Account, self).__init__()
        self.symbol_history_file = 'D:/Python/python_work/trading_system/symbol_history'
        self.account_login()
        

    def account_login(self):
        """Creates Binance client for accessing exchange, account and market data."""
        file = 'c:/python/python_work/credentials.txt'
        with open(file) as f_obj:
            lines = [line.rstrip('\n') for line in f_obj]
            api_key = lines[0]
            api_secret = lines[1]
            self.client = Client(api_key, api_secret)


    def account_trades(self, symbol):
        """Returns account's trade history for a given symbol"""
        trades = self.client.get_my_trades(symbol=symbol)
        return trades
    
    
    def exchange_server_time(self):
        """Retrieve the server time of the Binance exchange"""
        server_time = self.client.get_server_time()
        return server_time
    

