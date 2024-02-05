from openai import OpenAI
import boto3
import json
import os
from flask import current_app
client = OpenAI()

def ask_gpt4(conversations):
    conversation_history = conversations
    current_app.logger.info("About to show conversation history")
    current_app.logger.info(conversation_history)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            temperature=0.4,
            # model="ft:gpt-3.5-turbo-0613:it-consortium::7tEgnKPn",
            messages=conversation_history
        )
        response_text = response.choices[0].message.content
        response_to_send = {"role": "assistant", "content": response_text}
        return response_to_send
    except Exception as e:
        current_app.logger.error(f"Error in GPT-4 API call: {e}")
        return "I'm having trouble understanding that right now."


def ask_bedrock(conversations):
    conversation_history = conversations
    current_app.logger.info("About to show conversation history")
    current_app.logger.info(conversation_history)

    aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region_name = os.getenv('AWS_REGION')

    boto3.setup_default_session(
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key
    )

    brt = boto3.client(service_name='bedrock-runtime')

    body = json.dumps({
        'prompt': '\n\nHuman: write an essay for living on mars in 1000 words\n\nAssistant:',
        'max_tokens_to_sample': 100
    })

    try:
        response = brt.invoke_model_with_response_stream(
            modelId='anthropic.claude-v2',
            body=body
        )

        stream = response.get('body')
        if stream:
            for event in stream:
                chunk = event.get('chunk')
                if chunk:
                    return json.loads(chunk.get('bytes').decode())
    except Exception as e:
        print(f"Error invoking model: {e}")
        return None


# Function to replace specified keys
def replace_keys(objects):
    replacements = {'user': 'Human', 'assistant': 'Assistant'}
    new_objects = [
        {replacements.get(k, k): v for k, v in obj.items()} for obj in objects
    ]

    return new_objects
