"""This module allows to access the 0xCAFE CLI"""


import sys
from datetime import datetime

from .app import app
from .settings import DEFAULT_HOST, DEFAULT_PORT, TZ
from .models import Transaction
from .database import db_session


def truncate(string, length):
    """
    Truncate a string to a certain length

    :param string: The string to truncate
    :param length: The length
    """
    return (string[:length - 1] + '…') if len(string) > length else string

def format_time(timestamp):
    """
    Format a timestamp

    :param timestamp: The timestamp to format
    """
    return datetime.fromtimestamp(timestamp, TZ).isoformat().replace('-', '/').replace('T', ' ')

def format_amount(amount):
    """
    Format an amount

    :param amount: The amount to format
    """
    return str(amount/100) + ' €'

def die(code=0):
    """
    Clean up and exit the CLI

    :param code: The exit code
    """
    db_session.remove()
    sys.exit(code)

class Command:
    """
    This class contains all the commands of the CLI
    """

    @staticmethod
    def run(host=DEFAULT_HOST, port=str(DEFAULT_PORT)):
        """
        Run the app in debug mode

        :param host: The HTTP host
        :param port: The HTTP port
        """
        app.run(host=host, port=int(port), debug=True)

    @staticmethod
    def show():
        """
        Show all the transactions
        """
        print('╭───────────── ID ─────────────┬─────────── Date ───────────┬─ Amount ─┬'
              '───── What ─────╮')
        for txn in Transaction.query.all():
            print('│ {:28} │ {:26} │ {:>8} │ {:14} │'.format(truncate(txn.id, 28),
                                                             format_time(txn.timestamp),
                                                             format_amount(txn.amount),
                                                             truncate(txn.what, 14)))
        print('╰───────────── ID ─────────────┴─────────── Date ───────────┴─ Amount ─┴'
              '───── What ─────╯')

    @staticmethod
    def add(id, amount, what='CASH', timestamp=None):
        """
        Add a transaction

        :param id: The transaction id
        :param amount: The amount
        :param what: What the transaction is about
        :param timestamp: The transaction timestamp
        """
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        transaction = Transaction(id, int(timestamp), amount, what)
        db_session.add(transaction)
        db_session.commit()

    @staticmethod
    def remove(id):
        """
        Remove a transaction

        :param id: The transaction id
        """
        db_session.query(Transaction).filter(Transaction.id == id).delete()
        db_session.commit()


if len(sys.argv) < 2:
    print("Usage: python3 -m cafe <command> [args...]")
    die(1)

args = []
kwargs = {}
skip = False

for pair in zip(sys.argv[2:], sys.argv[3:] + [None]):
    if skip:
        skip = False
        continue
    if pair[0].startswith('--'):
        kwargs[pair[0][2:]] = pair[1]
        skip = True
    elif len(kwargs) == 0:
        args.append(pair[0])
    else:
        print("Error: Positional argument `%s' follows keyword argument" % pair[0])
        die(1)

commands = [command for command in Command.__dict__ if isinstance(Command.__dict__[command],
                                                                  staticmethod)]

if sys.argv[1] not in commands:
    print("Error: Command `%s' not found" % sys.argv[1])
    die(1)
command = Command.__dict__[sys.argv[1]]
command.__func__(*args, **kwargs)
