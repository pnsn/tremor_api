import os


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET = os.getenv('TREMOR_API_SECRET')
    SQLALCHEMY_DATABASE_BASE = os.getenv('TREMOR_DB_URI')
    API_KEYS = [os.getenv('TREMOR_API_KEY')]


class ProductionConfig(Config):
    DEBUG = False
    uri = Config.SQLALCHEMY_DATABASE_BASE + "tremor_production"
    SQLALCHEMY_DATABASE_URI = uri


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    uri = Config.SQLALCHEMY_DATABASE_BASE + "tremor_development"
    SQLALCHEMY_DATABASE_URI = uri


class TestingConfig(Config):
    TESTING = True
    uri = Config.SQLALCHEMY_DATABASE_BASE + "tremor_testing"
    SQLALCHEMY_DATABASE_URI = uri


class StagingConfig(Config):
    TESTING = True
    uri = Config.SQLALCHEMY_DATABASE_BASE + "tremor_staging"
    SQLALCHEMY_DATABASE_URI = uri


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'staging': StagingConfig,
}
