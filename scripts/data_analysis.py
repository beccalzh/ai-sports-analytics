#%%
from datetime import datetime, timedelta
import database
db = database.SQLiteOperation()
import pandas as pd
from ckip_transformers.nlp import CkipNerChunker
import numpy as np

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

class CommentAnalysis:
    def __init__(self, comment_list:list):
        self.comment_list = comment_list
        self.ner_driver = CkipNerChunker(model="bert-base")
        self.unwanted = ['CARDINAL', 'DATE', 'NORP']
    
    def combine_dict(self, d1:dict, d2:dict) -> dict:
        out = {}
        for key in set(d1) | set(d2):
            out[key] = d1.get(key, []) + d2.get(key, [])
        return out

    def get_entity(self) -> list:
        ner_sentence_list = self.ner_driver(self.comment_list, use_delim=True, batch_size=256, max_length=128)
        entity_out = {}
        for sentence, ner in zip(self.comment_list, ner_sentence_list):
            res = {j.word:[sentence] for j in ner if j.ner not in self.unwanted}
            entity_out = self.combine_dict(entity_out, res)
        return entity_out
    
    def keyword_selection(self, entity_dict:dict) -> dict:
        lengths = [len(v) for v in entity_dict.values()]        
        pr95_length = np.percentile(lengths, 95)        
        pr95_dict = {k: v for k, v in entity_dict.items() if len(v) >= pr95_length}
        return pr95_dict
        
    def main(self) -> list:
        entity_out = self.get_entity()
        pr95_dict = self.keyword_selection(entity_out)
        return list(pr95_dict.keys()), list(pr95_dict.values())

#%%
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
            pr95_key, pr95_val = CommentAnalysis(res_comment['comment'].to_list()).main() ## keyword extracted from comments
