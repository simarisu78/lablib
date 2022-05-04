from flask_sqlalchemy import SQLAlchemy
from lablib.app.util.db import db
import datetime


class Checkout(db.Model):
    __tablename__ = 'checkout'

    checkout_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer(), db.ForeignKey('books.book_id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('users.user_id'))
    checkoutDate = db.Column(db.DateTime, default=datetime.datetime.now)
    isReturn = db.Column(db.Boolean, default=False)
