from ._app import app, jwt, limiter, csrf, login_manager
from .rest import api
from .util.db import init_db
from .portal import views

app.register_blueprint(api)
csrf.exempt(api)
init_db(app)