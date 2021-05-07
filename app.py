#! /usr/bin/env python3.6

import stripe
import json
import os
import pytz
from datetime import datetime

from flask import Flask, render_template, jsonify, request, send_from_directory
from settings import pubkey, privkey

tz = pytz.timezone('Europe/Paris')

app = Flask(__name__, static_folder='static',
            static_url_path="", template_folder='templates')

stripe.api_key = privkey


@app.route('/', methods=['GET'])
def get_setup_intent_page():
    last_payments = stripe.Charge.list(limit=20)
    payments = list(map(lambda x: {'date': datetime.fromtimestamp(x['created'], tz).isoformat(),
                                   'amount': x['amount'] / 100},
                        filter(lambda x: x['paid'], last_payments)))[:5]
    return render_template('index.html', payments = payments)


@app.route('/public-key', methods=['GET'])
def get_public_key():
    return jsonify(publicKey=pubkey)


@app.route('/prepare-payment', methods=['POST'])
def create_payment_intent():
    try:
        data = json.loads(request.data)
        intent = stripe.PaymentIntent.create(amount=data['amount'], currency='eur')
        return jsonify(clientSecret=intent['client_secret'])
    except Exception as e:
        return jsonify(error=str(e)), 403
