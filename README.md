
---

# Flask Chatbot Application with WebSockets

This Flask application provides a web service for handling chat communications with llm models like gpt-4 and gpt-3.5-turbo using WebSockets, along with file processing and Elasticsearch indexing capabilities. It leverages Flask-SocketIO for real-time communication and integrates Python logging for efficient debugging and monitoring.

## Features

- Real-time chat communication using Flask-SocketIO for communicating with various chat models.
- File upload and processing supporting `.txt`, `.pdf`, `.docx`, and `.zip` formats.
- Text chunking using transformer models like BERT and Longformer.
- Integration with Elasticsearch for indexing processed data.
- Configurable Python logging for monitoring and debugging.

## Prerequisites

Before running the application, ensure you have the following installed:
- Python 3.6 or later
- Flask and Flask-SocketIO
- Elasticsearch
- Required Python libraries: `transformers`, `nltk`, `Pandas`, `PyPDF2`, `python-docx`, `numpy`, `Flask-SocketIO`, etc.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GodEye00/chatbot.git
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Export necessary environment variables:
   ```bash
   export ELASTICSEARCH_CLOUD_ID=your_cloud_id
   export ELASTICSEARCH_API_KEY=your_api_key
   export OPENAI_API_KEY=your_openai_key
   export AWS_ACCESS_KEY_ID=aws_access_key_id
   export AWS_SECRET_ACCESS_KEY=aws_secret_access_key
   export AWS_REGION=your_region
   ```

## Running the Application

Use Gunicorn with Eventlet to run the application:

```bash
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 -t 300 app.app:app
```

- `-k eventlet`: Use Eventlet worker class for concurrent socket connections.
- `-w 1`: Start the server with 1 worker process.
- `-b 0.0.0.0:8000`: Bind to all IP addresses on port 8000.
- `-t 300`: Set a timeout of 300 seconds for worker requests.

## WebSocket Chat Communication

The application features a chat system where users can send messages and receive responses from an llm chat model like gpt-4 in real-time. It uses Flask-SocketIO for handling WebSocket connections.

### Endpoints:

- **Route `/upload`**: Used to upload document(s) for indexing. The endpoint requires the following payload:
  - `data`: The zipped file(s) to be uploaded.
  - `index` (optional): The Elasticsearch index to be used (default is 'search-chatbot-final').
  - `split_size` (optional): The size for splitting the text for indexing (default is 3).

- **Route `/upload-s3`**: Used to upload document(s) to s3 bucket which may later be used for indexing. The endpoint requires the following payload:
  - `data`: The zipped file(s) to be uploaded.

- **Route `/index`**: Used for indexing uploaded files. The endpoint requires the following payload:
  - `file`: The name of the file to use for the indexing. File must have already been uploaded. Use 'all' to denote indexing ALL currently uploaded files in s3 bucket. Default is 'all'.
  - `index` (optional): The Elasticsearch index to be used (default is 'search-chatbot-final').
  - `split_size` (optional): The size for splitting the text for indexing (default is 3).

- **Route `/get-files`**: Used to get all uploaded files in s3 bucket.

- **Route `/get-csrf-token`**: Used to get csrf token that must be added to all forms upload. Add this csrf token in order to upload any form data.


### Listeners:

- **WebSocket `/connect`**: Establishes a WebSocket connection and joins a unique room for isolated conversations.
- **WebSocket `/chat`**: Handles incoming chat messages and responds with processed messages.
    - Payload for the `/chat` event:
      - `message`: The user's message.
      - `connection_id`: connection id returned after connection is established. This is required to join a conversation room with the llm.
      - `index` (optional): The Elasticsearch index to be used (default is 'search-chatbot-final').
      - `size` (optional): The size parameter for the model's response (default is 2).

  ### Events:

  - **WebSocket `connection`**: Used to show that the connection is successfully established. Data type is string.
  - **WebSocket `typing_indicator`**: Used to listen to typing indication showing that the llm model is responding to a request. Data type is string.
  - **WebSocket `message_from_llm`**: Used to receive processed messages after llm response is complete. Data type is string.
  - **WebSocket `chunks_retrieved`**: Used to list the passages that were retrieved and added to the prompt's context for llm to process. Data type is array[].

## File Processing

Supports processing and handling of various file types, including text, PDF, DOCX, and ZIP files.

## Elasticsearch Integration

Processed data can be indexed in Elasticsearch, enabling powerful search capabilities.

## Logging

Logs are written to `app.log` in the `logs` directory. Log rotation is configured to manage disk space usage.

## Contributing

Feel free to fork the repository and submit pull requests.

## License

[MIT](https://github.com/GodEye00/chatbot#)

---
