# article analysis plan
## do vector search on article
## save article to vectorDB
## summarize article
#%%
import chromadb
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from dotenv import load_dotenv
load_dotenv('../../.env')
import os

client = chromadb.PersistentClient(
    path=os.getenv('CHROMA_DIR'),
    settings=Settings(),
)

#%%
import ollama
# collection = client.create_collection(name="articles")
collection = client.create_collection(name="test")
documents = [
  "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
  "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
  "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
  "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
  "Llamas are vegetarians and have very efficient digestive systems",
  "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
]
for i, d in enumerate(documents):
  response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
  embedding = response["embedding"]
  collection.add(
    ids=[f'test_{str(i)}'],
    embeddings=[embedding],
    documents=[d],
    metadatas={'category':'a'}
  )

#%%
client.delete_collection('test')
#%%
import ollama
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
load_dotenv('../../.env')
import os
import pandas as pd

client = chromadb.PersistentClient(
  path=os.getenv('CHROMA_DIR'),
  settings=Settings(),
  )
collection = client.get_collection(name="articles")

# metadata = {'board':'NBA'}
class DataRetrieval:
  def __init__(self, collection):
    self.collection = collection

  def query_data(self, metadata:dict, title:str):
    response = ollama.embeddings(
      model="mxbai-embed-large", 
      prompt=title)
    results = self.collection.query(
      query_embedding=[response['embedding']],
      n_results=5,
      metadata=metadata
    )
    return results['documents']

  def save_data(self, metadata:dict, )

  def main(self, board:str, article_df:pd.DataFrame):
    metadata = {'board':board}
    for index, row in article_df.iterrows():
      title = row['title']
      results = self.query_data(metadata, title)



