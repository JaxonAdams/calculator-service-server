import pymysql
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
            ops = db.fetch_records(
                "operation",
                fields=["id", "type", "cost"],
                conditions={"deleted": 0},
            )

        return jsonify({"results": ops}), 200
    elif request.method == "POST":
        data = request.get_json()
        try:
            op_type = data["type"]
            cost = data["cost"]
        except KeyError as e:
            return jsonify({"error": f"Field {e} is required"}), 400

        with DBService() as db:
            op_id = db.insert_record("operation", {"type": op_type, "cost": cost})

        return jsonify({"id": op_id, "type": op_type, "cost": cost}), 201


@operation_bp.route("/<int:operation_id>", methods=["GET", "PUT", "DELETE"])
@jwt_required
def manage_single_operation(operation_id):
    if request.method == "GET":
        with DBService() as db:
            ops = db.fetch_records(
                "operation",
                fields=["id", "type", "cost"],
                conditions={"id": operation_id},
            )

        try:
            return jsonify(ops[0]), 200
        except IndexError:
            return (
                jsonify({"error": f"Operation with ID {operation_id} not found"}),
                404,
            )
    elif request.method == "PUT":
        data = request.get_json()

        if not len(data):  # no fields provided
            return jsonify({"error": "You must specify a field to update."}), 400

        with DBService() as db:
            try:
                db.update_record(
                    "operation",
                    data,
                    operation_id,
                )
            except pymysql.MySQLError as e:
                return jsonify({"error": e.args[1]}), 400

            updated_ops = db.fetch_records(
                "operation",
                fields=["id", "type", "cost"],
                conditions={"deleted": 0, "id": operation_id},
            )

        return jsonify(updated_ops[0]), 200
    elif request.method == "DELETE":
        with DBService() as db:
            to_delete = db.fetch_records(
                "operation",
                conditions={"id": operation_id, "deleted": 0},
            )

            if not len(to_delete):
                return (
                    jsonify({"error": f"Operation with ID {operation_id} not found"}),
                    404,
                )

            try:
                db.update_record(
                    "operation",
                    {"deleted": 1},
                    operation_id,
                )
            except pymysql.MySQLError as e:
                return jsonify({"error": e.args[1]}), 400

            # check that it was properly deleted
            updated_ops = db.fetch_records(
                "operation",
                conditions={"id": operation_id},
            )

            try:
                if updated_ops[0]["deleted"] == 1:
                    return (
                        jsonify(
                            {
                                "message": f"Operation with ID {operation_id} was deleted."
                            }
                        ),
                        200,
                    )
                else:
                    return (
                        jsonify(
                            {
                                "error": f"Could not delete operation with ID {operation_id}."
                            }
                        ),
                        500,
                    )
            except KeyError:
                return jsonify({"error": "Unexpected error occurred."}), 500
