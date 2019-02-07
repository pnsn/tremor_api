import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    DATABASE_URI = os.environ['TREMOR_DB_URI']


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
