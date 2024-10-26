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

    # TODO: handle actual authentication logic
    with DBService() as db:
        pass

    token = jwt_service.generate_token(user_id=1)

    return jsonify({"logged_in": True, "token": token}), 200
