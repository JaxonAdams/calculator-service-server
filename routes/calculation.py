import json

import pymysql
from flask import Blueprint, jsonify, request

from config import USER_STARTING_BALANCE
from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required, admin_protected
from services.calculator_service import CalculatorService


# Create a Blueprint for calculation routes. This blueprint will be registered
# later to make these routes available to the app.
calculation_bp = Blueprint("calculation", __name__)


@calculation_bp.route("", methods=["GET"])
@calculation_bp.route("/", methods=["GET"])
@jwt_required
def get_calculation_history():
    """Retrieve the calculation history for the authenticated user.
    
    This endpoint requires a valid user JWT token in the Authorization header.
    Supports filtering by operation type, start date, and end date.
    Supports pagination with 'page' and 'page_size' query parameters.

    Returns:
        Response: JSON response with the calculation history for the authenticated user.
    """

    # Extract the user ID from the provided JWT token
    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    # Extract query parameters for filtering and pagination
    limit = int(request.args.get("page_size", 10))
    offset = (int(request.args.get("page", 1)) - 1) * limit

    operation_type = request.args.get("operation_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    # Prepare the SQL query to retrieve the calculation history
    where_clause = "WHERE u.id = %s AND r.deleted = 0"
    filters = [user_id]

    if operation_type:
        where_clause += " AND o.`type` = %s"
        filters.append(operation_type)

    if start_date:
        where_clause += " AND r.`date` >= %s"
        filters.append(start_date)

    if end_date:
        where_clause += " AND r.`date` <= %s"
        filters.append(end_date)

    # Return dates from the database in this format:
    date_format = "%Y-%m-%d %H:%i:%s"

    # Query for fetching the user's calculation history
    get_history_sql = f"""
    SELECT
        r.id                      AS 'id',
        o.id                      AS 'operation_id',
        o.`type`                  AS 'operation_type',
        o.cost                    AS 'operation_cost',
        u.id                      AS 'user_id',
        u.username                AS 'username',
        u.status                  AS 'user_status',
        r.user_balance            AS 'user_balance',
        r.operation_response      AS 'calculation',
        DATE_FORMAT(r.`date`, %s) AS 'date'
    FROM record r
    LEFT JOIN operation o ON o.id = r.operation_id
    LEFT JOIN user u ON u.id = r.user_id
    {where_clause}
    ORDER BY r.`date` DESC
    LIMIT %s
    OFFSET %s;
    """

    # Query for fetching the total count of the user's calculation history
    get_history_count_sql = f"""
    SELECT
        COUNT(*) AS total
    FROM record r
    LEFT JOIN operation o ON o.id = r.operation_id
    LEFT JOIN user u ON u.id = r.user_id
    {where_clause}
    LIMIT 1;
    """

    # Fetch the calculation history and total count from the database
    try:
        with DBService() as db:
            total_count_results = db.execute_query(
                get_history_count_sql,
                tuple(filters),
            )
            total_count = total_count_results[0]["total"]

            results = db.execute_query(
                get_history_sql,
                tuple([date_format] + filters + [limit, offset]),
            )
    except pymysql.MySQLError as e:
        return jsonify({"error": f"{e.args[1]}"})

    # Format the results for the response
    user_history = []
    for result in results:
        history_item = dict(result)  # making a copy, not modifying in-place

        # Apply additional formatting for certain fields
        del history_item["operation_id"]
        del history_item["operation_type"]
        del history_item["operation_cost"]
        del history_item["user_id"]
        del history_item["username"]
        del history_item["user_status"]
        del history_item["calculation"]

        history_item["operation"] = {
            "id": result["operation_id"],
            "type": result["operation_type"],
            "cost": result["operation_cost"],
        }

        history_item["user"] = {
            "id": result["user_id"],
            "username": result["username"],
            "status": result["user_status"],
        }

        history_item["calculation"] = json.loads(result["calculation"])

        user_history.append(history_item)

    # Construct the response with the calculation history and metadata

    response = {
        "results": user_history,
        "metadata": {
            "total": total_count,
            "page": offset // limit + 1,
            "page_size": limit,
        },
    }

    return jsonify(response), 200


@calculation_bp.route("/new", methods=["POST"])
@jwt_required
def run_calculation():
    """Run a calculation operation for the authenticated user.
    
    Expects a JSON payload with 'operation' and 'operands' fields.
    Returns a JSON response with the calculation result and updated user balance.

    Returns:
        Response: JSON response with the calculation result and updated user balance.
        Response: JSON response with an error message and appropriate status code
                  if the operation is not known or the user has insufficient funds
    """

    data = request.get_json()

    # Extract the operation type and operands from the request data
    try:
        op_type = data["operation"]
        operands = data["operands"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required"}), 400

    # Extract the user ID from the provided JWT token
    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    # Query to fetch the user's balance from the database
    user_balance_sql = f"""
    SELECT
        IFNULL(r.user_balance, 0) AS 'balance'
    FROM user u
    LEFT JOIN record r ON u.id = r.user_id
    WHERE u.id = {user_id} AND r.deleted = 0
    ORDER BY r.`date` DESC;
    """

    with DBService() as db:

        # Fetch the user's balance from the database
        try:
            user_balance = db.execute_query(user_balance_sql)[0]["balance"]
        except pymysql.MySQLError as e:
            return jsonify({"error": f"{e.args[1]}"})
        except IndexError:
            user_balance = USER_STARTING_BALANCE

        # Fetch the operation details from the database
        try:
            op_info = db.fetch_records("operation", conditions={"type": op_type})[0]
        except IndexError:
            return jsonify({"error": f"Operation '{op_type}' not known"}), 400

        # Calculate the new user balance after the operation
        new_user_balance = round(float(user_balance) - float(op_info["cost"]), 2)
        # Check if the user has sufficient funds for the operation
        if new_user_balance <= 0:
            return jsonify({"error": "Insufficient funds"}), 402

        # Perform the calculation operation
        try:
            result = CalculatorService().calculate(op_info["id"], operands)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except NotImplementedError as e:
            return jsonify({"error": str(e)}), 500

        # Construct the response data with the operation details and result
        response_data = {
            "operation": op_type,
            "operands": operands,
            "result": result,
        }

        # Store the calculation record in the database
        db.insert_record(
            "record",
            {
                "operation_id": op_info["id"],
                "user_id": user_id,
                "amount": 1,
                "user_balance": new_user_balance,
                "operation_response": json.dumps(response_data),
            },
        )

    return jsonify(response_data), 200


@calculation_bp.route("/<int:record_id>", methods=["DELETE"])
@admin_protected
def delete_record(record_id):
    """Delete a calculation record by ID.
    
    This endpoint requires a valid admin JWT token in the Authorization header.
    Returns a JSON response with a message if the record was deleted successfully.

    Args:
        record_id (int): The ID of the calculation record to delete.
    
    Returns:
        Response: JSON response with a message if the record was deleted successfully.
        Response: JSON response with an error message and appropriate status code
                  if the record was not found or could not be deleted.
    """

    with DBService() as db:

        # Fetch the calculation record to delete
        to_delete = db.fetch_records(
            "record",
            join=[
                {
                    "table": "operation",
                    "left": "operation.id",
                    "right": "record.operation_id",
                }
            ],
            conditions={"record.id": record_id, "record.deleted": 0},
        )

        # If the record was not found, return a 404 Not Found response
        if not to_delete or not len(to_delete):
            return (
                jsonify(
                    {"error": f"Calculation record with ID '{record_id}' not found"}
                ),
                404,
            )

        # Calculate the new user balance after deleting the record
        try:
            new_user_balance = to_delete[0]["user_balance"] + to_delete[0]["cost"]
            db.update_record(
                "record",
                {"deleted": 1},
                record_id,
            )

            # We need to update the user balance on all subsequent records
            remaining_tx_sql = f"""
            SELECT
                r.id   AS id,
                o.cost AS cost
            FROM record r
            JOIN user u ON u.id = r.user_id
            JOIN operation o ON o.id = r.operation_id
            WHERE r.id > {record_id} AND u.id = {to_delete[0]['user_id']}  AND r.deleted = 0
            """

            to_update = db.execute_query(remaining_tx_sql)
            prev_balance = new_user_balance

            # Update the user balance on all subsequent records
            if to_update:
                for tx in to_update:
                    db.update_record(
                        "record",
                        {"user_balance": prev_balance - tx["cost"]},
                        tx["id"],
                    )

                    prev_balance -= tx["cost"]

        except pymysql.MySQLError as e:
            return jsonify({"error": e.args[1]}), 400

        # Check if the record was successfully deleted
        updated_records = db.fetch_records(
            "record",
            conditions={"id": record_id},
        )

        # Return a response based on the deletion result
        try:
            if updated_records[0]["deleted"] == 1:
                return (
                    jsonify(
                        {
                            "message": f"Calculation record with ID {record_id} was deleted."
                        }
                    ),
                    200,
                )
            else:
                return (
                    jsonify(
                        {
                            "error": f"Could not delete calculation record with ID {record_id}."
                        }
                    ),
                    500,
                )
        except KeyError:
            return jsonify({"error": "Unexpected error occurred."}), 500
