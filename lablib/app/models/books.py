from email.policy import default
from flask_sqlalchemy import SQLAlchemy
from lablib.app.db import db
from flask_marshmallow import Marshmallow

class Book(db.Model):
	__tablename__ = 'books'

	book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	barcode = db.Column(db.String(13), nullable=False, unique=True)
	title = db.Column(db.String(255), nullable=False)
	author = db.Column(db.String(255), nullable=False)
	detail = db.Column(db.Text())
	# YYYY-MM
	publishmonth = db.Column(db.String(7), nullable=False)
	publisher = db.Column(db.String(255))
	# 蔵書数
	amount = db.Column(db.Integer, nullable=False)
	stock = db.Column(db.Integer, nullable=False)
	# sumbnail url
	large_url = db.Column(db.Text())
	# relationship
	checkout = db.relationship("Checkout", backref=db.backref("book", uselist=False))

ma = Marshmallow()
class BookSchema(ma.Schema):
	class Meta:
		fields = ("barcode", "title", "author", "detail", "publishmonth", "publisher", "amount", "stock", "large_url")