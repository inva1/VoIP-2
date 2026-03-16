import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database — safe SQLite fallback for local dev; set DATABASE_URL env var for PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///voip_dev.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
    }

    # Redis
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)))
    JWT_TOKEN_LOCATION = ['headers']
    JWT_BLOCKLIST_ENABLED = True
    JWT_BLOCKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # KYC / SMS / DID Provider Configuration (env-only)
    KYC_PROVIDER_API_KEY = os.environ.get('KYC_PROVIDER_API_KEY')
    KYC_PROVIDER_URL = os.environ.get('KYC_PROVIDER_URL')
    SMS_PROVIDER_API_KEY = os.environ.get('SMS_PROVIDER_API_KEY')
    SMS_PROVIDER_URL = os.environ.get('SMS_PROVIDER_URL')
    DID_PROVIDER_API_KEY = os.environ.get('DID_PROVIDER_API_KEY')
    DID_PROVIDER_URL = os.environ.get('DID_PROVIDER_URL')

    # File Uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 16)) * 1024 * 1024

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/app.log'

    # App
    APP_NAME = "VoIP Business Solution Backend"
    APP_VERSION = "2.0"

    # AGI backend URL (for Asterisk AGI scripts to call back)
    AGI_BACKEND_URL = os.environ.get('AGI_BACKEND_URL') or 'http://localhost:5000'
    AGI_API_KEY = os.environ.get('AGI_API_KEY') or 'agi-internal-secret'


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL_PROD', 'INFO')

    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Enforce required env vars in production
    @classmethod
    def init_app(cls, app):
        for key in ['SECRET_KEY', 'JWT_SECRET_KEY', 'DATABASE_URL']:
            if not os.environ.get(key):
                raise ValueError(f"{key} not set for production environment")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL_DEV', 'DEBUG')


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_uploads')
    # Disable Redis for tests by default
    REDIS_URL = os.environ.get('TEST_REDIS_URL', '')


config_by_name = dict(
    dev=DevelopmentConfig,
    development=DevelopmentConfig,
    test=TestingConfig,
    testing=TestingConfig,
    prod=ProductionConfig,
    production=ProductionConfig,
    default=DevelopmentConfig
)


def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config_by_name.get(env, DevelopmentConfig)
