from flask_sqlalchemy import SQLAlchemy

import sqlalchemy.engine
from sqlalchemy import event

db = SQLAlchemy()

@event.listens_for(sqlalchemy.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()

def init_db(app):
    db.init_app(app)
