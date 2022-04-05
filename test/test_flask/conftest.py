import pytest
from lablib.app import app
from lablib.app.util.db import init_db
from datetime import timedelta
import os
import random
import string

import logging
logger = logging.getLogger(__name__)

class TestConf:
	#SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}/{}?charset=utf8mb4".format(
				os.environ.get("DB_USERNAME"),
				os.environ.get("DB_PASSWORD"),
				os.environ.get("DB_FQDN"),
				os.environ.get("DB_DATABASE_NAME")
				)
	JSON_SORT_KEYS = False
	JSON_AS_ASCII = False
	
	# Flask JWT
	JWT_SECRET_KEY = "".join(random.choices(string.ascii_letters + string.digits, k=32))
	JWT_ALGORITHM = 'HS256'		# Sigunature Algorithm
	JWT_LEEWAY = 0
	JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=3)
	JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
	JWT_TOKEN_LOCATION = ['headers', 'json']
 
	# LDAP
	logger.info(os.environ.get("BASE_DOMAIN"))
	BASE_DOMAIN = os.environ.get("BASE_DOMAIN")
	LDAP_SERVER = os.environ.get("LDAP_SERVER")
 
	RAKUTEN_APPLICATION_ID = os.environ.get("RAKUTEN_APPLICATION_ID")


@pytest.fixture(scope='session')
def client():
	app.config['TESTING'] = True
	app.config.from_object(TestConf)
	logger.info(app.config.get("BASE_DOMAIN"))
	
	with app.test_client() as client:
		with app.app_context():
			init_db(app)
		yield client