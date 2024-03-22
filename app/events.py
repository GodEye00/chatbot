from celery import group, chord
from flask_socketio import emit, join_room
from flask import request, current_app
import re

from .app import socketio
from .services.tasks import retrieve_conversation_from_cache, retrieve_passages_task, process_and_emit, delete_conversation_from_cache



def authenticate_user(request):
    # TODO: implement authentication
    pass

def get_user_from_session():
    return request.sid

def validate_chat_data(json):
    required_fields = ['message']
    errors = []
    for field in required_fields:
        if field not in json or json.get(field) == None or json.get(field) == "":
            errors.append(f"{field} is required")
        else:
            if field in ['index'] and not isinstance(json[field], str):
                errors.append(f"{field} must be a string")
            if field in ['size'] and not isinstance(json[field], int):
                errors.append(f"{field} must be an integer")
    return errors



@socketio.on('connect')
def handle_connect():
    current_app.logger.info("Connected")
    user = authenticate_user(request)
    conversation_id = user.conversation_id if user else get_user_from_session()
    join_room(conversation_id)


from celery import group, chord

def initiate_retrieval_and_processing(conversation_id, index, size, user_message, models):
    tasks = [retrieve_conversation_from_cache.s(conversation_id)]

    if index:
        tasks.append(retrieve_passages_task.s(conversation_id, index, size, user_message))

    header = group(*tasks)

    callback = process_and_emit.s(conversation_id=conversation_id, user_message=user_message, models=models)

    chord(header)(callback)



@socketio.on('chat')
def handle_client_message(json):
    errors = validate_chat_data(json)
    if errors:
        emit('error', {'error': "Validation errors: " + ", ".join(errors)}, room=json.get('connection_id', ''))
        return
    current_app.logger.info(f"Got chat: {json}")
    conversation_id = get_user_from_session()
    user_message = json['message']
    models = json.get('models', ['gpt4'])
    index = json.get('index', '')
    if index:
        index =  'search-'+re.sub(r'[\s/]+', '-', index).strip().lower()
    size = json.get('size', 2)

    initiate_retrieval_and_processing(conversation_id, index, size, user_message, models)


@socketio.on('disconnect')
def handle_disconnect():
    user = get_user_from_session()
    if user:
        delete_conversation_from_cache.delay(user)
        current_app.logger.info(f"Deleted conversation for {user}")
