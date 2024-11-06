from flask import Blueprint, jsonify, request

from config import USER_STARTING_BALANCE
from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required


user_bp = Blueprint("user", __name__)


@user_bp.route("/balance")
@jwt_required
def get_user_balance_using_jwt():

    token = request.headers["Authorization"].split(" ")[1]
    decoded = JWTService().verify_token(token)
    user_id = int(decoded["user_id"])

    with DBService() as db:
        last_calculation = db.fetch_records(
            "record",
            conditions={"user_id": user_id, "deleted": 0},
            limit=1,
            order_by="`date` DESC",
        )

        if not last_calculation:
            return jsonify({"balance": USER_STARTING_BALANCE}), 200

    return jsonify({"balance": last_calculation[0]["user_balance"]}), 200


@user_bp.route("/<int:user_id>/balance")
@jwt_required
def get_user_balance(user_id):

    with DBService() as db:
        last_calculation = db.fetch_records(
            "record",
            conditions={"user_id": user_id, "deleted": 0},
            limit=1,
            order_by="`date` DESC",
        )

        if not last_calculation:
            user = db.fetch_records(
                "user",
                conditions={"id": user_id, "status": "active"},
            )

            if not user:
                return jsonify({"error": f"User with ID {user_id} not found"}), 404

            return jsonify({"balance": USER_STARTING_BALANCE}), 200

    return jsonify({"balance": last_calculation[0]["user_balance"]}), 200
