import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    OPENAI_KEY = os.environ.get('OPENAI_KEY') or 'your-open-ai-key'
    ELASTICSEARCH_HOST = os.environ.get('ELASTICSEARCH_HOST') or 'localhost'
    ELASTICSEARCH_CLOUD_ID = os.environ.get('ELASTICSEARCH_CLOUD_ID') or 'your-cloud-id'
    ELASTICSEARCH_INDEX = os.environ.get('ELASTICSEARCH_INDEX') or 'your-elastic-search-index'
    ELASTICSEARCH_PORT = os.environ.get('ELASTICSEARCH_PORT') or 9200
    ELASTICSEARCH_API_KEY = os.environ.get('ELASTICSEARCH_API_KEY')  or ""