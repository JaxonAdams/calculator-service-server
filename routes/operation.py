import pymysql
from flask import Blueprint, jsonify, request

from services.db_service import DBService
from services.calculator_service import CalculatorService
from services.jwt_service import jwt_required, admin_protected


# Create a Blueprint for operation routes. This blueprint will be registered
# later to make these routes available to the app.
operation_bp = Blueprint("operation", __name__)


@operation_bp.route("", methods=["GET"])
@operation_bp.route("/", methods=["GET"])
@jwt_required
def get_operations():
    """Get a list of operations stored in the database.

    Returns:
        Response: JSON response with a list of operations and metadata.
    """

    # Handle pagination and filtering specified in the query parameters
    limit = int(request.args.get("page_size", 10))
    offset = (int(request.args.get("page", 1)) - 1) * limit

    filters = {}
    for param in ["type", "cost"]:  # filterable fields
        value = request.args.get(param)
        if value:
            filters[param] = value

    with DBService() as db:

        # Fetch operations from the database
        total_count = db.count_records(
            "operation",
            conditions={"deleted": 0} | filters,
        )

        ops = db.fetch_records(
            "operation",
            fields=["id", "type", "cost"],
            conditions={"deleted": 0} | filters,
            limit=limit,
            offset=offset,
        )

        # Fetch options/settings from the calculator for each operation
        ops_with_options = []
        for op in ops:
            ops_with_options.append(
                op | {
                    "options": CalculatorService().get_operation_options(op["id"])
                }
            )

    # Construct and return the response
    response = {
        "results": ops_with_options,
        "metadata": {
            "total": total_count,
            "page": offset // limit + 1,
            "page_size": limit,
        },
    }

    return jsonify(response), 200


@operation_bp.route("", methods=["POST"])
@operation_bp.route("/", methods=["POST"])
@admin_protected
def create_operation():
    """Create a new operation in the database.
    
    Please note that adding a new operation will also require an update to the
    calculator code. This route is provided for administrators to speed up the
    process of adding new operations to the app.

    Expects a JSON payload with 'type' and 'cost' fields.
    Returns a JSON response with the created operation.

    Returns:
        Response: JSON response with the created operation and a 201 Created status code.
        Response: JSON response with an error message and appropriate status code
                  if the request data is invalid.
    """

    data = request.get_json()

    # Extract operation type and cost from the request data
    try:
        op_type = data["type"]
        cost = data["cost"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required"}), 400

    # Insert the new operation into the database
    with DBService() as db:
        op_id = db.insert_record("operation", {"type": op_type, "cost": cost})

    return jsonify({"id": op_id, "type": op_type, "cost": cost}), 201


@operation_bp.route("/<int:operation_id>", methods=["GET"])
@jwt_required
def get_single_operation(operation_id):
    """Get a single operation by ID.
    
    Args:
        operation_id (int): The ID of the operation to retrieve.

    Returns:
        Response: JSON response with the operation details if found.
        Response: JSON response with an error message and a 404 Not Found status code
                  if the operation is not found.
    """

    # Fetch the operation from the database
    with DBService() as db:
        ops = db.fetch_records(
            "operation",
            fields=["id", "type", "cost"],
            conditions={"id": operation_id},
        )

    # Construct and return the response
    try:
        return jsonify(ops[0]), 200
    except IndexError:
        return (
            jsonify({"error": f"Operation with ID {operation_id} not found"}),
            404,
        )


@operation_bp.route("/<int:operation_id>", methods=["PUT"])
@admin_protected
def update_single_operation(operation_id):
    """Update a single operation by ID.
    
    This route is provided to administrators to simplify the task of
    updating an operation in the database, especially when the cost of
    the operation needs to change.

    Args:
        operation_id (int): The ID of the operation to update.
        
    Returns:
        Response: JSON response with the updated operation details if successful.
    """

    data = request.get_json()

    if not len(data):  # No fields provided
        return jsonify({"error": "You must specify a field to update."}), 400

    # Update the operation in the database
    with DBService() as db:
        try:
            db.update_record(
                "operation",
                data,
                operation_id,
            )
        except pymysql.MySQLError as e:
            return jsonify({"error": e.args[1]}), 400

        # Fetch the updated operation from the database
        updated_ops = db.fetch_records(
            "operation",
            fields=["id", "type", "cost"],
            conditions={"deleted": 0, "id": operation_id},
        )

    return jsonify(updated_ops[0]), 200


@operation_bp.route("/<int:operation_id>", methods=["DELETE"])
@admin_protected
def delete_operation(operation_id):
    """Delete a single operation by ID.
    
    Args:
        operation_id (int): The ID of the operation to delete.

    Returns:
        Response: JSON response with a success message if the operation was deleted.
        Response: JSON response with an error message and an appropriate status code
                  if the operation was not found or could not be deleted.
    """

    with DBService() as db:
        # Check if the operation exists
        to_delete = db.fetch_records(
            "operation",
            conditions={"id": operation_id, "deleted": 0},
        )

        if not len(to_delete):
            return (
                jsonify({"error": f"Operation with ID {operation_id} not found"}),
                404,
            )

        # Soft delete the operation
        try:
            db.update_record(
                "operation",
                {"deleted": 1},
                operation_id,
            )
        except pymysql.MySQLError as e:
            return jsonify({"error": e.args[1]}), 400

        # Check that it was properly deleted
        updated_ops = db.fetch_records(
            "operation",
            conditions={"id": operation_id},
        )

        # Construct and return the response
        try:
            if updated_ops[0]["deleted"] == 1:
                return (
                    jsonify(
                        {"message": f"Operation with ID {operation_id} was deleted."}
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {"error": f"Could not delete operation with ID {operation_id}."}
                    ),
                    500,
                )
        except KeyError:
            return jsonify({"error": "Unexpected error occurred."}), 500
