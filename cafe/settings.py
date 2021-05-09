"""This module provides the configuration variables for the app"""


import pytz


TZ = pytz.timezone('Europe/Paris')

DATABASE = 'sqlite:///cafe.db'

DEFAULT_HOST = 'localhost'
DEFAULT_PORT = 4242

STATIC_FOLDER = 'static'
STATIC_URL = ''
TEMPLATE_FOLDER = 'templates'

MONTHLY_TARGET = 5000

PRIVKEY = 'sk_test_51In3owKZdjBRnbvgstWYpen5QXrSrHR2xtmJPyAAZYiXXpYHfTdQSd1oS1izEPdyDt5EvUCK' \
          'EuIEgEByqM09fr7j00vazMmBrR'
PUBKEY = 'pk_test_51In3owKZdjBRnbvgCtvzBLSf7aG4tXNbQDUGqunoTHLgMzCmPdek314KPSQaUyLlAzqPdKN0J' \
         'ApgrDGdTyo6yeCm001JZiwpH2'
WEBHOOK_SECRET = 'whsec_G2H4uztMNxmH0AMJcuSh490UXP8CQ0SR'
