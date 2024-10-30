from bcrypt import checkpw
from flask import Blueprint, request, jsonify

from services.db_service import DBService
from services.jwt_service import JWTService


auth_bp = Blueprint("auth", __name__)
jwt_service = JWTService()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    try:
        username = data["username"]
        password = data["password"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required."}), 409

    with DBService() as db:
        users = db.fetch_records(
            "user",
            conditions={"username": username},
        )

        try:
            user = users[0]
        except IndexError:
            return jsonify({"error": f"User '{username}' not found"}), 404

    valid_pw = checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
    if not valid_pw:
        return jsonify({"error": "Invalid password"}), 401

    token = jwt_service.generate_token(user_id=int(user["id"]))

    return jsonify({"logged_in": True, "token": token}), 200
