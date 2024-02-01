import pandas as pd
from openai import OpenAI
from flask import copy_current_request_context, current_app
import threading

from ..utils.write_to_file import write
client = OpenAI()

file_name = 'output_emb'

def get_embedding_with_error_check(passage, index, model="text-embedding-ada-002"):
    try:
        text = passage.replace("\n", " ")
        return client.embeddings.create(input = [text], model=model).data[0].embedding
    except Exception as e:
        current_app.logger.exception(f"Skipping passage at index {index} due to error in embedding retrieval: {e}")
        return None
    
def perform_embedding(passage):
    current_app.logger.info("About to start performing embedding")
    passage_emb_duo = []

    try: 
        if isinstance(passage, list):
            # Assuming passage_metadata_df is defined elsewhere and accessible
            passage_emb_duo.extend([
                {'Passage': row, 'Embedding': get_embedding_with_error_check(row, index)}
                for index, row in enumerate(passage)
                if get_embedding_with_error_check(row, index) is not None
            ])

        elif isinstance(passage, pd.DataFrame):
            # Apply embedding function across the DataFrame
            passage_emb_duo['Embedding'] = passage['Passage'].apply(
                lambda text: get_embedding_with_error_check(text, passage_emb_duo.index)
            )
            # Filter out rows where embedding retrieval failed
            passage_emb_duo = passage_emb_duo.dropna(subset=['Embedding'])
            
        @copy_current_request_context
        def thread_function():
            try:
                write(passage_emb_duo, 'csv', file_name)
            except Exception as e:
                current_app.logger.exception(f"An error occurred while writing embeddings to CSV. Error: {e}")

        thread = threading.Thread(target=thread_function)
        thread.start()
        return passage_emb_duo
    except Exception as e:
        current_app.logger.exception(f"An error occurred while obtaining embeddings for passages. Error{e}")
        raise Exception("An error occurred while obtaining embeddings")
