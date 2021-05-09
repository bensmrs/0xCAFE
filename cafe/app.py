"""This module provides the application logic"""


import json
from datetime import datetime
from os.path import join

import stripe
from flask import Flask, render_template, jsonify, request

from .settings import (STATIC_FOLDER, STATIC_URL, TEMPLATE_FOLDER, PUBKEY, PRIVKEY, WEBHOOK_SECRET,
                       TZ)
from .database import init_db, db_session
from .models import Transaction


app = Flask(__name__, static_folder=join('..', STATIC_FOLDER), static_url_path=STATIC_URL,
            template_folder=join('..', TEMPLATE_FOLDER))
stripe.api_key = PRIVKEY

init_db()


@app.teardown_request
def shutdown_session(exception=None):
    """
    Close the session properly
    """
    db_session.remove()


@app.route('/', methods=['GET'])
def index():
    """
    Home page view
    """
    payments = [{'date': datetime.fromtimestamp(txn.timestamp, TZ).isoformat(),
                 'amount': txn.amount / 100,
                 'what': txn.what} for txn in Transaction.query.limit(5)]
    return render_template('index.html', payments = payments, amount=35, target=50, percent=70)


@app.route('/public-key', methods=['GET'])
def get_public_key():
    """
    Public key getter
    """
    return jsonify(publicKey=PUBKEY)


@app.route('/prepare-payment', methods=['POST'])
def create_payment_intent():
    """
    Create a payment intent
    """
    try:
        data = json.loads(request.data)
        intent = stripe.PaymentIntent.create(amount=data['amount'], currency='eur')
        return jsonify(clientSecret=intent['client_secret'])
    except Exception as err:
        return jsonify(error=str(err)), 403


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle Stripe events
    """
    try:
        event = json.loads(request.data)
    except:
        return jsonify(success=False)

    sig_header = request.headers.get('stripe-signature')
    try:
        event = stripe.Webhook.construct_event(request.data, sig_header, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        return jsonify(success=False)

    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        transaction = Transaction(intent['id'], intent['created'], intent['amount'], 'CARD')
        db_session.add(transaction)
        db_session.commit()
    return jsonify(success=True)
