from elasticsearch import Elasticsearch, helpers
from flask import current_app
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

def process_row(row, es_index):
    try:
        embedding = row['Embedding'] if isinstance(row, pd.Series) else row.get('Embedding')
        embedding = ast.literal_eval(embedding) if isinstance(embedding, str) else embedding
        if not isinstance(embedding, list):
            raise ValueError("Invalid format for embedding")
        return {
            "_index": es_index,
            "_source": {
                "Passage": row['Passage'],
                "Embedding": embedding
            }
        }
    except Exception as e:
        current_app.logger.exception(f"Error processing row: {e}")
        return None

# Preparing the passage_metadata for indexing purposes
index = "search-chatbot-final"
def index_data(data, es_index=index, mapping=mapping):
    current_app.logger.info("About to start indexing data")
    indexing_data = []
    if isinstance(data, pd.DataFrame):
        data_iter = data.iterrows()
    elif isinstance(data, list):
        data_iter = enumerate(data)
    else:
        raise TypeError("Data must be a pandas DataFrame or a list")

    for index, row in data_iter:
        document = process_row(row, es_index)
        if document:
            indexing_data.append(document)

    try:
        if es.indices.exists(index=es_index):
            es.indices.delete(index=es_index)
        es.indices.create(index=es_index, body=mapping)
        helpers.bulk(es, indexing_data)
        current_app.logger.info("Successfully indexed data")
        return True
    except Exception as e:  # Catching broader exceptions for robust error handling
        current_app.logger.execption(f"Error during indexing: {e}")
        return False
