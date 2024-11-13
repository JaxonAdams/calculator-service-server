from flask import Blueprint, jsonify, request

from config import USER_STARTING_BALANCE
from services.db_service import DBService
from services.jwt_service import JWTService, jwt_required, admin_protected


# Create a Blueprint for user-related routes. This blueprint will be registered
# later to make these routes available to the app.
user_bp = Blueprint("user", __name__)


@user_bp.route("/balance")
@jwt_required
def get_user_balance_using_jwt():
    """Get the current balance of the user making the request.

    Note that this balance can also be retrieved from the last calculation record.
    This route is provided as a simpler way of getting the user's balance.
    
    Returns:
        Response: JSON response with the user's balance.
    """

    # Extract the user ID from the JWT token
    token = request.headers["Authorization"].split(" ")[1]
    decoded = JWTService().verify_token(token)
    user_id = int(decoded["user_id"])

    with DBService() as db:
        # Fetch the last calculation record for the user
        last_calculation = db.fetch_records(
            "record",
            conditions={"user_id": user_id, "deleted": 0},
            limit=1,
            order_by="`date` DESC",
        )

        # If no calculation record is found, return the starting balance
        if not last_calculation:
            return jsonify({"balance": USER_STARTING_BALANCE}), 200

    return jsonify({"balance": last_calculation[0]["user_balance"]}), 200


@user_bp.route("/<int:user_id>/balance")
@admin_protected
def get_user_balance(user_id):
    """Get the current balance of the specified user.

    This differs from the route above in that it allows an admin to get the balance
    of any user by providing the user's ID in the URL.
    
    Args:
        user_id (int): The ID of the user whose balance is to be retrieved.
    
    Returns:
        Response: JSON response with the user's balance.
    """

    with DBService() as db:
        # Fetch the last calculation record for the user
        last_calculation = db.fetch_records(
            "record",
            conditions={"user_id": user_id, "deleted": 0},
            limit=1,
            order_by="`date` DESC",
        )

        # If no calculation record is found, return the starting balance
        if not last_calculation:
            user = db.fetch_records(
                "user",
                conditions={"id": user_id, "status": "active"},
            )

            # If the user doesn't exist or is not active, return a 404 Not Found response
            if not user:
                return jsonify({"error": f"User with ID {user_id} not found"}), 404

            return jsonify({"balance": USER_STARTING_BALANCE}), 200

    return jsonify({"balance": last_calculation[0]["user_balance"]}), 200
