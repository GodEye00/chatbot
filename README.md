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

## Running the Application

Use Gunicorn with Eventlet to run the application:

```bash
gunicorn -k eventlet -w 1 -b 0.0.0.0:8000 -t 600 app.app:app
```

- `-k eventlet`: Use Eventlet worker class for concurrent socket connections.
- `-w 1`: Start the server with 1 worker process.
- `-b 0.0.0.0:8000`: Bind to all IP addresses on port 8000.
- `-t 300`: Set a timeout of 300 seconds for worker requests.

## WebSocket Chat Communication

The application features a chat system where users can send messages and receive responses from an llm chat model like gpt-4 in real-time. It uses Flask-SocketIO for handling WebSocket connections.

### Endpoints:

- **Route `/upload`**: Used to upload document(s) for indexing.

### Listeners:

- **WebSocket `/connect`**: Establishes a WebSocket connection and joins a unique room for isolated conversations.
- **WebSocket `/chat`**: Handles incoming chat messages and responds with processed messages.

  ### Events:

  - **WebSocket `connection`**: Use to show that connection is successfully established. 
  - **WebSocket `typing_indicator`**: Use to listen to typing indication showing that the llm model is responding to request.
  - **WebSocket `message_from_llm`**: Use to receive processed messages after llm response is complete. 

## File Processing

Supports processing and handling of various file types, including text, PDF, DOCX, and ZIP files.

## Elasticsearch Integration

Processed data can be indexed in Elasticsearch, enabling powerful search capabilities.

## Logging

Logs are written to `app.log` in the `logs` directory. Log rotation is configured to manage disk space usage.

## Contributing

Feel free to fork the repository and submit pull requests.

## License

[MIT](https://github.com/GodEye00/chatbot#)https://github.com/GodEye00/chatbot#

---
