from elasticsearch import Elasticsearch, helpers
import pandas as pd
import ast
import os

# Connecting to Elasticsearch
es = Elasticsearch(
    cloud_id=os.environ.get('ELASTICSEARCH_CLOUD_ID'),
    api_key=os.environ.get('ELASTICSEARCH_API_KEY'),
    request_timeout=30,
)

# Defining the index for the mapping
mapping = {
    "mappings": {
        "properties": {
            "Passage": {"type": "text"},
            "Embedding": {
                "type": "dense_vector",
                "dims": 1536,
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# Creating the index for the search
es_index = "search-chatbot"
if es.indices.exists(index=es_index):
    es.indices.delete(index=es_index)
es.indices.create(index=es_index, body=mapping)

# Loading the passage_metadata_emb.csv file
df = pd.read_csv('../docs/output_emb.csv')

# Preparing the passage_metadata for indexing purposes
indexing_data = []
for index, row in df.iterrows():
    try:
        embedding = ast.literal_eval(row['Embedding'])
        if not isinstance(embedding, list):
            raise ValueError(f"Invalid format for embedding at row {index}")

        document = {
            "Passage": row['Passage'],
            "Embedding": embedding
        }
        indexing_data.append({"_index": es_index, "_source": document})
    except Exception as e:
        print(f"Error in row {index}: {e}")

# Finally indexing the data
try:
    helpers.bulk(es, indexing_data)
except helpers.BulkIndexError as e:
    print(f"Bulk indexing error: {e.errors}")
