import threading
from flask_socketio import emit, join_room
from flask import request, copy_current_request_context, current_app
import uuid
from app.gpt import ask_gpt4
from .app import socketio
from .helpers.retrieval import retrievePassages
from .helpers.summerizing import summarize_conversation, summarize_conversation_t5

conversations = {}
default_messages = [
            {"role": "system", "content": "You are Romeo. IT Consortium's personal chatbot agent who responds to user queries concerning all questions they have about the company, our product, services and what we do. Play to your strength as an llm without any legal compromises. You may receive some sample information (starting with the key 'info:') together with its score (denoted by 'score:') about the question asked in order to add to your context and aid you in responding to the question. The higher the score the higher the relevance of the info"},
            {"role": "user", "content": "What is IT Consortium"},
            {"role": "assistant", "content": "IT Consortium is one of Africa’s leading financial services technology solutions provider. Our mission is simple: To provide innovative systems that bring obvious value to our patrons. We adapt technology to create systems that provide clear competitive advantages to our customers."},
        ]

@socketio.on('connect')
def handle_connect():
    current_app.logger.info("Connected")
    # Authenticate user and get user-specific conversation ID or generate a new one
    user = authenticate_user(request)
    conversation_id = user.conversation_id if user else generate_conversation_id()
    join_room(conversation_id)  # Join a room specific to the conversation
    emit('connection', {'connection_id': conversation_id } )

@socketio.on('chat')
def handle_client_message(json):
    current_app.logger.info(f"Got chat: {json} ")
    conversation_id = json.get('connection_id', "")
    user_message = json['message']
    index = json.get('index', 'search-chatbot-final')
    size = json.get('size', 2)
    retrieved_passage = retrievePassages(index, size, [user_message])
    message = {"role": "user", "content": user_message+"\ninfo: " + retrieved_passage}
    update_conversation_history(conversation_id, message, default_messages)
        # Emitting typing status before processing the message
    emit('typing_indicator', {'status': True}, room=conversation_id)

    
    # Processing the message in a separate thread
    @copy_current_request_context
    def process_message():
        response = ask_gpt4(conversations.get(conversation_id, default_messages.append(message)))
        update_conversation_history(conversation_id, response)
        emit('typing_indicator', {'status': False}, room=conversation_id)
        emit('message_from_llm', {'message': response["content"]}, room=conversation_id)
        summary(conversation_id)


    threading.Thread(target=process_message).start()
    # threading.Thread(target=summary).start()
    
    

def summary(conversation_id):
         summarized_text = summarize_conversation_t5(conversations.get(conversation_id, []))
         if summarized_text:
            new_default_messages = [
                {"role": "system", "content": "You are Romeo. IT Consortium's personal chatbot agent who responds to user queries concerning all questions they have about the company, our product, services and what we do. Play to your strength as an llm without any legal compromises. You may receive some sample information (starting with the key 'info:') together with its score (denoted by 'score:') about the question asked in order to add to your context and aid you in responding to the question. The higher the score the higher the relevance of the info"},
            ]
            update_conversation_history(conversation_id, summarized_text, new_default_messages, True)

def authenticate_user(request):
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

