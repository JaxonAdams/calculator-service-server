from flask import Blueprint, request, jsonify


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    # TODO: handle actual authentication logic
    data = request.get_json()

    try:
        username = data["username"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required."}), 409

    return jsonify({"logged_in": True, "username": username}), 200
