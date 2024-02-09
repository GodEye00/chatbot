import os

class Config(object):
    ELASTICSEARCH_CLOUD_ID = os.environ.get('ELASTICSEARCH_CLOUD_ID') or 'your-cloud-id'
    ELASTICSEARCH_API_KEY = os.environ.get('ELASTICSEARCH_API_KEY')  or ""
    OPENAI_KEY = os.environ.get('OPENAI_API_KEY') or 'your-open-ai-key'
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or ""
    RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or ""
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or ""
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or ""
    AWS_REGION = os.environ.get('AWS_REGION') or "eu-west-1"
    WTF_CSRF_TIME_LIMIT = os.environ.get('WTF_CSRF_TIME_LIMIT') or "1800"
    CACHE_REDIS_URL = os.environ.get('CACHE_REDIS_URL') or 'redis://localhost:6379/0'
    REDIS_EXPIRY = os.environ.get('REDIS_EXPIRY') or '3600'
    REDIS_KEY = os.environ.get('REDIS_Key') or 'sXQVG8yTQt-j97ZV1HAGGup-DD2dbx8WzFZtZG9DkWY='