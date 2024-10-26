from routes.auth import auth_bp


class Router:

    def __init__(self, flask_app):

        self.flask_app = flask_app

    def init(self):
        # register routes

        # auth-related routes
        self.flask_app.register_blueprint(auth_bp, url_prefix="/auth")
