from flask import render_template, send_from_directory, request, redirect
from flask_paginate import Pagination, get_page_parameter
from flask_login import login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

from lablib.app import app, login_manager
from lablib.app.models import Book, Users, Checkout
from lablib.app.util.auth import ldap_auth


@app.route('/', methods=['get', 'post'])
def index():
    keyword = request.form.get('keyword')
    if keyword is None:
        books = Book.query.all()
    else:
        books = Book.query.filter(
            Book.title.like("%{}%".format(keyword))).all()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    rows = books[(page-1)*30: page*30]
    pagination = Pagination(page=page, total=len(
        books), per_page=30, css_framework='bootstrap5')
    return render_template('toppage.html', pagination=pagination, rows=rows, current_user=current_user)


@app.route('/login', methods=['get', 'post'])
def login():
    user = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('passwd')
        if username is not None and password is not None:
            user = User.auth(username=username, passwd=password)

    if user:
        login_user(user)
        print("login succeeded")
        return redirect(request.args.get('next', '/'))
    else:
        print("login failure")

    return render_template('login_form.html')


@login_manager.user_loader
def load_user(username):
    return User(username)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/userpage')
@login_required
def profile():
    usr = Users.query.filter_by(ldap_user_name=current_user.username).first()
    history = Checkout.query.filter_by(
        user_id=usr.user_id, isReturn=True).all()
    now = Checkout.query.filter_by(user_id=usr.user_id, isReturn=False).all()

    page = request.args.get(get_page_parameter(), type=int, default=1)
    rows = history[(page-1)*30: page*30]
    pagination = Pagination(page=page, total=len(
        history), per_page=30, css_framework='bootstrap5')
    return render_template('user_page.html', pagination=pagination, history=rows, now=now, current_user=current_user)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/media', 'favicon.ico')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class User:
    def __init__(self, username, stu_id=None):
        self.username = username
        self.stu_id = stu_id

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @classmethod
    def auth(cls, username, passwd):
        # ldap login failure
        if not ldap_auth(username, passwd):
            return None

        usr = Users.query.filter_by(ldap_user_name=username)[0]
        stu_id = usr.student_id
        return User(username, stu_id)
