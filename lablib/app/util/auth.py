#from flask import current_app
from ldap3 import Connection
from lablib.app import app

BASE_DOMAIN = app.config.get("BASE_DOMAIN")
LDAP_SERVER = app.config.get("LDAP_SERVER")

def ldap_auth(username, password):
	domain = ','.join(['cn={}'.format(username), BASE_DOMAIN])
	conn = Connection(LDAP_SERVER, domain, password=password)
 
	if conn.bind() is False:
		return False
	else:
		return True