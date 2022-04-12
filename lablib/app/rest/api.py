from functools import wraps
from flask import Blueprint, make_response, request, abort, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token

api = Blueprint('api', __name__, url_prefix='/api/v1')
from lablib.app.util.auth import ldap_auth
from lablib.app.models import Book, BookSchema, Checkout
from lablib.app import limiter
from .book_register import self_register, search_external_api

# content_type checker
def content_type(value):
	def _content_type(func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if not request.headers.get("Content-Type") == value:
				return make_response(
					jsonify({"msg":
					"Content-Type is invalid. Please set application/json"})
				)
			return func(*args, **kwargs)
		return wrapper
	return _content_type

# generate token
@api.route('/auth', methods=['POST'])
@content_type("application/json")
def auth():
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
@content_type("application/json")
@jwt_required()
def register_books():
	try:
		data = request.get_json()
		selfRegister = data.get('self')
		books = data.get('books')
	except:
		return jsonify({"status":"ng", "msg":"can not read book data. Please sent book data in json's list format"})

	if selfRegister:
		return self_register(books)
	else:
		return search_external_api(books)

# borrow books
@api.route('/checkout', methods=['POST'])
@content_type("application/json")
def borrow_books():
	return "check out books"

# return books
@api.route('/checkout', methods=['DELETE'])
@content_type("application/json")
def return_books():
	return "return books"

# error handler
@api.errorhandler(400)
@api.errorhandler(404)
def error_handler(error):
	return "error"

@api.errorhandler(429)
def ratelimit_handler(e):
	return make_response(jsonify(error="ratelimit exceeded: %s" % e.description), 429)