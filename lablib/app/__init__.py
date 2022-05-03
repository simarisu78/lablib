from ._app import app, jwt, limiter, csrf
from .rest import api
from .util.db import init_db
from .portal import views

app.register_blueprint(api)
init_db(app)