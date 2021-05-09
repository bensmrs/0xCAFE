"""This module provides the data models for the ORM"""


from sqlalchemy import Column, Integer, String
from .database import Base


class Transaction(Base):
    """
    This class describes a transaction

    :param id: The transaction id
    :param timestamp: The timestamp
    :param amount: The amount
    :param what: What this transaction is about
    """
    __tablename__ = 'transactions'
    id = Column(String(50), primary_key=True)
    timestamp = Column(Integer)
    amount = Column(Integer)
    what = Column(String(16))

    def __init__(self, id, timestamp, amount, what):
        self.id = id
        self.timestamp = timestamp
        self.amount = amount
        self.what = what

    def __repr__(self):
        return '<Transaction %r>' % (self.id)
