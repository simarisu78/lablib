from flask import Blueprint, request, abort, jsonify

api = Blueprint('api', __name__, url_prefix='/api/v1')

# get book list
@api.route('/books', methods=['GET'])
def book_list():
    return "book list"

# register books
@api.route('/books', methods=['POST'])
def register_books():
    return "register a book"

# borrow books
@api.route('/library', methods=['POST'])
def borrow_books():
    return "borrow books"

# return books
@api.route('/library', methods=['DELETE'])
def return_books():
    return "return books"

# error handler
@api.errorhandler(400)
@api.errorhandler(404)
def error_handler(error):
    return "error"
