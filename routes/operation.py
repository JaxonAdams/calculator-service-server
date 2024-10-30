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


@operation_bp.route("/<int:operation_id>", methods=["GET"])
@jwt_required
def manage_single_operation(operation_id):
    with DBService() as db:
        ops = db.fetch_records(
            "operation",
            conditions={"id": operation_id},
        )

    try:
        return jsonify(ops[0]), 200
    except IndexError:
        return jsonify({"error": f"Operation with ID {operation_id} not found"}), 404
