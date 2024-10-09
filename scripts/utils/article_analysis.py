# article analysis plan
## do vector search on article v
## save article to vectorDB v
## summarize article

import ollama
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv('../../.env')
# load_dotenv()
import os
import pandas as pd
from utils import database

class DataRetrieval:
  def __init__(self):
    self.client = chromadb.PersistentClient(
      path=os.getenv('CHROMA_DIR'),
      settings=Settings(),
      )

  def get_collection(self, board:str):
    return self.client.get_or_create_collection(board)

  def get_href(self, article_ids:list) -> dict:
    db = database.SQLiteOperation()
    query = f'''
    SELECT article_id, href 
    FROM Overview
    WHERE article_id IN {tuple(article_ids)}
    '''
    href_df = db.select_query(query).drop_duplicates()
    return href_df.set_index('article_id')['href'].to_dict()

  def query_data(self, collection, title:str) -> dict:
    response = ollama.embeddings(
      model = "mxbai-embed-large", 
      prompt = title)
    results = collection.query(
      query_embeddings = [response['embedding']],
      n_results = 5
    )
    href_dict = self.get_href(results['ids'][0])
    return {doc:href_dict[_id] for _id, doc in zip(results['ids'][0], results['documents'][0])}

  def save_data(self, collection, article_dict:dict):
    if article_dict['title'] != None:
      response = ollama.embeddings(model="mxbai-embed-large", prompt=article_dict['title'])
      collection.add(
        ids = [article_dict['article_id']],
        embeddings = [response["embedding"]],
        documents = [article_dict['title']],
      )

  def main(self, board:str, article_dict:dict) -> dict:
    collection = self.get_collection(board)
    title = article_dict['title']
    if title != None:
      results = self.query_data(collection, title) # find similar articles
      # self.save_data(collection, article_dict) # save article to vectorDB
      return {article_dict['article_id']: results}

