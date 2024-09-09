import collect_articles
import data_analysis
import json
from datetime import date

def main():
    # collect_articles.main()
    da_out = data_analysis.main()
    today = date.today().strftime('%Y-%m-%d')
    with open(f'/Users/becca/ai-sports-analytics/database/da-test/{today}.json', 'w') as f:
        json.dump(da_out, f)
