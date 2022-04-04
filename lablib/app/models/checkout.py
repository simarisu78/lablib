from flask_sqlalchemy import SQLAlchemy
from lablib.app.db import db
import datetime

class Checkout(db.Model):
	__tablename__ = 'checkout'
	__table_args__ = (
		db.UniqueConstraint('book_id', 'user_id', name='unique_checkout_per_user'),
	)

	checkout_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
	book_id = db.Column(db.Integer(), db.ForeignKey('books.book_id'))
	user_id = db.Column(db.String(8), nullable=False)
	checkoutDate = db.Column(db.DateTime, default=datetime.datetime.now)
	isReturn = db.Column(db.Boolean, default=False)