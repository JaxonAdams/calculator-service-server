import json

import pymysql
from flask import Blueprint, jsonify, request

from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required
from services.calculator_service import CalculatorService


calculation_bp = Blueprint("calculation", __name__)


@calculation_bp.route("", methods=["GET"])
@calculation_bp.route("/", methods=["GET"])
@jwt_required
def get_calculation_history():
    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    date_format = "%Y-%m-%d %H:%i:%s"

    get_history_sql = """
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
    WHERE u.id = %s
    ORDER BY r.`date` DESC;
    """

    try:
        with DBService() as db:
            results = db.execute_query(get_history_sql, (date_format, user_id))
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

    return jsonify({"results": user_history}), 200


@calculation_bp.route("/new", methods=["POST"])
@jwt_required
def run_calculation():

    data = request.get_json()

    try:
        op_type = data["operation"]
        operands = data["operands"]
    except KeyError as e:
        return jsonify({"error": f"Field '{e}' is required"}), 400

    user_token = request.headers["Authorization"].split(" ")[1]
    user_id = JWTService().verify_token(user_token)["user_id"]

    user_balance_sql = f"""
    SELECT
        IFNULL(r.user_balance, 0) AS 'balance'
    FROM user u
    LEFT JOIN record r ON u.id = r.user_id
    WHERE u.id = {user_id}
    ORDER BY r.`date` DESC;
    """

    with DBService() as db:

        try:
            user_balance = db.execute_query(user_balance_sql)[0]["balance"]
        except pymysql.MySQLError as e:
            return jsonify({"error": f"{e.args[1]}"})

        if float(user_balance) <= 0:
            return jsonify({"error": "Insufficient funds"}), 402

        try:
            op_info = db.fetch_records("operation", conditions={"type": op_type})[0]
        except IndexError:
            return jsonify({"error": f"Operation '{op_type}' not known"}), 400

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
                "user_balance": user_balance,  # TODO: DECREMENT BALANCE!!
                "operation_response": json.dumps(response_data),
            }
        )

    return jsonify(response_data), 200
