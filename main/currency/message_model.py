from flask import jsonify, request, session
from main.db import mongo
import uuid
from datetime import datetime


class Currency:
    def update(self, data):

        currency = {
            "_id": uuid.uuid4().hex,
            "date_update": datetime.now(),
            "data": data,
            "currency": "usd",
            "convertTo": "ils",
        }

        mongo.db.usd.insert_one(currency)
        return jsonify("message was sent"), 200
