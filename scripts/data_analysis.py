#%%
from datetime import datetime, timedelta
import database
db = database.SQLiteOperation()

b4yesterday = (datetime.today() - timedelta(days=2)).strftime('%Y-%m-%d')   
yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
board = 'basketballTW'

class DataSelection:
    def __init__(self):
        pass
    
    @staticmethod
    def board_cond() -> dict:
        board_cond = {}
        query = 'SELECT * FROM Overview'
        alldf = db.select_query(query)
        for board in alldf['board'].unique():
            res = alldf[(alldf['board'] == board)&(alldf['popularity'] > 0)]
            for n in range(2):
                median = res.describe()['popularity']['50%']
                res = res[res['popularity'] > median]
            board_cond[board] = res.describe()['popularity']['75%']
        return board_cond

    @staticmethod
    def get_data(ndays:int, board:str, popularity:int) -> list:
        date = (datetime.today() - timedelta(days=ndays)).strftime('%Y-%m-%d')
        query = f'''
        SELECT * FROM Article
        WHERE date BETWEEN '{date}' AND '{datetime.today().strftime('%Y-%m-%d')}' 
        AND article_id IN (
            SELECT article_id FROM Overview
            WHERE board = '{board}'
            AND popularity >= {popularity}
        )
        ''' 
        return db.select_query(query)

def main():
    board_cond = DataSelection.board_cond()
    for board, popularity in board_cond.items():
        data = DataSelection.get_data(3, board, popularity)
        # do something with data


# %%
