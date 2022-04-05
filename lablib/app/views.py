from flask import render_template, send_from_directory
from markupsafe import escape

from lablib.app import app

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
    return send_from_directory('static/media', 'favicon.ico')
