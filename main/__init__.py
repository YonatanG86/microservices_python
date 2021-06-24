
from flask import Flask
from main.db import mongo
from main.currency.view import currency


def create_app():

    app = Flask(__name__)
    app.config.from_object('config')
    mongo.init_app(app)

    app.register_blueprint(currency)

    return app
