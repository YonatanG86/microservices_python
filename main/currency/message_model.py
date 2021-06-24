from flask import jsonify, request, session
from main.db import mongo
import uuid
from datetime import datetime


class Message:
    def write(self):

        receiver = request.form.get('receiver', None)
        message = request.form.get('message', None)
        subject = request.form.get('subject')


# Message data validation
        if not receiver:
            return jsonify({"error": "A message must contain a receiver"}), 400

        if not subject:
            return jsonify({"error": "A message must contain a subject"}), 400

        receiver_user = mongo.db.usd.find_one({'email': receiver})
        if not receiver_user:
            return jsonify({"error": "Received user could not be found"}), 400


# Added Sender_id and receiver_user because users sometimes change their email
# Any type of reference to the users should be done with unchangeable filed like primary key
        message = {
            "_id": uuid.uuid4().hex,
            "sender": session['logged_in']['email'],
            "sender_id": session['logged_in']['_id'],
            "sender_name": session['logged_in']['name'],
            "receiver": receiver,
            "receiver_id": receiver_user['_id'],
            "receiver_name": receiver_user['name'],
            "message": message,
            "subject": subject,
            "creation_date": datetime.now(),
            "read": False,
            "sender_delete": False,
            "receiver_delete": False,
        }

        mongo.db.usd.insert_one(message)
        return jsonify("message was sent"), 200

    def all_messages(self):
        messages = mongo.db.usd.find({'receiver_id': session['logged_in']['_id'],
                                      'receiver_delete': False})
        response = []
        for message in messages:
            response.append(message)
        if len(response) == 0:
            return jsonify("No messages found"), 200

        return jsonify({"messages": response}), 200


# A massage can be deleted without the receiver reading the massage

    def all_unread_messages(self):
        messages = mongo.db.messages.find({'receiver_id': session['logged_in']['_id'],
                                           'receiver_delete': False,
                                           'read': False})
        response = []

        for message in messages:
            response.append(message)

        if len(response) == 0:
            return jsonify({"error": "No messages found"}), 400

        return jsonify({"messages": response}), 200

    def read_message(self, id):
        message = mongo.db.messages.find_one({'receiver_id': session['logged_in']['_id'],
                                              '_id': str(id)})

        if message is None:
            return jsonify({"error": "The message does not exist"}), 400
        else:
            mongo.db.messages.find_one_and_update({'receiver_id': session['logged_in']['_id'],
                                                   '_id': str(id)},
                                                  {'$set': {'read': True}})

# after the read update, the message need to be to be retrive again
            message = mongo.db.messages.find_one({'receiver_id': session['logged_in']['_id'],
                                                  '_id': str(id)})

            return jsonify(message), 200


# Delete message
#  If user is the sender - delelet the message for sender
#  If user is the sender and the receiver have not read the message - delelet the message for both sender and receiver
#  If user is the  receiver - delete the message for the receiver
#  Messages are not being deleted (with delete_one query) from data base but they will not show up in searches.
#  If the message was already deleted return an error


    def delete_message(self, id):
        message = mongo.db.messages.find_one({'_id': str(id)})

        if message is None:
            return jsonify({"error": "The message does not exist"}), 400

        if message['sender_id'] == session['logged_in']['_id']:

            if message['sender_delete'] == True:
                return jsonify({"error": "The message was already deleted"}), 400

            mongo.db.messages.find_one_and_update({'_id': str(id),
                                                   'sender_id': session['logged_in']['_id']},
                                                  {'$set': {'sender_delete': True}})

            if message['read'] == False:
                mongo.db.messages.find_one_and_update({'_id': str(id),
                                                       'sender_id': session['logged_in']['_id'],
                                                       'read': False},
                                                      {'$set': {'receiver_delete': True}})
                return jsonify({"message": "The message was deleted for both sender and receiver"}), 200

            return jsonify({"message": "The message was deleted for the sender only"}), 200

        if message['receiver_id'] == session['logged_in']['_id']:

            if message['receiver_delete'] == True:
                return jsonify({"error": "The message was already deleted"}), 400

            mongo.db.messages.find_one_and_update({'_id': str(id),
                                                   'receiver_id': session['logged_in']['_id']},
                                                  {'$set': {'receiver_delete': True}})

            return jsonify({"message": "The message was deleted for the receiver"}), 200

        return jsonify({"error": "User not authorized to delete the message"}), 401

    def conversation(self, id):
        if mongo.db.users.find_one({'_id': str(id)}) is None:
            return jsonify({"error": "The requested user does not exist"}), 400

# Converstion between 2 users
# find all the messages that were not deleted by the user
# with either the session's user as the receiver and the requested user in the sender
# OR the session's user as the sender and the requested user in the receiver
        messages = mongo.db.messages.find({'$or': [
            {'receiver_id': session['logged_in']['_id'],
                'receiver_delete':False, 'sender_id': str(id)},
            {'sender_id': session['logged_in']['_id'],
                'sender_delete':False, 'receiver_id': str(id)}
        ]}).sort('creation_date', -1)
        response = []

        for message in messages:
            response.append(message)

        if len(response) == 0:
            return jsonify({"error": "You do not have a conversation with the requested user"}), 400

        return jsonify({"messages": response}), 200

    def all_messages_users(self):
        messages = mongo.db.messages.find({})
        response = []
        for message in messages:
            response.append(message)
        if len(response) == 0:
            return jsonify("No messages found"), 200

        return jsonify({"messages": response}), 200
