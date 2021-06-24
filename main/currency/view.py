from flask import Blueprint
import requests
import json
from ..currency.message_model import Currency
# from utilities.utilities import login_required

currency = Blueprint('currency', __name__)


@currency.route('/', methods=['GET'])
def Hello():
    req = requests.get(
        'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/ils.json')
    currency_update = json.loads(req.content)
    print(currency_update)
    Currency().update(currency_update)
    return 'Hello, you reach currency update server'
