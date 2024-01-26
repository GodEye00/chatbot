import pandas as pd
from openai import OpenAI
import numpy as np

client = OpenAI()

# Loading the passage_metadata.csv file
passage_metadata_df = pd.read_csv('../docs/output.csv')

# initializing an empty list to store passage metadata and embeddings 
passage_emb_duo = []

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

# Generating embeddings for every passage in the passage_metadata
for index, row in passage_metadata_df.iterrows():
    passage = row['Passage']
    
    # Generating embeddings for the passage
    passage_embedding = get_embedding(passage)
    
    # Append only if embedding is successfully retrieved
    if passage_embedding is not None:
        passage_emb_duo.append({
            'Passage': passage,
            'Embedding': passage_embedding,
        })
    else:
        print(f"Skipping passage at index {index} due to error in embedding retrieval.")

# Creating a DataFrame from the duo
passage_metadata_emb_df = pd.DataFrame(passage_emb_duo)

# Writing the results to passage_metadata_emb.csv
passage_metadata_emb_df.to_csv('../docs/output_emb.csv', index=False)
