#%%
from datetime import datetime, timedelta
import database
db = database.SQLiteOperation()
import pandas as pd

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
            for n in range(2): # do it twice to get rid of outliers
                median = res.describe()['popularity']['50%']
                res = res[res['popularity'] > median]
            board_cond[board] = res.describe()['popularity']['75%']
        return board_cond

    @staticmethod
    def article_data(ndays:int, board:str, popularity:int) -> pd.DataFrame:
        date = (datetime.today() - timedelta(days=ndays)).strftime('%Y-%m-%d')
        query = f'''
        SELECT DISTINCT article_id, date, title, article 
        FROM Article
        WHERE date BETWEEN '{date}' AND '{datetime.today().strftime('%Y-%m-%d')}' 
        AND article_id IN (
            SELECT article_id FROM Overview
            WHERE board = '{board}'
            AND popularity >= {popularity}
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

#%%
from ckip_transformers.nlp import CkipNerChunker
from collections import Counter

class CommentAnalysis:
    def __init__(self, comment_list:list):
        self.comment_list = comment_list
        self.ner_driver = CkipNerChunker(model="bert-base")
        self.unwanted = ['CARDINAL', 'DATE', 'NORP']
    
    def get_entity(self) -> list:
        if self.comment_list == ['']:
            return []
        ner_sentence_list = self.ner_driver(self.comment_list, use_delim=True, batch_size=256, max_length=128)
        entity_out = [list(i) for i in ner_sentence_list if len(i) != 0]
        return entity_out

    def sort_entity(self, entity_list:list) -> dict:
        result = {}
        for t in entity_list:
            for j in t:
                if j.ner in result:
                    result[j.ner].append(j.word)
                elif j.ner in self.unwanted:
                    continue
                else:
                    result[j.ner] = [j.word]
        return {k:Counter(v) for k, v in result.items()}

    def main(self):
        entity_list = self.get_entity()
        return self.sort_entity(entity_list)


#%%
def main():
    board_cond = DataSelection.board_cond()
    for board, popularity in board_cond.items():
        article_df = DataSelection.article_data(3, board, popularity)
        comment_df = DataSelection.comment_data(article_df['article_id'].to_list())
        # do something with data
        ## summarize article
        ## keyword extracted from comments


# %%
