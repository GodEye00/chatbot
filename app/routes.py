from flask import Flask, render_template, request, jsonify, Blueprint, current_app
from flask_wtf.csrf import generate_csrf
import traceback

from app.utils.Flask_form import IndexForm, S3UploadForm, UploadForm
from .utils.read_files import process_uploaded_file, process_file_content
from .utils.aws_helper import upload_file_to_s3, get_file_from_s3, list_files_in_folder
from .helpers import parsing, indexing, embeddings

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.data.data
        split_size = form.split_size.data
        index = form.index.data
        try:
            file_contents = process_uploaded_file(file)
            chunks = parsing.parse_text(file_contents, split_size)
            generated_embeddings = embeddings.perform_embedding(chunks)
            success = indexing.index_data(generated_embeddings, index)
            if success:
                return jsonify({"success": "Data uploaded and indexed successfully"}), 200
            else:
                return jsonify({"failure": "Unable to index data due to unexpected error"}), 500
        except Exception as e:
            current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
            return jsonify({"error": "Sorry, an error occurred while uploading data"}), 500
    else:
        return jsonify({"error": form.errors}), 400

@bp.route('/upload-s3', methods=["POST"])
def upload_to_s3():
    form = S3UploadForm()
    if form.validate_on_submit():
        file = form.data.data
        success, message = upload_file_to_s3(file)
        if not success:
            return jsonify({"failure": message}), 500
        return jsonify({"success": message}), 200
    else:
        return jsonify({"error": form.errors}), 400

@bp.route('/index', methods=['POST'])
def index_file():
    form = IndexForm()
    if form.validate_on_submit():
        split_size = form.split_size.data
        index = form.index.data
        file_name = form.file.data
        try:
            success, file_contents_bytes = get_file_from_s3(file_name)
            if not success:
                return jsonify({"error": "An error occurred while downloading files from s3."}), 500
            file_content = process_file_content(file_contents_bytes)
            chunks = parsing.parse_text(file_content, split_size)
            generated_embeddings = embeddings.perform_embedding(chunks)
            success = indexing.index_data(generated_embeddings, index)
            if success:
                return jsonify({"success": "Data uploaded and indexed successfully"}), 200
            else:
                return jsonify({"failure": "Unable to index data due to unexpected error"}), 500
        except Exception as e:
            current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
            return jsonify({"error": "Sorry, an error occurred while uploading data"}), 500
    else:
        return jsonify({"error": form.errors}), 400

@bp.route("/get-files", methods=["GET"])
def get_files():
    try:
        success, files = list_files_in_folder()
        if not success:
            return jsonify({"error": "An error occurred while getting files from s3."}), 500
        if len(files) == 0:
            return jsonify({"error": "Sorry, there is currently no files in chatbot bucket in s3"}), 404
        return jsonify({"success": "Got file from s3 bucket", "files": files}), 200
    except Exception as e:
        current_app.logger.exception(f"An error occurred: {traceback.format_exc()}")
        return jsonify({"error": "Sorry, an error occurred while getting files from s3"}), 500
    
    

@bp.route("/get-csrf-token", methods=["GET"])
def get_csrf_token():
    return jsonify({'csrf_token': generate_csrf()}), 200

