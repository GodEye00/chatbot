import csv
import threading
from flask import current_app, copy_current_request_context

from ..utils import chunking, formatter, write_to_file

# docs_path_dir = '../utils/extracted_pages'
# texts = read_files.import_text_from_directory(docs_path_dir)

file_name = 'output'

def parse_text(text, size):
    current_app.logger.info("About to start parsing text")
    passages = chunking.transformer_based_chunking(text)
    formatted_chunks = formatter.split_flatten_and_join(passages, size)
    
    @copy_current_request_context
    def thread_function():
        write_to_file.write(formatted_chunks, 'csv', file_name, ['Passage'])

    # Start the thread to write to CSV, without waiting for it to finish
    thread = threading.Thread(target=thread_function)
    thread.start()

    return formatted_chunks

