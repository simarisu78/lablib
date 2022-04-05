from ._app import app, jwt, limiter
from .rest import api
from .util.db import init_db

app.register_blueprint(api)
init_db(app)