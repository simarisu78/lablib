import os
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__, static_folder='static')
if os.path.exists("/".join([ os.path.dirname(__file__), "config.py" ])):
	app.config.from_object('lablib.app.config.Config')

jwt = JWTManager(app)
limiter = Limiter(app, key_func=get_remote_address)

# dirty hack
app.config["LAST_API_CALL"] = 0