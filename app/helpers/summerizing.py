from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from flask import current_app

def summarize_conversation(conversation_array, max_length=2048, summary_model="sshleifer/distilbart-cnn-12-6"):
    current_app.logger.info("About to summarize conversation")
    """
    Summarize the conversation if it exceeds max_length.

    Args:
    - conversation_array (list of dict): Array of messages with 'role' and 'content'.
    - max_length (int): The length threshold to trigger summarization.
    - summary_model (str): Model used for summarization.

    Returns:
    - str: Original or summarized conversation.
    """
    # Concatenate the conversation
    concatenated_conversation = " ".join([msg["content"] for msg in conversation_array])

    # Check if conversation exceeds the max_length
    if len(concatenated_conversation) > max_length:
        # Initialize a summarization pipeline
        summarizer = pipeline("summarization", model=summary_model)

        # Summarize the conversation
        summary = summarizer(concatenated_conversation, max_length=300, min_length=30, do_sample=False)
        summarized_text = summary[0]['summary_text']
        current_app.logger.info(f"Conversation history is: {summarized_text}")
        return  {"role": "assistant", "content": "Your History: " + summarized_text}

    # If conversation does not exceed max_length, return it as is
    return False



def summarize_conversation_t5(conversation_array, max_length=2048, model_name="t5-base"):
    concatenated_conversation = " ".join([msg["content"] for msg in conversation_array])
    
    if len(concatenated_conversation) > max_length:
        tokenizer = T5Tokenizer.from_pretrained(model_name)
        model = T5ForConditionalGeneration.from_pretrained(model_name)

        inputs = tokenizer.encode("summarize: " + concatenated_conversation, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        current_app.logger.info(f"Summarized Conversation: {summary}")
        return {"role": "assistant", "content": "Your History: " + summary}
    
    return False

