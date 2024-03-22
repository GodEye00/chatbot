from cryptography.fernet import Fernet
from flask import current_app
import json

def get_cipher_suite(key=None):
    if key is None:
        key = current_app.config['REDIS_KEY']
    key_bytes = key.encode() if isinstance(key, str) else key
    return Fernet(key_bytes)


def save_encrypted_conversation(id, data, key=None):
    current_app.logger.info(f"Saving conversation with id: {id}")
    data_str = json.dumps(data)
    cipher_suite = get_cipher_suite(key)
    encrypted_data = cipher_suite.encrypt(data_str.encode())
    current_app.redis.setex(id, current_app.config['REDIS_EXPIRY'], encrypted_data)


def get_decrypted_conversation(prefix):
    conversations_dict = {}

    keys = current_app.redis.scan_iter(f"{prefix}*")
    for key in keys:
        key_str = key.decode('utf-8') if isinstance(key, bytes) else key

        suffix = key_str[len(prefix):].split('-')[1]
        encrypted_message = current_app.redis.get(key)
        if encrypted_message:
            cipher_suite = get_cipher_suite(current_app.config['REDIS_KEY'])
            decrypted_message = cipher_suite.decrypt(encrypted_message).decode()
            message_obj = json.loads(decrypted_message)

            if suffix in conversations_dict:
                conversations_dict[suffix].append(message_obj)
            else:
                conversations_dict[suffix] = message_obj
    current_app.logger.info(f"Conversation are: {conversations_dict}")
    return conversations_dict

def delete_conversation_from_cache(prefix):
    keys = current_app.redis.scan_iter(f"{prefix}*")
    for key in keys:
        current_app.redis.delete(key)
