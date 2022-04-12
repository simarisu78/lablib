from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import null
from lablib.app.util.db import db
import datetime

class Users(db.Model):
	__tablename__ = 'users'

	user_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
	ldap_user_name = db.Column(db.String(256), nullable=False)

	# relationship
	checkout = db.relationship("Checkout", backref=db.backref("user",uselist=False))