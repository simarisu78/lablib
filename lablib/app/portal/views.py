from flask import render_template, send_from_directory, request
from flask_paginate import Pagination, get_page_parameter
from markupsafe import escape

from lablib.app import app, csrf
from lablib.app.models import Book

@app.route('/', methods=['get', 'post'])
def index():
	keyword = request.form.get('keyword')
	if keyword is None:
		books = Book.query.all()
	else:
		books = Book.query.filter(Book.title.like("%{}%".format(keyword))).all()

	page = request.args.get(get_page_parameter(), type=int, default=1)
	rows = books[(page-1)*30 : page*30]
	pagination = Pagination(page=page, total=len(books), per_page=30, css_framework='bootstrap5')
	return render_template('toppage.html', pagination=pagination, rows=rows)

@app.route('/login')
def login():
	return 'login'

@app.route('/users/<username>')
def profile(username):
	return '{}\'s profile'.format(escape(username))


@app.route('/favicon.ico')
def favicon():
	return send_from_directory('static/media', 'favicon.ico')
