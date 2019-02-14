import os

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET = os.getenv('TREMOR_API_SECRET')
    SQLALCHEMY_DATABASE_BASE  = os.getenv('TREMOR_DB_URI')
    API_KEYS = [os.getenv('TREMOR_API_KEY')]



class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_BASE + "tremor_production"


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_BASE + "tremor_development"

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_BASE + "tremor_testing"

class StagingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = Config.SQLALCHEMY_DATABASE_BASE + "tremor_staging"

app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
}
