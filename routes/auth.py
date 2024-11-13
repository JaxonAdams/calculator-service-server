from bcrypt import checkpw
from flask import Blueprint, request, jsonify

from services.db_service import DBService
from services.jwt_service import JWTService


# Create a Blueprint for authentication routes. This blueprint will be registered
# later to make these routes available to the app.
auth_bp = Blueprint("auth", __name__)
jwt_service = JWTService()


@auth_bp.route("/login", methods=["POST"])
def login():
    """Handle user login.
    
    Expects a JSON payload with 'username' and 'password' fields.
    Returns a JSON response with a JWT token if authentication is successful.

    Returns:
        Response: JSON response with a JWT token if authentication is successful.
        Response: JSON response with an error message and appropriate status code
                  if authentication fails.
    """

    data = request.get_json()

    # Extract username and password from the request data
    try:
        username = data["username"]
        password = data["password"]
    except KeyError as e:
        return jsonify({"error": f"Field {e} is required."}), 409

    # Fetch the user from the database
    with DBService() as db:
        users = db.fetch_records(
            "user",
            conditions={"username": username},
        )

        # If the user doesn't exist, return a 404 Not Found response
        try:
            user = users[0]
        except IndexError:
            return jsonify({"error": f"User '{username}' not found"}), 404

    # Check if the password matches the hashed password in the database
    valid_pw = checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
    if not valid_pw:
        return jsonify({"error": "Invalid password"}), 401

    # Generate a JWT token and return it in the response
    token = jwt_service.generate_token(user_id=int(user["id"]))

    return jsonify({"logged_in": True, "token": token}), 200
