#%%
from datetime import datetime
import database
db = database.SQLiteOperation()

today = datetime.today().strftime('%Y-%m-%d') # 2024-06-24 for test
board = 'basketballTW'
query = f'''
SELECT * FROM Article
WHERE date = '{today}' 
AND article_id IN (
    SELECT article_id FROM Overview
    WHERE board = '{board}'
    AND popularity = 100
)
''' 

data = db.select_query(query)
# %%
