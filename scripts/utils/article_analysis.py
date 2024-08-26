# article analysis plan
## do vector search on article v
## save article to vectorDB v
## summarize article

import ollama
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv('../../.env')
import os
import pandas as pd
from utils import database

class DataRetrieval:
  def __init__(self):
    client = chromadb.PersistentClient(
      path=os.getenv('CHROMA_DIR'),
      settings=Settings(),
      )
    self.collection = client.get_collection(name="articles")

  def get_href(self, article_ids:list) -> dict:
    db = database.SQLiteOperation()
    query = f'''
    SELECT article_id, href 
    FROM Overview
    WHERE article_id IN {tuple(article_ids)}
    '''
    href_df = db.select_query(query).drop_duplicates()
    return href_df.set_index('article_id')['href'].to_dict()

  def query_data(self, metadata:dict, title:str) -> dict:
    response = ollama.embeddings(
      model = "mxbai-embed-large", 
      prompt = title)
    results = self.collection.query(
      query_embeddings = [response['embedding']],
      n_results = 5,
      where = metadata
    )
    href_dict = self.get_href(results['ids'])
    return {doc:href_dict[_id] for _id, doc in zip(results['ids'], results['documents'])}

  def save_data(self, metadata:dict, article_dict:dict):
    response = ollama.embeddings(model="mxbai-embed-large", prompt=article_dict['title'])
    self.collection.add(
      ids = [article_dict['article_id']],
      embeddings = [response["embedding"]],
      documents = [article_dict['title']],
      metadatas = metadata
    )

  def main(self, board:str, article_dict:dict) -> dict:
    metadata = {'board':board}  
    title = article_dict['title']
    if title != None:
      results = self.query_data(metadata, title) # find similar articles
      # self.save_data(metadata, article_dict) # save article to vectorDB
      return {article_dict['article_id']: results}

