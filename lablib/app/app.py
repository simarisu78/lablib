from flask import Flask, url_for, render_template, send_from_directory
from markupsafe import escape
import os

from lablib.app.api import api
from lablib.app.models.books import Book
from lablib.app.db import init_db

app = Flask(__name__, static_folder="static")
app.config.from_object('lablib.app.config.Config')
init_db(app)

# register api blueprint
app.register_blueprint(api)

@app.route('/')
def index():
    return render_template('layout.html')


@app.route('/login')
def login():
    return 'login'


@app.route('/users/<username>')
def profile(username):
    return '{}\'s profile'.format(escape(username))


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/media'),
                               'favicon.ico', )
