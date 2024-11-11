import os

from flask_cors import CORS
from flask import Flask, jsonify

from routes import Router

app = Flask(__name__)

cors_origins_str = os.environ.get("CORS_ORIGINS")
if cors_origins_str:
    cors_origins = cors_origins_str.split(",")
else:
    cors_origins = ["*"]

CORS(
    app,
    origins=cors_origins,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
)

router = Router(app)
router.init()


@app.errorhandler(401)
def unauthorized_error(error):
    return jsonify({"error": "Unauthorized"}), 401


@app.errorhandler(403)
def forbidden_error(error):
    return jsonify({"error": "Forbidden"}), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not Found"}), 404


@app.errorhandler(409)
def invalid_request(error):
    return jsonify({"error": "Invalid or Malformed Request"}), 409


@app.errorhandler(415)
def media_not_supported_error(error):
    return jsonify({"error": "Unsupported Media Type"}), 415


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":

    app.run(debug=True)
