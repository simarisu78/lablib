from mmap import ACCESS_COPY
from os import access
from flask import Blueprint, request, abort, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

api = Blueprint('api', __name__, url_prefix='/api/v1')
from lablib.app.auth import ldap_auth
from .models import Book, BookSchema, Checkout

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
	return "register a book! user:%s" % get_jwt_identity()

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
