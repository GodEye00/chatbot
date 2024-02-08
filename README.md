---

# Flask Chatbot Application with WebSockets

This Flask application provides a web service for handling chat communications with LLM models like GPT-4, GPT-3.5-turbo, and now including Anthropic, using WebSockets. It leverages Flask-SocketIO for real-time communication, integrates Python logging for efficient debugging and monitoring, and utilizes Celery for background task processing. The application also supports file processing and Elasticsearch indexing capabilities, with added Redis caching for encrypted conversation histories.

## Features

- Real-time chat communication using Flask-SocketIO with various LLM models.
- Asynchronous task processing with Celery for improved application efficiency.
- File upload and processing supporting `.txt`, `.pdf`, `.docx`, and `.zip` formats.
- Text chunking and processing using transformer models like BERT and Longformer.
- Integration with Elasticsearch for indexing processed data.
- Redis caching for encrypted conversation histories.
- Configurable Python logging for monitoring and debugging.

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.6 or later
- Flask and Flask-SocketIO
- Elasticsearch
- Redis
- Required Python libraries: `transformers`, `nltk`, `Pandas`, `PyPDF2`, `python-docx`, `numpy`, `Flask-SocketIO`, `Celery`, `redis`, etc.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/chatbot.git
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Export the necessary environment variables as per your `Config` class setup:

```bash
export ELASTICSEARCH_HOST=localhost
export ELASTICSEARCH_INDEX=your-elastic-search-index
export ELASTICSEARCH_PORT=9200
export ELASTICSEARCH_CLOUD_ID=your-cloud-id
export ELASTICSEARCH_API_KEY=your_api_key
export SECRET_KEY=you-will-never-guess
export OPENAI_API_KEY=your_open_ai_key
export CELERY_BROKER_URL=your_celery_broker_url
export CELERY_RESULT_BACKEND=your_result_backend
export REDIS_CHANNEL=your_redis_channel
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_DB=your_redis_db
export AWS_ACCESS_KEY_ID=your_aws_access_key_id
export AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
export AWS_REGION=your_aws_region
export WTF_CSRF_TIME_LIMIT=1800
export CACHE_TYPE=RedisCache
export CACHE_REDIS_URL=redis://localhost:6379/0
export REDIS_EXPIRY=3600
export REDIS_KEY=your_redis_key
...
```

## Running the Application

Use Gunicorn with Eventlet for WebSocket support:

```bash
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 -t 300 app:app
```

Start the Celery worker for background tasks:

```bash
celery -A app:celery worker --concurrency=5 --loglevel=info -P eventlet
```

## WebSocket Chat Communication and Background Tasks

The application features a chat system where users can send messages and receive responses from LLM models in real-time, with support for concurrent model processing and response emission. It uses Flask-SocketIO for handling WebSocket connections and Celery for handling background tasks.

### Endpoints

- `/upload`: Upload documents for indexing.
- `/upload-s3`: Upload documents to S3 for later indexing.
- `/index`: Index uploaded files.
- `/task-status/<task_id>`: Keep track of the status of task submitted for indexing.
- `/get-files`: Retrieve all uploaded files in the S3 bucket.
- `/get-csrf-token`: Get a CSRF token for form uploads.

### WebSocket Listeners and Events

- **Listeners**:
  - `/connect`: Establishes a WebSocket connection. (No connection id will be sent anymore.)
  - `/chat`: Handles incoming chat messages. (connection should not be sent anymore.)

- **Events**:
  - `typing_indicator`: Shows typing status with model identification.
  - `model_response`: Receives responses from language models.
  - `chunks_retrieved`: Lists passages retrieved for LLM processing.
  - `error`: Shows error during processing and includes model identification if model encountered an error while processing

### New Features

- **Celery for Asynchronous Task Processing**: Enhances efficiency by delegating tasks like file processing, indexing, and conversation caching to background workers.
- **Redis Caching**: Manages encrypted conversation histories.
- **Updated WebSocket Events**: `model_response` for language model responses, and an updated `typing_indicator`.
- **Server-Sent Events (SSE) for Task Status Updates**: Streams the status of indexing tasks, providing real-time updates.

## File Processing, Elasticsearch Integration, and Logging

- Supports processing of various file types and indexing in Elasticsearch.
- Configured logging for monitoring application activities and debugging.

## Contributing

Contributions are welcome. Feel free to fork the repository and submit pull requests.

## License

[MIT License](https://opensource.org/licenses/MIT)

---
