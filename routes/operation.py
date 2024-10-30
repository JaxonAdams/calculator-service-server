from flask import Blueprint, jsonify

from services.db_service import DBService
from services.jwt_service import jwt_required


operation_bp = Blueprint("operation", __name__)


@operation_bp.route("", methods=["GET"])
@operation_bp.route("/", methods=["GET"])
@jwt_required
def manage_operations():
    with DBService() as db:
        ops = db.fetch_records("operation")

    return jsonify({"results": ops}), 200
