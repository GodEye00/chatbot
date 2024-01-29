from flask import Blueprint, render_template
from flask import request, jsonify, current_app
import traceback

from .utils.read_files import process_uploaded_file
from .helpers import parsing, indexing, embeddings

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')



@bp.route('/upload', methods=['POST'])
def upload_file():
    current_app.logger.info("Received request to start processing uploaded data...")
    try:
        if 'data' not in request.files:
            return jsonify({"error": "No file part was sent"}), 400

        file = request.files['data']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        split_size = request.form.get('split_size', 3)
        split_size = int(split_size)
        index = request.form.get('index', "search-chatbot-final")
        current_app.logger.info(f"Request payload is: {index, split_size}")
        file_contents = process_uploaded_file(file)
        chunks = parsing.parse_text(file_contents, split_size)
        generated_embeddings = embeddings.perform_embedding(chunks)
        success = indexing.index_data(generated_embeddings, index)
        if success:
            current_app.logger.info("Data successfully uploaded and indexed")
            return jsonify({"success": "Data uploaded and indexed successfully"}), 200
        else:
            current_app.logger.error("An error occurred while uploading and indexing data")
            return jsonify({"failure": "Unable to index data due to unexpected error"}), 500
    except Exception as e:
        current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
        return jsonify({"error": "Sorry, an error occurred while uploading data"}), 500




