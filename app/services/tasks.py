from celery.exceptions import MaxRetriesExceededError
from flask import current_app
from ..utils import aws, read_files, write_to_file, redis
from ..helpers import embeddings, indexing, parsing, model, summerizing, retrieval
from ..app import celery, socketio
from ..gpt import ask_bedrock, ask_openai


@celery.task(bind=True)
def process_and_index_file(self, data):
    try:
        file_name = data['file']
        split_size = int(data['split_size'])
        index = data['index']

        # Attempting to get file content from S3
        success, file_contents_bytes = aws.get_file_from_s3(file_name)
        if not success:
            raise Exception("Failed to download file from S3")

        file_content = read_files.process_file_content(file_contents_bytes, file_name)
        if not file_content:
            return {'current': 0, 'total': 0, 'status': 'Task not started', 'result': 'No text to index'}
        chunks = parsing.parse_text(file_content, split_size)

        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks, start=1):
            generated_embeddings = embeddings.perform_embedding_single(chunk)
            success = indexing.index_data_append(generated_embeddings, index)
            if not success:
                current_app.logger.error("Failed to index data")

            self.update_state(state='PROGRESS', meta={'current': i, 'total': total_chunks, 'status': 'Processing'})

        return {'current': 100, 'total': 100, 'status': 'Task completed', 'result': 'Successfully indexed data'}
    except Exception as e:
        current_app.logger.exception(f"An error occurred while processing and indexing file. Error: {e}")
        self.update_state(state='FAILURE', meta={'status': 'Error'})


@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def bulk_process_and_index_file(self, data):
    try:
        file_name = data['file']
        split_size = int(data['split_size'])
        index = data['index']

        # Start progress update
        self.update_state(state='STARTED', meta={'current': 0, 'total': 100, 'status': 'Downloading file'})

        # Attempt to get file content from S3
        success, file_contents_bytes = aws.get_file_from_s3(file_name)
        if not success:
            raise Exception("Failed to download file from S3")
        
        # File downloaded progress update
        self.update_state(state='PROGRESS', meta={'current': 20, 'total': 100, 'status': 'Processing file'})
        
        file_content = read_files.process_file_content(file_contents_bytes, file_name)
        chunks = parsing.parse_text(file_content, split_size)

        # Processed file progress update
        self.update_state(state='PROGRESS', meta={'current': 40, 'total': 100, 'status': 'Embedding and indexing'})

        # Since these are bulk operations, perform them outside the loop
        generated_embeddings = embeddings.perform_embedding(chunks)
        success = indexing.index_data(generated_embeddings, index)

        if not success:
            raise Exception("Failed to index data")

        # Final progress update
        return {'current': 100, 'total': 100, 'status': 'Task completed', 'result': 42}
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            self.update_state(state='FAILURE', meta={'status': 'Error'})
            raise Exception("Max retries exceeded for task") from e



@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def write_file(self, file_data, ext, file_name, headers=None):
    try:
        write_to_file.write(file_data, ext, file_name, headers=headers)
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            return self.update_state(state='FAILURE', meta={'exc': str(e)})


@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def retrieve_passages_task(self, conversation_id, index, size, user_message):
    try:
        return retrieval.retrievePassages(index, size, [user_message])
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            socketio.emit('error', {'error': "An error occurred while retrieving passages"}, room=conversation_id)
            raise Exception("Max retries exceeded for task retrieve_passages_task") from e



@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def process_message_with_model(self, user_conversations, conversation_id, model_name):
    """
    Task to process a message with a specified model.
    """
    try:
        def switcher(model):
            if model == 'gpt4':
                return ask_openai("gpt-4", user_conversations)
            elif model == "gpt3.5":
                return ask_openai("gpt-3.5-turbo", user_conversations)
            elif model == "anthropic":
                return ask_bedrock("anthropic.claude-v2", user_conversations)
            else:
                return  "Model not supported"

        response = switcher(model_name)
        conversations = user_conversations + [response]
        # Emit that the model has finished processing ("not typing")
        socketio.emit('typing_indicator', {'status': False, 'model': model_name}, room=conversation_id)

        # Emit the response from the model
        socketio.emit('model_response', {'model': model_name, 'content': response}, room=conversation_id)

        update_conversation_history_task.apply_async(args=[conversations, conversation_id, response, True, model_name])

        return response
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            socketio.emit('error', {'model': model_name, 'error': "An error occurred fetching message from model "}, room=conversation_id)
            raise Exception("Max retries exceeded for task process_message_with_model") from e


@celery.task(bind=True)
def update_conversation_history_task(self, conversations, conversation_id, message=None, summary=False, model_name=None):
    """
    Task to update conversation history, optionally including the model name.
    """
    # Logic to append message to conversation history
    if message:
        conversations = conversations or [] + [message]
    # If summary is requested, generate and append a summary message
    if summary:
        conversations = summerizing.summary('t5', conversations)
    # If model is provided store conversation history in cache
    if model_name:
        set_conversation_to_cache.apply_async(args=[f"{conversation_id}-{model_name}", conversations])


@celery.task()
def process_and_emit(results, conversation_id, user_message, models):

    for model_name in models:

        conversation, [chunks, retrieved_passage] = results

        socketio.emit(f'chunks_retrieved', {'chunks': chunks}, room=conversation_id)

        user_conversations = conversation.get(model_name, model.default_messages)

        combined_message = f"{user_message}. Context: {retrieved_passage}"
        message = {"role": "user", "content": combined_message }

        user_conversations = user_conversations + [message]

        update_conversation_history_task.apply_async(args=[user_conversations, conversation_id])

        socketio.emit('typing_indicator', {'status': True, 'model': model_name}, room=conversation_id)

        process_message_with_model.apply_async(args=[user_conversations, conversation_id, model_name])


@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def retrieve_conversation_from_cache(self, conversation_id):
    try:
        return redis.get_decrypted_conversation(conversation_id)
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            socketio.emit('error', {'error': "An error occurred while retrieving conversation from cache"}, room=conversation_id)
            raise Exception("Max retries exceeded for task retrieve_conversation_from_cache") from e

@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def set_conversation_to_cache(self, conversation_id, message):
    try:
        return redis.save_encrypted_conversation(conversation_id, message)
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            socketio.emit('error', {'error': "An error occurred while setting conversation to cache"}, room=conversation_id)
            raise Exception("Max retries exceeded for task set_conversation_to_cache") from e

@celery.task(bind=True, max_retries=3, default_retry_delay=5)
def delete_conversation_from_cache(self, conversation_id):
    try:
        return redis.delete_conversation_from_cache(conversation_id)
    except Exception as e:
        try:
            self.retry(exc=e)
        except MaxRetriesExceededError:
            socketio.emit('error', {'error': "An error occurred while deleting conversation from cache"}, room=conversation_id)
            raise Exception("Max retries exceeded for task delete_conversation_from_cache") from e




# @celery.task(bind=True)
# def summarize_conversation_task(self, conversation_id):
#     """
#     Task to summarize the conversation and update the conversation history.
#     """
#     if conversation_id in conversations:
#         conversation_history = conversations[conversation_id]
#         summarized_text = summarize_conversation_t5(conversation_history)
#         if summarized_text:
#             summary_message = {"role": "system", "content": summarized_text}
#             # Update the conversation with the summary message
#             conversations[conversation_id].append(summary_message)
#             # Emit the summary message to the client
#             emit('conversation_summary', {'message': summarized_text}, room=conversation_id)


