from openai import OpenAI
from flask import current_app
client = OpenAI()

def ask_gpt4(conversations):
    conversation_history = conversations
    current_app.logger.info("About to show conversation history")
    current_app.logger.info(conversation_history)
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            # model="ft:gpt-3.5-turbo-0613:it-consortium::7tEgnKPn",
            messages=conversation_history
        )
        response_text = response.choices[0].message.content
        response_to_send = {"role": "assistant", "content": response_text}
        return response_to_send
    except Exception as e:
        current_app.logger.error(f"Error in GPT-4 API call: {e}")
        return "I'm having trouble understanding that right now."
