from flask import Blueprint, jsonify

progress = Blueprint("progress", __name__)

@progress.route("/progress", methods=["GET"])
def get_progress():
    return jsonify({"message": "Progress route placeholder"})
