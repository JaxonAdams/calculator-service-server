from flask import Blueprint, jsonify, request

from services.db_service import DBService
from services.jwt_service import jwt_required


operation_bp = Blueprint("operation", __name__)


@operation_bp.route("", methods=["GET", "POST"])
@operation_bp.route("/", methods=["GET", "POST"])
@jwt_required
def manage_operations():
    if request.method == "GET":
        with DBService() as db:
            ops = db.fetch_records("operation")

        return jsonify({"results": ops}), 200
    elif request.method == "POST":
        data = request.get_json()
        try:
            op_type = data["type"]
            cost = data["cost"]
        except KeyError as e:
            return jsonify({"error": f"Field '{e}' is required"}), 400

        with DBService() as db:
            op_id = db.insert_record("operation", {"type": op_type, "cost": cost})

        return jsonify({"id": op_id, "type": op_type, "cost": cost}), 201


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
