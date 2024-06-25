import sqlite3
import pandas as pd

class SQLiteConnectionSettings():
    """ connect to sqlite3 database """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """ use Singleton """
        if not cls._instance:
            cls._instance = super(SQLiteConnectionSettings, cls).__new__(cls)
            cls._instance.conn = sqlite3.connect('../data.db', *args, **kwargs)
            cls._instance.cursor = cls._instance.conn.cursor()
        return cls._instance

    def __init__(self):
        if self.conn is not None:
            print("Connected to SQLite database successfully.")
        else:
            print("Connected to SQLite database unsuccessfully.")

class SQLiteOperation(SQLiteConnectionSettings):
    def create_table(self, table_name:str, column_names:list):
        columns = ', '.join(column_names)
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        self.conn.commit()
        print(f"Table {table_name} has been created successfully.")

    def insert_data(self, table_name:str, data:pd.DataFrame):
        data.to_sql(table_name, self.conn, if_exists='append', index=False)
        print(f"Data has been inserted into {table_name} successfully.")

    def read_data(self, table_name:str, conditions:str=None) -> pd.DataFrame:
        if conditions:
            query = f"SELECT * FROM {table_name} WHERE {conditions}"
        else:
            query = f"SELECT * FROM {table_name}"
        return pd.read_sql_query(query, self.conn)
    
    def update_data(self, table_name:str, conditions:str, new_data:str):
        self.cursor.execute(f"UPDATE {table_name} SET {new_data} WHERE {conditions}")
        self.conn.commit()
        print(f"Data has been updated in {table_name} successfully.")

    def delete_data(self, table_name:str, conditions:str):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE {conditions}")
        self.conn.commit()
        print(f"Data has been deleted from {table_name} successfully.")

    def truncate_table(self, table_name:str):
        self.cursor.execute(f"DELETE FROM {table_name}")
        self.conn.commit()
        print(f"Data has been truncated from {table_name} successfully.")

    def drop_table(self, table_name:str):
        self.cursor.execute(f"DROP TABLE {table_name}")
        self.conn.commit()
        print(f"Table {table_name} has been dropped successfully.")

    def select_table(self, table_name:str, use_col:list=['*']):
        return pd.read_sql_query(f"SELECT {','.join(use_col)} FROM {table_name}", self.conn)

    def select_query(self, query:str):
        return pd.read_sql_query(query, self.conn)

    def close_connection(self):
        self.cursor.close()
        self.conn.close()
        print("Connection to SQLite database has been closed.")
    
        