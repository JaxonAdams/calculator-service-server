import json

import pymysql
from flask import Blueprint, jsonify, request

from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required, admin_protected
from services.calculator_service import CalculatorService


calculation_bp = Blueprint("calculation", __name__)


@calculation_bp.route("", methods=["GET"])
@calculation_bp.route("/", methods=["GET"])
@jwt_required
def get_calculation_history():
    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    limit = int(request.args.get("page_size", 10))
    offset = (int(request.args.get("page", 1)) - 1) * limit

    date_format = "%Y-%m-%d %H:%i:%s"

    operation_type = request.args.get("operation_type")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

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

    get_history_count_sql = f"""
    SELECT
        COUNT(*) AS total
    FROM record r
    LEFT JOIN operation o ON o.id = r.operation_id
    LEFT JOIN user u ON u.id = r.user_id
    {where_clause}
    LIMIT 1;
    """

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

    user_history = []
    for result in results:
        history_item = dict(result)  # making a copy, not modifying in-place

        # apply additional formatting for certain fields
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

    data = request.get_json()

    try:
        op_type = data["operation"]
        operands = data["operands"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required"}), 400

    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    user_balance_sql = f"""
    SELECT
        IFNULL(r.user_balance, 0) AS 'balance'
    FROM user u
    LEFT JOIN record r ON u.id = r.user_id
    WHERE u.id = {user_id} AND r.deleted = 0
    ORDER BY r.`date` DESC;
    """

    with DBService() as db:

        try:
            user_balance = db.execute_query(user_balance_sql)[0]["balance"]
        except pymysql.MySQLError as e:
            return jsonify({"error": f"{e.args[1]}"})

        try:
            op_info = db.fetch_records("operation", conditions={"type": op_type})[0]
        except IndexError:
            return jsonify({"error": f"Operation '{op_type}' not known"}), 400

        new_user_balance = round(float(user_balance) - float(op_info["cost"]), 2)
        if new_user_balance <= 0:
            return jsonify({"error": "Insufficient funds"}), 402

        try:
            result = CalculatorService().calculate(op_info["id"], operands)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except NotImplementedError as e:
            return jsonify({"error": str(e)}), 500

        response_data = {
            "operation": op_type,
            "operands": operands,
            "result": result,
        }

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
    with DBService() as db:
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

        if not to_delete or not len(to_delete):
            return (
                jsonify(
                    {"error": f"Calculation record with ID '{record_id}' not found"}
                ),
                404,
            )

        try:
            new_user_balance = to_delete[0]["user_balance"] + to_delete[0]["cost"]
            db.update_record(
                "record",
                {"deleted": 1},
                record_id,
            )

            remaining_tx_sql = f"""
            SELECT
                r.id   AS id,
                o.cost AS cost
            FROM record r
            JOIN operation o ON o.id = r.operation_id
            WHERE r.id > {record_id}
            """

            to_update = db.execute_query(remaining_tx_sql)
            prev_balance = new_user_balance

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

        updated_records = db.fetch_records(
            "record",
            conditions={"id": record_id},
        )

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
