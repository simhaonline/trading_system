from return_info import ReturnInfo

class GetsChecks(ReturnInfo):
    """
    - Functions always require data as a parameter
    - Functions that retrieve market data `from the Binance exchange.
    """
    
    def __init__(self):
        super(GetsChecks, self).__init__()
        
        
####### Database
        
    def get_table_data(self, pair, tick_size, columns):
        """load the data from the SQL database and return as a dataframe"""
        table_name = self.return_table_name(pair, tick_size)
        self.c.execute(f"""SELECT * FROM {table_name}""")   #will want to specify which data in future (eg. skip rows if missing data)
        results = self.c.fetchall()
        data = pd.DataFrame(results, columns=columns)
        return data
        

    
    def check_populated_table_records(self, combo):
         """Check if pair-tick size combination table has been already populated"""
         fpath = 'D:/Python/python_work/trading_system/records'
         fname = 'populated_tables.csv'
         self.check_folder_exists(fpath)
         self.check_file_exists(fpath, fname)
         if os.path.getsize(f"{fpath}/{fname}") > 0:
             #return True if record exists, False if not
             in_file = self.check_record_exists(fpath, fname, combo)
             return in_file
         else:
            print("empty file")
            return False      


    def check_folder_exists(self,fpath):
        """ create folder to save data if not already existing"""
        if not os.path.exists(fpath):
            os.makedirs(fpath)    


    def check_file_exists(self, fpath, fname):
        """Check if file exists"""
        if not os.path.isfile(f"{fpath}/{fname}"):
             with open(f"{fpath}/{fname}", 'w') as f_obj:
                 pass
             

    def check_record_exists(self, fpath, fname, combo):
        """check if record within file exists"""
        with open(f"{fpath}/{fname}", 'r') as f_obj:
             reader = csv.reader(f_obj, delimiter='\n')
             for row in reader:
                 for field in row:
                     #if combo exists in table, return True
                     if field == combo:
                         return True
             return False        
                    
####### Binance        
    
    def get_ohlc_data(self, pair, tick_size, start, end, limit=1000):
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
    
    



           