from calculations import Calculations

import sqlite3

from itertools import product
import numpy as np
import pandas as pd
import sys
import csv
import os
import time



class Operations(Calculations):
    """
    - Operations combine calculations and data functions to perform specific tasks (operations)
    """
    
            
    def __init__(self):
        super(Operations, self).__init__()
        self.filepath = 'D:/Python/python_work/trading_system/trading_system.db'
        conn = sqlite3.connect(self.filepath)
        self.conn = conn
        self.c = conn.cursor()
        

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
            batch_size = 500
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
            batch_size = 500
            if ticks_to_dl>batch_size:
                batches_remaining = int(np.ceil(ticks_to_dl/batch_size))
                batches_complete = 0
                ticks_remaining = ticks_to_dl
                while ticks_remaining >0:
                    ticks_in_batch = batch_size if ticks_remaining > 500 else ticks_remaining
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
            self.insert_into_db(pair, tick_size, data)
        elif in_file == True:
           print("already done.")
        else:
            print("broke at operator_insert_into_db")
        
    def ohlc(self, pair, tick_size, start, end):
        """Get ohlc data and return it in a formatted table"""
        print(f'Get new data for {pair} ({tick_size})...')
        ohlc_data = self.ohlc_get_data(pair, tick_size, start, end)
        ohlc_formatted = self.ohlc_format_data(ohlc_data)
        return ohlc_formatted


            
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
    
    def insert_into_db(self, pair, tick_size, data):
        """Take ohlc formatted data and insert it into a table
        Pass in only the data which is to be inserted into DB"""
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
            
            
    #create function that combines the three functions below?        
            
            
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
        all_symbols = self.get_all_pairs()
        for pair in all_symbols:
            self.c.execute("""INSERT INTO master_symbols VALUES (?)""", (pair,))
        self.conn.commit()
        print("Master symbols table has been refreshed.")  
        
    def create_all_tables(self):
        """Creates a pairs - tick size table that holds every combination of pairs/tick_size in it. """
        data = self.create_pairs_ticks_combinations()
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
        all_symbols = self.get_all_pairs()
        new_symbols = []
        for symbol in all_symbols:
#            print(symbol)
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
        pairs_ticks = self.create_pairs_ticks_combinations()
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
        pairs_ticks = self.create_pairs_ticks_combinations()
        mass_operator_completed = 0
        for combo in pairs_ticks:              
            pair, formatted_tick_size = self.split_combo(combo)
            tick_size = self.reverse_tick_size_formatting(formatted_tick_size)
            self.operator(pair, tick_size)
            mass_operator_completed += 1
            print(f"mass operated has completed {mass_operator_completed} table(s).")
            
            
            

            
    def check_populated_table_records(self, combo):
         """Check if pair-tick size combination table has been already populated"""
         fpath = 'D:/Python/python_work/trading_system/records'
         fname = 'populated_tables.csv'
         self.check_folder_exists(fpath)
         self.check_file_exists(fpath, fname)
         if os.path.getsize(f"{fpath}/{fname}") > 0:
             #return True if record exists, False if not
             in_file = self.check_record_exists(fpath, fname, combo)
#             print(f"in file?: {in_file}")
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
#                         print("returning true...")
                         return True
#             print("returning false...")
             return False        
           
                
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
            
    def get_master_symbols(self):
        """Update db and then create a list of all the symbols in the master symbol table. """
        self.update_master_symbols_table()
        self.c.execute("""SELECT Master_pair_list FROM master_symbols""")
        all_symbols = self.c.fetchall()
        all_symbols = [_[0] for _ in all_symbols]   #turns list of tuples into a list
        return all_symbols
        
        
    def create_pairs_ticks_combinations(self):
        """Create each combination of pair/ tick_size"""
        fts = self.return_formatted_tick_sizes()
        all_pairs = self.get_master_symbols()
        pairs_ticks = [pair+"_"+fts for pair, fts in product(all_pairs, fts)]
        return pairs_ticks
    

    