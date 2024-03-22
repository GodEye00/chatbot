#!/bin/bash

# Export environment variables
export ELASTICSEARCH_CLOUD_ID='your-cloud-id'
export ELASTICSEARCH_API_KEY='your-elasticsearch-api-key'
export OPENAI_API_KEY='your-open-ai-key'
export CELERY_BROKER_URL='your-celery-broker-url'
export CELERY_RESULT_BACKEND='your-celery-result-backend-url'
export AWS_ACCESS_KEY_ID='your-aws-access-key-id'
export AWS_SECRET_ACCESS_KEY='your-aws-secret-access-key'
export AWS_REGION='eu-west-1'
export WTF_CSRF_TIME_LIMIT='1800'
export CACHE_REDIS_URL='redis://localhost:6379/0'
export REDIS_EXPIRY='3600'
export REDIS_KEY='your-redis-key'

echo "Starting Flask application..."
# Use Gunicorn with Eventlet for WebSocket support
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 -t 300 app.app:app &

echo "Starting Celery worker..."
# Start the Celery worker for background tasks
celery -A app.app:celery worker --concurrency=5 --loglevel=info -P eventlet &
