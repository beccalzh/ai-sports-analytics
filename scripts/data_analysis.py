from datetime import datetime, timedelta
import sys
sys.path.append('../utils')
import scripts.database as database
db = database.SQLiteOperation()
import pandas as pd
import sys
import comment_analysis

board = 'basketballTW' # for testing

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
            for n in range(2): # do it twice to get rid of outliers
                median = res.describe()['popularity']['50%']
                res = res[res['popularity'] > median]
            board_cond[board] = res.describe()['popularity']['75%']
        return board_cond

    @staticmethod
    def article_data(ndays:int, board:str, popularity:int) -> pd.DataFrame:
        date = (datetime.today() - timedelta(days=ndays)).strftime('%Y-%m-%d')
        query = f'''
        SELECT article_id, date, title, article 
        FROM Article
        WHERE article_id IN (
            SELECT article_id FROM Overview
            WHERE board = '{board}'
            AND popularity >= {popularity}
            AND update_at BETWEEN '{date}' AND '{datetime.today().strftime('%Y-%m-%d')}'
        )
        ''' 
        return db.select_query(query)
    
    @staticmethod
    def comment_data(article_ids:list) -> pd.DataFrame:
        query = f'''
        SELECT article_id, reaction, comment 
        FROM Comment
        WHERE article_id IN {tuple(article_ids)}
        '''
        return db.select_query(query)


def main() -> pd.DataFrame:
    board_cond = DataSelection.board_cond() # {board(str): popularity(float)}
    for board, popularity in board_cond.items():
        article_df = DataSelection.article_data(1, board, popularity)
        comment_df = DataSelection.comment_data(article_df['article_id'].to_list())  
        for aid in comment_df['article_id'].unique():
            res_article = article_df[article_df['article_id'] == aid]
            ## summarize article
            ## similarity search
            res_comment = comment_df[comment_df['article_id'] == aid]
            # input to comment_analysis.py `res_comment['comment'].to_list()`
