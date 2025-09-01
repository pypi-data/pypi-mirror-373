import os
from flask import Flask, request, jsonify, Blueprint
from werkzeug.utils import secure_filename
from flask import current_app as app

upload_file_bp = Blueprint('upload_file', __name__, url_prefix='/api/upload')


@upload_file_bp.route("", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    return jsonify({"file_path": filepath})