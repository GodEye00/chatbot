from elasticsearch import Elasticsearch 
import pandas as pd
import os
from openai import OpenAI
from flask import current_app

client = OpenAI()

# Connecting to Elasticsearch
es = Elasticsearch(
    cloud_id=os.environ.get('ELASTICSEARCH_CLOUD_ID'),
    api_key=os.environ.get('ELASTICSEARCH_API_KEY'),
    request_timeout=30,
)

# Load the user queries 
user_queries = [
    "What is OASIS",
    "Who is Mr. Bugyei",
    "What is transflow used for?"
]

def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding

def retrievePassages(index, size, user_queries = user_queries):
    current_app.logger.info(f"About to retrieve passages for queries: {user_queries}")
    # initializing an empty list which will be used to store the results of the search
    results = []
    # Processing each query
    for query in user_queries:
        # Generating the embeddings for every query in the user_queries
        query_embedding = get_embedding(query)
        # query_embedding = query_embedding.cpu().detach().numpy().flatten()
            
        # Searching elasticsearch for the matched passages
        body = {
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.queryVector, 'Embedding') + 1.0",
                        "params": {"queryVector": query_embedding}
                    }
                }
            }
        }
        response = es.search(index=index, body=body)

        # Getting the needed passages and metadata from the search response
        needed_passages = []
        for hit in response['hits']['hits']:
            passage = hit['_source']['Passage']
            score = hit['_score']
            needed_passages.append((passage, score))

        # sorting the needed passages by their score
        needed_passages.sort(key=lambda x: x[1], reverse=True)

        # extracting the top {size} passages
        top_passages = needed_passages[:size]

        # current_app.logger.info("Passages are: ",needed_passages)

        # extracting the necessary information for csv output
        passage_texts, score = zip(*top_passages)
        passage_texts = list(passage_texts)
        score = list(score)

        results = ""
        for i, passage in enumerate(passage_texts):
            # results.append({
            #     "Question": query,
            #     "Passage 1": passage_texts[0],
            #     "Relevance Score 1": score[0],
            #     "Passage 2": passage_texts[1],
            #     "Relevance Score 2": score[1],
            # })
            results += f" Passage {i+1}: "+ passage_texts[i]+ f" Passage {i+1} Score: "+str(score[i])+"."
        
    # Creating a DataFrame from the results
    # results_df = pd.DataFrame(results)

    # saving final results to the questions_answers.csv
    # results_df.to_csv('../docs/question_answers.csv', index=False)
    return results