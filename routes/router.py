from routes.auth import auth_bp
from routes.operation import operation_bp
from routes.calculation import calculation_bp


class Router:

    def __init__(self, flask_app):

        self.flask_app = flask_app

    def init(self):
        # register routes

        # auth-related routes
        self.flask_app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")

        # resource routes
        self.flask_app.register_blueprint(operation_bp, url_prefix="/api/v1/operations")
        self.flask_app.register_blueprint(calculation_bp, url_prefix="/api/v1/calculations")
