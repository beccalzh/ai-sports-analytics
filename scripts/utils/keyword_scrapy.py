#%%
import requests
from bs4 import BeautifulSoup
import json

chunk_size = 1000
with open('data/excl_list.json', 'r') as f:
        excl_list = json.load(f)


## TW basketball

def wiki_twbasketball():
    chunk_size = 1000
    wiki_url = 'http://wikibasketball.dils.tku.edu.tw/index.php?title=%E7%89%B9%E6%AE%8A:%E9%8F%88%E5%85%A5%E9%A0%81%E9%9D%A2/%E5%88%86%E9%A1%9E:%E4%BA%BA%E7%89%A9'
    with open('data/excl_list.json', 'r') as f:
        excl_list = json.load(f)

    keyword_list = []
    next_page = True
    start_page = 0
    while next_page:
        if start_page == 0:
            url = f'{wiki_url}&limit={chunk_size}'
        else:
            url  = f'{wiki_url}&limit={chunk_size}&from={start_page}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        li_tags = soup.find_all('li')
        li_texts = [li.get_text().replace('  \u200e （← 連入）', '') for li in li_tags]
        li_texts = [li.split('/')[-1] for li in li_texts if (li not in excl_list) and ('模板' not in li) and ('分類' not in li)]
        keyword_list.extend(li_texts)
        if len(li_texts) == 0:
            next_page = False
        else: 
            start_page += chunk_size

    with open('data/keyword/basketballTW.json', 'w') as f:
        json.dump(keyword_list, f, ensure_ascii=False, indent=4)


# %%
