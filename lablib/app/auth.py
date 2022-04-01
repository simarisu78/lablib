#from flask import current_app
from ldap3 import Connection
from .config import Config

BASE_DOMAIN = Config.BASE_DOMAIN
LDAP_SERVER = Config.LDAP_SERVER

def ldap_auth(username, password):
	domain = ','.join(['cn={}'.format(username), BASE_DOMAIN])
	conn = Connection(LDAP_SERVER, domain, password=password)
 
	if conn.bind() is False:
		return False
	else:
		return True