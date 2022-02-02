# Development config
# DO NOT USE PRODUCTION SERVER
class DevelopmentConfig():
      DEBUG = True
      SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

Config = DevelopmentConfig
