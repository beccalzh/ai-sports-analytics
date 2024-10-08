#%%
from datetime import datetime, timedelta
from utils import database, comment_analysis, article_analysis
from utils.log_decorator import log_decorator # log decorator
import pandas as pd


class DataSelection:
    def __init__(self):
        self.db = database.SQLiteOperation()

    @log_decorator
    def board_cond(self) -> dict:
        board_cond = {}
        query = 'SELECT * FROM Overview'
        alldf = self.db.select_query(query)
        for board in alldf['board'].unique():
            res = alldf[(alldf['board'] == board)&(alldf['popularity'] > 0)]
            for n in range(2): # do it twice to get rid of outliers
                median = res.describe()['popularity']['50%']
                res = res[res['popularity'] > median]
            board_cond[board] = res.describe()['popularity']['75%']
        return board_cond

    @log_decorator
    def article_query(self, date: str, board: str, popularity: int) -> str:
        return f'''
        SELECT article_id, title, article 
        FROM Article
        WHERE article_id IN (
            SELECT article_id FROM Overview
            WHERE board = '{board}'
            AND popularity >= {popularity}
            AND update_at BETWEEN '{date}' AND '{datetime.today().strftime('%Y-%m-%d')}'
        )
        ORDER BY date DESC
        '''
    
    @log_decorator
    def article_data(self, ndays: int, board: str, popularity: int) -> pd.DataFrame:
        date = (datetime.today() - timedelta(days=ndays)).strftime('%Y-%m-%d')
        query = self.article_query(date, board, popularity)
        article_df = self.db.select_query(query)

        # if the query returns nothing, try the previous day
        while len(article_df) == 0:
            ndays += 1
            date = (datetime.today() - timedelta(days=ndays)).strftime('%Y-%m-%d')
            query = self.article_query(date, board, popularity)
            article_df = self.db.select_query(query)
        return article_df.drop_duplicates()
    
    @log_decorator
    def comment_data(self, article_ids:list) -> pd.DataFrame:
        query = f'''
        SELECT article_id, comment 
        FROM Comment
        WHERE article_id IN {tuple(article_ids)}
        '''
        return self.db.select_query(query).drop_duplicates()
    
    @log_decorator
    def main(self, board:str, popularity:int) -> dict:
        board_out = {}
        article_df = self.article_data(1, board, popularity)
        comment_df = self.comment_data(article_df['article_id'].to_list())  
        for aid in comment_df['article_id'].unique():
            res_article = article_df[article_df['article_id'] == aid].to_dict(orient='records')[0]
            ## similarity search
            similar_articles = article_analysis.DataRetrieval().main(board, res_article)
            ## summarize article
            ## keyword extraction
            comment_list = comment_df[comment_df['article_id'] == aid]['comment'].to_list()
            comment_out = comment_analysis.CommentChunker(comment_list).main()
            # input to comment_analysis.py `res_comment['comment'].to_list()`
            board_out[aid] = {'similar_articles': similar_articles, 'comment_out': comment_out}
        return board_out

def main() -> dict:
    ds = DataSelection()
    board_cond = ds.board_cond() # {board(str): popularity(float)}
    out = {}
    for board, popularity in board_cond.items():
        out[board] = ds.main(board, popularity)
    return out
# %%
