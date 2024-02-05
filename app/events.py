import threading
from flask_socketio import emit, join_room
from flask import request, copy_current_request_context, current_app
import uuid
from threading import Lock

from app.gpt import ask_gpt4
from .app import socketio
from .helpers.retrieval import retrievePassages
from .helpers.summerizing import summarize_conversation, summarize_conversation_t5


conversations = {}
conversation_lock = Lock()
default_messages = [
    {"role": "system", "content": "You're 'Romeo,' the IT Consortium chatbot, here to answer "+
                               " questions about our services. You'll get more info denoted by 'Context:' for "+
                                "better replies. Use a friendly tone. For greetings like 'Hi/What's up/Yo'"+
                                "respond as if starting fresh: Without Context. "+
                                "Ignore 'Context:' for greetings. If unsure about names, ask for clarity."},
]

def authenticate_user(request):
    # TODO: implement authentication
    pass

def generate_conversation_id():
    return str(uuid.uuid4())


def update_conversation_history(conversation_id, message, default_messages=default_messages, summary=False):
    if conversation_id not in conversations:
        conversations[conversation_id] = default_messages.copy()

    if summary:
        new_conversation = default_messages.copy() + [message]
        conversations[conversation_id] = new_conversation
    else:
        conversations[conversation_id].append(message)

def summary(conversation_id):
         summarized_text = summarize_conversation_t5(conversations.get(conversation_id, []))
         if summarized_text:
            new_default_messages = [
                        {"role": "system", "content": "You're 'Romeo,' the IT Consortium chatbot, here to answer "+
                                                    " questions about our services. You'll get more info denoted by 'Context:' for "+
                                                        "better replies. Use a friendly tone. For greetings like 'Hi/What's up/Yo'"+
                                                        "respond as if starting fresh: Without Context. "+
                                                        "Ignore 'Context:' for greetings. If unsure about names, ask for clarity."},
                        ]
            update_conversation_history(conversation_id, summarized_text, new_default_messages, True)


@socketio.on('connect')
def handle_connect():
    current_app.logger.info("Connected")
    user = authenticate_user(request)
    conversation_id = user.conversation_id if user else generate_conversation_id()
    join_room(conversation_id)
    emit('connection', {'connection_id': conversation_id})

@socketio.on('chat')
def handle_client_message(json):
    current_app.logger.info(f"Got chat: {json}")
    conversation_id = json.get('connection_id', "")
    user_message = json['message']

    # Retrieve and prepare the message
    index = json.get('index', 'search-chatbot-final')
    size = json.get('size', 2)
    chunks, retrieved_passage = retrievePassages(index, size, [user_message])
    emit('chunks_retrieved', {'chunks': chunks}, room=conversation_id)
    message = {"role": "user", "content": user_message + ". Context: " + retrieved_passage}

    update_conversation_history(conversation_id, message)
    emit('typing_indicator', {'status': True}, room=conversation_id)

    @copy_current_request_context
    def process_message():
        try:
            response = ask_gpt4(conversations.get(conversation_id, default_messages))
            update_conversation_history(conversation_id, response)
            emit('typing_indicator', {'status': False}, room=conversation_id)
            emit('message_from_llm', {'message': response["content"]}, room=conversation_id)
            summary(conversation_id)
        except Exception as e:
            current_app.logger.error(f"Error processing message: {e}")
            emit('error', {'error': "An error occurred while processing message"}, room=conversation_id)

    threading.Thread(target=process_message).start()

@socketio.on('disconnect')
def handle_disconnect():
    try:
        # Your disconnect logic here
        print('Client disconnected')
    except Exception as e:
        print(f'Error during disconnect: {e}')
