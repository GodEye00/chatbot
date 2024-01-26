from openai import OpenAI
client = OpenAI()

def ask_gpt4(conversations):
    conversation_history = conversations
    print("About to show conversation history")
    print(conversation_history)
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
        print(f"Error in GPT-4 API call: {e}")
        return "I'm having trouble understanding that right now."
