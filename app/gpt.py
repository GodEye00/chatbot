from openai import OpenAI
import boto3
import json
import os
from flask import current_app
client = OpenAI()

def ask_openai(model, conversations):
    conversation_history = conversations
    current_app.logger.info(f"About to show conversation history in openai {conversation_history}")
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0.4,
            # model="ft:gpt-3.5-turbo-0613:it-consortium::7tEgnKPn",
            messages=conversation_history
        )
        response_text = response.choices[0].message.content
        response_to_send = {"role": "assistant", "content": response_text}
        return response_to_send
    except Exception as e:
        current_app.logger.error(f"Error in {model} GPT API call: {e}")
        raise Exception(f"Error in {model} GPT API call: {e}")


def ask_bedrock(model, conversations):
    conversation_history = conversations
    current_app.logger.info("About to show conversation history")
    current_app.logger.info(conversation_history)

    aws_access_key_id = current_app.config['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = current_app.config['AWS_SECRET_ACCESS_KEY']
    region_name = current_app.config['AWS_REGION']

    boto3.setup_default_session(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    brt = boto3.client(service_name='bedrock-runtime')
    
    prompt = replace_and_stringify(conversations)
    
    current_app.logger.info(f"About to show conversation history in bedrock {prompt}")


    body = json.dumps({
        'prompt': prompt,
        'max_tokens_to_sample': 100
    })

    try:
        response = brt.invoke_model_with_response_stream(
            modelId=model,
            body=body
        )
        response = {}
        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    response.update(json.loads(chunk.get('bytes').decode()))
        current_app.logger.info(f'Response from bedrock is: {response}')
        response_to_send = {"role": "assistant", "content": response}
        return response_to_send
    except Exception as e:
        current_app.logger.error(f"Error in {model} GPT API call: {e}")
        raise Exception(f"Error in {model} GPT API call: {e}")


# Function to replace specified keys
# def replace_keys(objects):
#     replacements = {'user': 'Human', 'assistant': 'Assistant'}
#     new_objects = [
#         {replacements.get(k, k): v for k, v in obj.items()} for obj in objects
#     ]

#     return new_objects

def replace_and_stringify(data):
    converted_data = []
    for item in data:
        role = 'Human' if isinstance(item, dict) and  item['role'] == 'user' else 'Assistant'
        content = item['content'].replace('user', 'Human').replace('system', 'Assistant').replace('assistant', 'Assistant') if isinstance(item, dict)  else item.replace('user', 'Human').replace('system', 'Assistant').replace('assistant', 'Assistant')
        converted_data.append(f'\n\n{role}: {content}')

    result = ''.join(converted_data)
    return result