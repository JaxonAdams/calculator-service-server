from flask import Blueprint, jsonify

from config import USER_STARTING_BALANCE
from services.db_service import DBService
from services.jwt_service import jwt_required


user_bp = Blueprint("user", __name__)


@user_bp.route("/<int:user_id>/balance")
@jwt_required
def get_user_balance(user_id):

    with DBService() as db:
        last_calculation = db.fetch_records(
            "record",
            conditions={"user_id": user_id, "deleted": 0},
            limit=1,
            order_by="`date` DESC",
        )[0]

    if not last_calculation:
        return jsonify({"balance": USER_STARTING_BALANCE}), 200

    return jsonify({"balance": last_calculation["user_balance"]}), 200
