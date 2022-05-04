from flask import current_app
from ldap3 import Connection
#from lablib.app import app


def ldap_auth(username, password):
    BASE_DOMAIN = current_app.config.get("BASE_DOMAIN")
    LDAP_SERVER = current_app.config.get("LDAP_SERVER")

    domain = ','.join(['cn={}'.format(username), BASE_DOMAIN])
    conn = Connection(LDAP_SERVER, domain, password=password)

    if conn.bind() is False:
        return False
    else:
        return True
