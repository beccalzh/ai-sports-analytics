import schedule
import scripts.collect_articles.collect_articles as collect_articles 
import time

# def test():
#     print('Hello World')

# schedule.every(1).minutes.do(test)

def collect_schedule():
    collect_articles.main()
    
schedule.every().day.at("12:00").do(collect_schedule) # post time

while True:
    schedule.run_pending()
    time.sleep(1)