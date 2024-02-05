from flask import Blueprint, render_template
from flask import request, jsonify, current_app
import traceback

from .utils.read_files import process_uploaded_file, process_file_content
from .utils.aws_helper import upload_file_to_s3, get_file_from_s3, list_files_in_folder
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

        split_size = int(request.form.get('split_size', 3))
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


@bp.route('/upload-s3', methods=["POST"])
def upload_to_s3():
    current_app.logger.info("Uploading file to s3 bucket ...")
    try:
        if 'data' not in request.files:
            return jsonify({"error": "No file part was sent"}), 400

        file = request.files['data']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        success, message = upload_file_to_s3(file)

        if (success == False):
            return jsonify({"failure": "An error occurred while uploading files to s3."}), 500
        else:
            return jsonify({"success": message}), 200
    except Exception as e:
        current_app.logger.exception(f"Error uploading file. Error: {e}")
        return jsonify({"error": "Error uploading file"}), 500

@bp.route('/index', methods=['POST'])
def index_file():
    current_app.logger.info("Received request to start indexing file(s)...")
    try:
        
        split_size = int(request.form.get('split_size', 3))
        index = request.form.get('index', "search-chatbot-final")
        file = request.form.get('file', "main-files")
        current_app.logger.info(f"Request payload is: {index, split_size}")
        
        success, file_contents_bytes = get_file_from_s3(file)
        if success == False:
            current_app.logger.info({"error": "An error occurred while downloading files from s3."})
            return jsonify({"error": "An error occurred while downloading files from s3."}), 500
        if file_contents_bytes:
            file_content = process_file_content(file_contents_bytes)
            chunks = parsing.parse_text(file_content, split_size)
            generated_embeddings = embeddings.perform_embedding(chunks)
            success = indexing.index_data(generated_embeddings, index)
            if success:
                current_app.logger.info("Data successfully uploaded and indexed")
                return jsonify({"success": "Data uploaded and indexed successfully"}), 200
            else:
                current_app.logger.error("An error occurred while uploading and indexing data")
                return jsonify({"failure": "Unable to index data due to unexpected error"}), 500
        else:
            current_app.logger.exception(f"An error occurred while getting files from bucket: {traceback.format_exc()}")
            return jsonify({"error": "Sorry, an error occurred while getting files from bucket"}), 500
    except Exception as e:
        current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
        return jsonify({"error": "Sorry, an error occurred while uploading data"}), 500


@bp.route("/get-files", methods=["GET"])
def get_files():
    current_app.logger.info("Getting files from s3 bucket")

    try:
        success, files = list_files_in_folder()
        if success == False:
            current_app.logger.error("There was an error while getting files")
            return jsonify({"error:": "An error occurred while getting files from s3."}), 500
        if (len(files) == 0):
            current_app.logger.exception(f"There was no file in s3 bucket: {traceback.format_exc()}")
            return jsonify({"error": "Sorry, there is currently no files in chatbot bucket in s3"}), 500
        current_app.logger.info("Successfully got files from s3 bucket")
        return jsonify({"success": "Got file from s3 bucket", "files": files}), 404
    except Exception as e:
        current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
        return jsonify({"error": "Sorry, an error occurred while getting files from s3"}), 500





