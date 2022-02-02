from flask_sqlalchemy import SQLAlchemy
from lablib.app.db import db

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    barcode = db.Column(db.String(13), nullable=False, unique=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    # YYYY-MM
    publishmonth = db.Column(db.String(7), nullable=False)
    publisher = db.Column(db.String(255))
    

