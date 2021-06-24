from flask import Blueprint
# from model.message_model import Message
# from utilities.utilities import login_required

currency = Blueprint('currency', __name__)


@currency.route('/', methods=['POST'])
def Hello():
    return 'Hello'
