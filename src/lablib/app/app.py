from flask import Flask, url_for, render_template, send_from_directory
from markupsafe import escape
import os

from app.api import api


app = Flask(__name__, static_folder="static")

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

