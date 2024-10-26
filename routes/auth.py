from flask import Blueprint, request, jsonify

from services.jwt_service import JWTService


auth_bp = Blueprint("auth", __name__)
jwt_service = JWTService()


@auth_bp.route("/login", methods=["POST"])
def login():
    # TODO: handle actual authentication logic
    data = request.get_json()

    try:
        username = data["username"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required."}), 409

    token = jwt_service.generate_token(user_id=1)

    return jsonify({"logged_in": True, "token": token}), 200
