import os
import sys
import json
import datetime

import requests
from flask import Flask, request
from get_reponse import get_reponse

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "App running ", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
#     log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    log("\nRECEIVE: {sender_id}  o>>> {recipient} [Me] :   {text}".format(sender_id=sender_id,recipient=recipient_id, text=message_text))
                    try:
                        response= get_reponse(message_text)
                    except:
                        response= get_reponse(message_text)
                    send_message(recipient_id,sender_id,response)



                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(sender_id,recipient_id, message_text):

    log("\nSEND: {sender_id} [Me]  o>>> {recipient} :   {text}".format(sender_id=sender_id,recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
        # "access_token": "EAAL4VfjZBoG8BAB8gB3u61AZAQ3Lx3H75m8gizvZAtaAUWpwenoLk7hjOBtNPLwkmGUbdVvg4wGHke6RpITVwWETrcnFYanZAMgYpp5SjtOEe3LjtYpgkZB2tZCqZCSGcWNeawKXNY8ZAW0d8psGCabf1wEt93mFnbzmFfyrzlouAxOZCuD4MknN5ZANnZCUEYQaZCwZD"
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg).format(*args, **kwargs)
        print("\n{} : {}".format(datetime.datetime.now()+datetime.timedelta(hours = 7), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
