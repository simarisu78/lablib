from mmap import ACCESS_COPY
from os import access
import re
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

api = Blueprint('api', __name__, url_prefix='/api/v1')
from lablib.app.auth import ldap_auth
from .models import Book, BookSchema, Checkout
from .db import db

# generate token
@api.route('/auth', methods=['POST'])
def auth():
	if request is None:
		return jsonify({"msg": "Authentication was failed"})

	username = request.json.get("username", None)
	password = request.json.get("password", None)
	if ldap_auth(username, password) is False:
		return jsonify({"msg": "Authentication was failed"})

	access_token = create_access_token(identity=username)
	return jsonify(access_token=access_token)

# get book list
@api.route('/books', methods=['GET'])
def book_list():
	books = Book.query.all()
	if books is not None:
		return jsonify({"status": "ok", "Books" : BookSchema(many=True).dump(books)})
	else:
		return jsonify({"status": "ng"})

# register books
@api.route('/books', methods=['POST'])
@jwt_required()
def register_books():
	if request is None:
		return jsonify({"status": "ng", "msg": "Please post data"})

	if request.headers['Content-Type'] != 'application/json':
		return jsonify({"status": "ng", "msg": "Content-Type is invalid. Please set application/json"})
	
	try:
		data = request.get_json()
		selfRegister = data.get('self')
		books = data.get('books')
	except:
		return jsonify({"status":"ng", "msg":"can not read book data. Please sent book data in json's list format"})

	if selfRegister:
		try:
			for book_req in books:
				barcode = book_req.get('barcode')
				title = book_req.get('title')
				author = book_req.get('author')
				detail = book_req.get('detail')
				publishmonth = book_req.get('publishmonth')
				publisher = book_req.get('publisher')
				amount = 1
				stock = amount

				barcode_pat = re.compile("\d+")
				publishmonth_pat = re.compile("\d{4}-\d{2}")
				if not barcode_pat.fullmatch(barcode) or not publishmonth_pat.fullmatch(publishmonth):
					raise ValueError

				book = Book(barcode=barcode, title=title, author=author,
                   detail=detail, publishmonth=publishmonth, publisher=publisher,
                   amount=amount, stock=stock)
				db.session.add(book)

			db.session.commit()
		except ValueError:
			return jsonify({"status":"ng", "msg":"The format is invalid. Please check barcode and publishmonth."})
		except:
			return jsonify({"status":"ng", "msg":"Some error occured. Please check your book data. barcode, title, author, publishmonth are required."})

		return jsonify({"status": "ok"})
	else:
		return jsonify({"msg":"auto mode"})

# borrow books
@api.route('/checkout', methods=['POST'])
def borrow_books():
	return "check out books"

# return books
@api.route('/checkout', methods=['DELETE'])
def return_books():
	return "return books"

# error handler
@api.errorhandler(400)
@api.errorhandler(404)
def error_handler(error):
	return "error"
