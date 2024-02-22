from flask import current_app

from ..utils import chunking, formatter, write_to_file

def parse_text(text, size):
    current_app.logger.info("About to start parsing text")
    try:
        passages = chunking.transformer_based_chunking(text)
        formatted_chunks = formatter.split_flatten_and_join(passages, size)
        return formatted_chunks
    except Exception as e:
        current_app.logger.exception(f"An error occurred while parsing file(s): Error: {e}")
        raise Exception("An error occurred while parsing file(s)")

