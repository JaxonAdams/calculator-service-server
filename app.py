from flask import Flask

from routes import Router

app = Flask(__name__)

router = Router(app)
router.init()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":

    app.run(debug=True)
