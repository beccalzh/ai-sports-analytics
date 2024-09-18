import collect_articles
import data_analysis
import json
from datetime import date
import os

def main():
    collect_articles.main()
    da_out = data_analysis.main()
    today = date.today().strftime('%Y-%m-%d')
    if '../database/da-test/' not in os.listdir():
        os.mkdir('../database/da-test')
    with open(f'../database/da-test/{today}.json', 'w') as f:
        json.dump(da_out, f)
        print(da_out)
