from calculations import Calculations

import sqlite3

import numpy as np
import sys
import time



class Operations(Calculations):
    """
    Operations combining fetching data, reformatting, calculations and function specific code to perform tasks (operations).
    """
            
    def __init__(self):
        super(Operations, self).__init__()
        self.filepath = 'D:/Python/python_work/trading_system/trading_system.db'
        conn = sqlite3.connect(self.filepath)
        self.conn = conn
        self.c = conn.cursor()
        
######## Strategy functions
        
    def test_strategy(self):
        """
        Along with buy/sell signals, could also produce a confidence estimate for how strong the pattern is.
        - can assess the strength of trend ratings too based on the actual results.
        - having some sort of % accuracy would be useful for choices between two strategies.
        """
        pass

######## Database Functions
        
    def apply_to_all(self, function):
        """Take a function and apply it to every table"""
        pass
    

    def new_create_table(self, pair, tick_size):
        """Create a new table with a pair and tick size"""
        table_name = self.return_table_name(pair, tick_size)
        self.c.execute(f"""CREATE TABLE IF NOT EXISTS {table_name} (
            Unix_Open INTEGER NOT NULL PRIMARY KEY,
            UTC_Open TEXT NOT NULL,
            Open REAL NOT NULL,
            High REAL NOT NULL,
            Low REAL NOT NULL,
            Close REAL NOT NULL,
            Volume REAL NOT NULL,
            Unix_Close INTEGER NOT NULL,
            UTC_Close TEXT NOT NULL,
            Quote_Asset_Volume REAL NOT NULL,
            Number_of_Trades INTEGER NOT NULL,
            Taker_Buy_Base_Asset_Volume REAL NOT NULL,
            Taker_Buy_Quote_Asset_Volume REAL NOT NULL
            )""")
        print("Tables have been updated for all possible pair-tick size combinations.")
        
    
    def check_db_gaps(self, pair, tick_size):
        """Check if any gaps exist in the table"""
        binance_records = self.timestamps_on_binance(pair, tick_size)
        table_name = self.return_table_name(pair, tick_size)
        self.c.execute(f"""SELECT Unix_Open FROM {table_name}""")
        table_records = self.c.fetchall() 
        actual_difference = np.setdiff1d(binance_records, table_records) 
        """All elements in actual differences need to be downloaded, but rather than request them individually and as many records will occur in a row, start/ end points for missing periods are identified"""
        records_to_dl = np.isin(binance_records,actual_difference)
        new = np.where(records_to_dl == False, 0, binance_records) 
        """Compare each element of an array against the next element by creating a copy of the array and deleting the first element from the new and the last from the old"""
        diff_between_elements = np.diff(new)
        tick_in_ms = self.return_tick_in_ms(tick_size)
        arr = np.where(diff_between_elements == 0, 2, diff_between_elements)
        arr_start = np.where(arr>tick_in_ms, -1, arr)
        arr_start_end = np.where(arr_start<-1, 1, arr_start) 
        arr_dl = np.where(arr_start_end>2, 0, arr_start_end) 
        """Add back in what the first element would have been if it wasn't lost when differencing"""
        first_lost_element = {-1:2, 0:-1, 1:-1, 2:2}
        for adj_e, insert_e in first_lost_element.items():
            if arr_dl[0] == adj_e:
                arr_dl = np.insert(arr_dl, 0, insert_e)
        """Adjust the last element if the array ends during specifying records to be download. force last element to be end. """       
        starts = arr_dl[arr_dl == -1]
        ends = arr_dl[arr_dl == 1]
        if arr_dl[-1] == 0:
                arr_dl = np.delete(arr_dl,-1) 
                arr_dl = np.insert(arr_dl, -1, 1) 
        """Return starts, ends and count how many changes will be made."""
        starts = binance_records[arr_dl == -1]
        ends = binance_records[arr_dl == 1]
        if len(starts) != len(ends):
            print("Error: starts does not equal ends!")
            sys.exit()
        count = 0
        for start, end in zip(list(starts), list(ends)):
            ticks_in_period = self.calc_db_ticks(start, end, tick_in_ms)
            count += ticks_in_period
        print(f"Up to {count} records will be downloaded.")    
        return starts, ends 
         

    def operator_update(self, pair, tick_size):
        """Starting at the most recent timestamp, the operator will populate a table."""
        table_name = self.return_table_name(pair, tick_size)
        check_if_table_populated = self.check_populated_table_records(table_name)
        if check_if_table_populated == False:
            trading_start = self.get_latest_timestamp(pair, tick_size)
            print(f"latest timestamp: {trading_start}")
            start = trading_start
            end  = int(time.time())*1000
            #calculate chunks to download
            tick_in_ms = self.return_tick_in_ms(tick_size)
            ticks_to_dl = self.calc_chunks(start, end, tick_in_ms)
            batch_size = 1000
            if ticks_to_dl>batch_size:
                batches_remaining = int(np.ceil(ticks_to_dl/batch_size))
                batches_complete = 0
                ticks_remaining = ticks_to_dl
                while ticks_remaining >0:
                    ticks_in_batch = batch_size if ticks_remaining > batch_size else ticks_remaining
                    end = start + (tick_in_ms*ticks_in_batch)
                    self.operator_insert_into_db(pair, tick_size, start, end)
                    start = end
                    batches_complete += 1
                    batches_remaining += -1
                    print(f"{batches_complete} chunks complete for {table_name} ({batches_remaining} remaining).")
                    ticks_remaining += -ticks_in_batch
                self.record_new_populated_table(table_name)
                print(f"All batches complete for {table_name}.")
            #single batch    
            elif ticks_to_dl<batch_size:
                self.operator_insert_into_db(pair, tick_size, start, end)
                self.record_new_populated_table(table_name)
                print(f"{table_name} was populated in a single batch.")
            else:
                print(f"No ticks to download for {table_name}.")
        elif check_if_table_populated == True:
            print(f"{table_name} table already populated.")
        else:
            print("error at operator")    
            
    
    def operator(self, pair, tick_size):
        """Starting at the earliest available timestamp on Binance, the operator will populate a table."""
        table_name = self.return_table_name(pair, tick_size)
        check_if_table_populated = self.check_populated_table_records(table_name)
        if check_if_table_populated == False:
            trading_start = self.get_earliest_valid_timestamp(pair, tick_size)
            start = trading_start
            end  = int(time.time())*1000
            #calculate chunks to download
            tick_in_ms = self.return_tick_in_ms(tick_size)
            ticks_to_dl = self.calc_chunks(start, end, tick_in_ms)
            batch_size = 1000
            if ticks_to_dl>batch_size:
                batches_remaining = int(np.ceil(ticks_to_dl/batch_size))
                batches_complete = 0
                ticks_remaining = ticks_to_dl
                while ticks_remaining >0:
                    ticks_in_batch = batch_size if ticks_remaining > batch_size else ticks_remaining
                    end = start + (tick_in_ms*ticks_in_batch)
                    self.operator_insert_into_db(pair, tick_size, start, end)
                    start = end
                    batches_complete += 1
                    batches_remaining += -1
                    print(f"{batches_complete} chunks complete for {table_name} ({batches_remaining} remaining).")
                    ticks_remaining += -ticks_in_batch
                self.record_new_populated_table(table_name)
                print(f"All batches complete for {table_name}.")
            #single batch    
            elif ticks_to_dl<batch_size:
                self.operator_insert_into_db(pair, tick_size, start, end)
                self.record_new_populated_table(table_name)
                print(f"{table_name} was populated in a single batch.")
            else:
                print(f"No ticks to download for {table_name}.")
        elif check_if_table_populated == True:
            print(f"{table_name} table already populated.")
        else:
            print("error at operator")


    def operator_insert_into_db(self,pair, tick_size, start, end):
        """Inserts the operator data into the appropriate table and in the appropriate fashion."""
        table_name = self.return_table_name(pair, tick_size)
        in_file = self.check_populated_table_records(table_name)
        if in_file == False:                
            pair, formatted_tick_size = self.split_combo(table_name)
            tick_size = self.reverse_tick_size_formatting(formatted_tick_size)
            data = self.ohlc(pair, tick_size, start, end)
            """Remove unusual timestamps from data."""
            data = self.format_remove_unusual_timestamps(data, pair, tick_size)
            self.insert_into_db(pair, tick_size, data)
        elif in_file == True:
           print("already done.")
        else:
            print("broke at operator_insert_into_db")
        
         
    def insert_into_db(self, pair, tick_size, data):
        """ Take ohlc data (DataFrame) and insert it into a table.
            Pass in only the data which is to be inserted into DB."""
        formatted_tick_size = self.format_tick_size(tick_size)
        table_name = self.return_table_name(pair, formatted_tick_size)
        rows = len(data.iloc[:,1])
        if rows > 1:
            columns = len(data.iloc[1,:])
            new = np.array(data).reshape(rows, columns)
            replaced = 0
            inserted = 0
            for row in new:
                l = []
                for i in range(0,columns):
                    l.append(row[i])
                tup = tuple(l)
                """If timestamp already exists in table, update row.
                   If timestamp does not exist in table, add row.   """
                if self.record_exists_in_table(row[1], table_name):
                    replaced += 1
                    self.c.execute(f"""UPDATE {table_name}
                    SET
                    Open=?,
                    High=?,
                    Low=?,
                    Close=?,
                    Volume=?,
                    UTC_Close=?,
                    Unix_Close=?,
                    Quote_Asset_Volume=?,
                    Number_of_Trades=?,
                    Taker_Buy_Base_Asset_Volume=?,
                    Taker_Buy_Quote_Asset_Volume=? 
                    WHERE Unix_Open={row[1]} """,(row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10],row[11],row[12]))                                
                else:
                    inserted += 1
                    self.c.execute(f"""INSERT INTO {table_name}(
                    UTC_Open,
                    Unix_Open,
                    Open,
                    High,
                    Low,
                    Close, 
                    Volume,
                    UTC_Close,
                    Unix_Close,
                    Quote_Asset_Volume,
                    Number_of_Trades,
                    Taker_Buy_Base_Asset_Volume,
                    Taker_Buy_Quote_Asset_Volume) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (tup))
            print(f"{table_name} table was extended with {inserted} new row(s). {str(replaced)} row was updated.")
            self.conn.commit()
        else:
            print(f"No new data for {table_name}. Tick size is {tick_size}, refresh accordingly.") 
            

    
    def get_latest_timestamp(self, pair, tick_size):
        table_name = self.return_table_name(pair, tick_size)
        self.c.execute(f"""SELECT MAX(Unix_Open) FROM {table_name}""")
        result = self.c.fetchone()[0]      
        return result           
    
    
    def record_exists_in_table(self, timestamp, table_name):
        """Lookup timestamp in table, if exists, return True"""
        self.c.execute(f"""SELECT Unix_Open FROM {table_name} WHERE Unix_Open = {timestamp}""")
        result = self.c.fetchone()
        if result:
            result = result[0]
            return True
        else:
            return False
    
    def table_delete_unusual_timestamps(self, pair, tick_size):
        """
        Delete timestamps from table that are unexpected.
        """
        expected_timestamps = self.timestamps_on_binance(pair, tick_size)
        table_name = self.return_table_name(pair, tick_size)
        """Fetch timestamps from table."""
        self.c.execute(f"""SELECT Unix_Open FROM {table_name}""")
        table_timestamps = self.c.fetchall()
        """Convert SQLite output to array"""
        table_timestamps = np.array([i[0] for i in table_timestamps])
        """Find unexpected timestamps by comparing timestamps in table to those expected from Binance."""
        unexpected_timestamps = np.setdiff1d(table_timestamps, expected_timestamps)
        print(f"Unexpected timestamps: {len(unexpected_timestamps)}")
        """ - Perform deleting action on table.
            - Can only process 999 timestamps at one time, so break up and iterate over unexpected timestamps list."""
        timestamps_for_deletion = unexpected_timestamps.tolist()
        print("Deleting...")
        try:
            con = sqlite3.connect('D:/Python/python_work/trading_system/trading_system.db')
            with con:
                while len(timestamps_for_deletion)>999:
                    print(f"Remaining: {len(timestamps_for_deletion)}")
                    timestamps = timestamps_for_deletion[-999:]
                    con.execute(f"""DELETE FROM {table_name} WHERE Unix_Open IN ({','.join(['?']*len(timestamps))})""", timestamps)
                    del timestamps_for_deletion[-999:]
                    con.commit()
                print(f"Remaining: {len(timestamps_for_deletion)}")
                con.execute(f"""DELETE FROM {table_name} WHERE Unix_Open IN ({','.join(['?']*len(timestamps_for_deletion))})""", timestamps_for_deletion)
                con.commit()
        except Exception as e:
            print(f"Error: {e}")
        print("Done.")
        con.close() 
                
                
    def load_table_data(self, pair, tick_size):
        """load the data from the SQL database and return as a dataframe"""
        table_name = self.return_table_name(pair, tick_size)
        self.c.execute(f"""SELECT * FROM {table_name}""")   #will want to specify which data in future (eg. skip rows if missing data)
        results = self.c.fetchall()
        """Return a list of tuples, where each tuple is a row."""
        return results
        
####### OHLC    
            
    def ohlc(self, pair, tick_size, start, end):
        """Get ohlc data and return as a DataFrame."""
        print(f'Get new data for {pair} ({tick_size})...')
        ohlc_data = self.get_ohlc_data(pair, tick_size, start, end)
        ohlc_formatted = self.format_ohlc_data(ohlc_data)
        return ohlc_formatted   
            
            
    def update_table(self, pair, tick_size):
        """Download the latest Binance symbols. If any are new then add them to the master symbols table. """
        start = self.get_latest_timestamp(pair, tick_size)
        if start == None:
            print("Cannot update as no data exists. Exiting...")
            sys.exit()     
        end = 'now'
        data = self.ohlc(pair, tick_size, start, end)
        self.insert_into_db(pair, tick_size, data)            
#
        
    def refresh_master_symbols_table(self):
        """Completely rewrite the master symbols table. """
        self.delete_master_symbols_table_data()
        all_symbols = self.return_exchange_pairs()
        for pair in all_symbols:
            self.c.execute("""INSERT INTO master_symbols VALUES (?)""", (pair,))
        self.conn.commit()
        print("Master symbols table has been refreshed.")  
        
        
    def create_all_tables(self):
        """Creates a pairs - tick size table that holds every combination of pairs/tick_size in it. """
        data = self.return_pairs_ticks_combinations()
        for combo in data:
            self.c.execute(f"""CREATE TABLE IF NOT EXISTS {combo} (
            Ind INTEGER PRIMARY KEY,
            UTC_Open TEXT,
            Unix_Open INTEGER,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL NOT NULL,
            Volume REAL NOT NULL,
            UTC_Close TEXT NOT NULL,
            Unix_Close INTEGER NOT NULL,
            Quote_Asset_Volume REAL NOT NULL,
            Number_of_Trades INTEGER NOT NULL,
            Taker_Buy_Base_Asset_Volume REAL NOT NULL,
            Taker_Buy_Quote_Asset_Volume REAL NOT NULL
            )""")
        print("Tables have been updated for all possible pair-tick size combinations.")    
          

    def return_new_symbols(self):
        """Download the latest Binance symbols. Return any not in the master symbols table."""
        all_symbols = self.return_exchange_pairs()
        new_symbols = []
        for symbol in all_symbols:
            self.c.execute("""SELECT Master_pair_list FROM master_symbols WHERE Master_pair_list=?""",(symbol,))
            result = self.c.fetchone()
            if result:
                pass
            else:
                new_symbols.append(symbol)
        return new_symbols
        self.conn.commit()      
    
    
    def update_master_symbols_table(self):
        """Download the latest Binance symbols. If any are new then add them to the master symbols table. """
        new_symbols = self.return_new_symbols()
        for symbol in new_symbols:
            self.c.execute("""INSERT INTO master_symbols (Master_pair_list) VALUES (?)""", (symbol,))
            print(f"{symbol} was added to the master symbols table.")
        self.conn.commit()
         
        
    def populate_table(self, pair, tick_size):
        """Download the latest Binance symbols. If any are new then add them to the master symbols table. """
        start = '1, Jan 2010'
        end = 'now'
        data = self.ohlc(pair, tick_size, start, end)
        self.insert_into_db(pair, tick_size, data)

        
    def mass_populate_table(self):
        pairs_ticks = self.return_pairs_ticks_combinations()
        start = '1, Jan 2017'
        end = 'now'
        for combo in pairs_ticks:
            in_file = self.check_populated_table_records(combo)
            if in_file == False:                
                pair, formatted_tick_size = self.split_combo(combo)
                tick_size = self.reverse_tick_size_formatting(formatted_tick_size)
                data = self.ohlc(pair, tick_size, start, end)
                self.insert_into_db(pair, tick_size, data)
                self.record_new_populated_table(combo)
            elif in_file == True:
               print("already done (check this).")
            else:
                print("broke")
        
        
    def operator_mass_populate_table(self):
        pairs_ticks = self.return_pairs_ticks_combinations()
        mass_operator_completed = 0
        for combo in pairs_ticks:              
            pair, formatted_tick_size = self.split_combo(combo)
            tick_size = self.reverse_tick_size_formatting(formatted_tick_size)
            self.operator(pair, tick_size)
            mass_operator_completed += 1
            print(f"mass operated has completed {mass_operator_completed} table(s).")   

                
    def record_new_populated_table(self, combo):
        """Record each time a pair-tick size table has been populated."""
        fpath = 'D:/Python/python_work/trading_system/records'
        fname = 'populated_tables.csv'
        self.check_folder_exists(fpath)
        self.check_file_exists(fpath, fname)
        outcome = self.check_record_exists(fpath, fname, combo)
        if outcome == True:
            print(f"{combo} table already populated.")
        elif outcome == False:
            with open(f'{fpath}/{fname}', 'a') as f_obj:  # save data to symbols file
                 f_obj.write(f"{combo}\n")
                 print(f"{combo} table now recorded as populated.")
        else:
            print("error at record_populated_table")