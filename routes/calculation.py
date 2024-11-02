import json

import pymysql
from flask import Blueprint, jsonify, request

from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required


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

