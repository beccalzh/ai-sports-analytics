#%%
import requests
import database
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
db = database.SQLiteOperation()
update_at = datetime.today().strftime('%Y-%m-%d')
from log_decorator import log_decorator # log decorator

class PTTArticle:
    def __init__(self, board:str):
        self.board = board
        self.page_count = 10
        self.start_index = self.get_start_index()
        self.use_board = {'basketballTW': ['討論', '新聞', '情報', '乳摸'],
                          'baseball': ['分享', '新聞', '討論', '情報'],
                          'NBA': ['討論', '新聞', '情報', '花邊']}
    @log_decorator    
    def get_start_index(self) -> int:
        index_page = f'https://www.ptt.cc/bbs/{self.board}/index.html'
        response = requests.get(index_page)
        soup = BeautifulSoup(response.text, 'html.parser')
        return int(soup.find_all('a', 'btn wide')[1]['href'].split('index')[1].replace('.html', ''))+1

    @log_decorator
    def get_popularity(self, article:BeautifulSoup) -> int:
        push = article.find('div', 'nrec').text
        if push == '':
            return 0
        elif push == '爆':
            return 100
        elif push[:1] == 'X':
            if push == 'XX':
                return -100
            else:
                return -10*int(push[1])
        return int(push)

    @log_decorator
    def get_headline(self, article:BeautifulSoup) -> str:
        if '刪除) <' in article.find('div', 'title').text.strip():
            return '[deleted] deleted'
        return article.find('div', 'title').text.strip()

    @log_decorator
    def split_cate_reply(self, article:BeautifulSoup):
        title = self.get_headline(article).split(']')
        pattern = r"\(已被(.+?)刪除\)"
        reply = False
        if bool(re.search(pattern, title[-1])):
            return 'deleted', reply
        elif len(title) == 1:
            return None, reply
        if 'Re:' in title[0]:
            reply = True
        return title[0].split('[')[1].lower(), reply

    @log_decorator
    def get_href(self, article:BeautifulSoup) -> str:
        return article.a['href']

    @log_decorator
    def collect_article_data(self) -> list: # list of html
        article_data = []
        for i in range(self.start_index, self.start_index-self.page_count, -1):
            url = f'https://www.ptt.cc/bbs/{self.board}/index{i}.html'
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            link_data = soup.find_all('div', 'r-ent')
            article_data.extend(link_data)
        return article_data

    @log_decorator
    def article_filter(self, article_data:list) -> pd.DataFrame:
        article_df = pd.DataFrame()
        for article in article_data:
            cate, reply = self.split_cate_reply(article)
            if cate in self.use_board[self.board]:
                res_df = pd.DataFrame([self.get_popularity(article), cate, reply, self.get_href(article)]).T
                article_df = pd.concat([article_df, res_df], ignore_index=True)
        article_df.columns = ['popularity', 'category', 'reply', 'href']
        article_df = article_df.sort_values('popularity', ascending=False).reset_index(drop=True)
        return article_df

    def main(self) -> pd.DataFrame:
        article_data = self.collect_article_data()
        article_df = self.article_filter(article_data)
        article_df['article_id'] = [href.split('.')[1] for href in article_df['href']]
        article_df['board'] = self.board
        article_df['update_at'] = update_at
        db.insert_data('Overview', article_df) # insert data into database
        return article_df[['href', 'article_id']]

class ArticleContent:
    def __init__(self, href, article_id):
        self.url = f'https://www.ptt.cc{href}'
        self.article_id = article_id

    @log_decorator
    def get_title(self, soup:BeautifulSoup) -> str:
        meta_content = soup.find('meta', {'property': 'og:title'})['content']
        if ']' in meta_content:
            return meta_content.split(']')[1].strip()
        else:
            return meta_content

    @log_decorator
    def get_article(self, all_content:list) -> str:
        return''.join([i for i in all_content[0].split('\n')[1:] if i != ''])

    @log_decorator
    def get_date(self, all_content:list) -> str:
        match = re.search(r'\w{3} (\w{3}) (\d{2}) (\d{2}:\d{2}:\d{2}) (\d{4})', all_content[0])
        if match:
            date_str = f"{match.group(4)}-{match.group(1)}-{match.group(2)}"  # 格式化為 'YYYY-MMM-DD'
            # 將月份的英文縮寫轉換為數字
            date_obj = datetime.strptime(date_str, '%Y-%b-%d')
            return date_obj.strftime('%Y-%m-%d')  # 轉換為 'YYYY-MM-DD' 格式
        else:
            return None

    @log_decorator
    def get_comment_info(self, all_content:list) -> list:
        comments = all_content[1].split('\n')[1:-1]
        last_commenter = None
        comment_data = []
        for comment in comments:
            id_and_text = comment.split(': ') 
            try:    
                push = id_and_text[0].split()[0]
                id = id_and_text[0].split()[-1]
                text = re.sub(r'\d{2}/\d{2} \d{2}:\d{2}', '', id_and_text[1]).strip()
                if id == last_commenter:
                    comment_data[-1][2] += text 
                elif (id == '編輯' or (id == '文章網址')):
                    pass
                else:
                    comment_data.append([push, id, text])  
                last_commenter = id 
            except IndexError:
                pass
        return comment_data

    
    def main(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        main_content = soup.find('div', {'id': 'main-content'})
        span_f2 = main_content.find('span', {'class': 'f2'})
        all_content = main_content.get_text().split(span_f2.get_text())
        title = self.get_title(soup)
        article = self.get_article(all_content)
        article_date = self.get_date(all_content)
        comment_info = self.get_comment_info(all_content)
        db.insert_data('Article', pd.DataFrame([{'article_id': self.article_id,
                                                 'title': title,
                                                 'article': article,
                                                 'date': article_date,
                                                 'update_at': update_at}])) # insert data into 'Article' table
        comment_df = pd.DataFrame(comment_info, columns=['reaction', 'commenter', 'comment'])
        comment_df['article_id'] = self.article_id
        comment_df['update_at'] = update_at
        db.insert_data('Comment', comment_df) # insert data into 'Comment' table
#%%
if __name__ == '__main__':
    target_board = {'basketballTW': 11, 
                    'baseball': 15, 
                    'NBA': 30}
    for board in target_board:
        article_df = PTTArticle(board).main().head(target_board[board])
        for index, row in article_df.iterrows():
            ArticleContent(row['href'], row['article_id']).main()
        