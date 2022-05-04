# When you use this application, rename this file to config.py
from datetime import timedelta


class LablibConfig():
    #SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'
    SQLALCHEMY_DATABASE_URI = '[URI of your database server]'
    JSON_SORT_KEYS = False
    JSON_AS_ASCII = False

    # Flask JWT
    JWT_SECRET_KEY = '[your secret key]'
    JWT_ALGORITHM = 'HS256'		# Sigunature Algorithm
    JWT_LEEWAY = 0
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers', 'json']

    # LDAP
    BASE_DOMAIN = '[domain (e.g. cn=Users,dc=dc,dc=localdomain)]'
    LDAP_SERVER = '[ip or FQDN of your ldap server]'

    RAKUTEN_APPLICATION_ID = '[Your application ID here!]'


Config = LablibConfig
