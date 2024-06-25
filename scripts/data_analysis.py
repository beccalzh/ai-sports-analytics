#%%
from datetime import datetime
import database
db = database.SQLiteOperation()

today = datetime.today().strftime('%Y-%m-%d')
board = 'basketballTW'
query = f'''
SELECT * FROM Article
WHERE date = {today}
AND article_id IN (
    SELECT article_id FROM Overview
    WHERE board = {board}
)
'''
data = db.select_query(query)
# %%
