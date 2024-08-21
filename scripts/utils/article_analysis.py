# article analysis plan
## do vector search on article v
## save article to vectorDB v
## summarize article
#%%

import ollama
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv('../../.env')
import os
import pandas as pd

class DataRetrieval:
  def __init__(self):
    client = chromadb.PersistentClient(
      path=os.getenv('CHROMA_DIR'),
      settings=Settings(),
      )
    self.collection = client.get_collection(name="articles")

  def query_data(self, metadata:dict, title:str) -> list:
    response = ollama.embeddings(
      model = "mxbai-embed-large", 
      prompt = title)
    results = self.collection.query(
      query_embeddings = [response['embedding']],
      n_results = 5,
      where = metadata
    )
    return results['documents']

  def save_data(self, metadata:dict, row:pd.Series):
    response = ollama.embeddings(model="mxbai-embed-large", prompt=row['title'])
    self.collection.add(
      ids = [row['article_id']],
      embeddings = [response["embedding"]],
      documents = [row['title']],
      metadatas = metadata
    )

  def main(self, board:str, article_df:pd.DataFrame):
    metadata = {'board':board}
    out = {}
    """ for testing use only """
    import json 
    from datetime import datetime
    """ for testing use only """
    for _, row in article_df.iterrows():
      title = row['title']
      if title != None:
        results = self.query_data(metadata, title) # find similar articles
        # out[row['article_id']] = results
        """ for testing use only """
        out[title] = results
        json.dump(out, open(f"article_analysis/{datetime.today().strftime('%Y-%m-%d')}.json","w"))
        """ for testing use only """
        self.save_data(metadata, row)
        return out

