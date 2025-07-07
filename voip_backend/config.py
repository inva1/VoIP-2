import os
from datetime import timedelta

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    # Ensure this is a strong, randomly generated key in production

    # Database Configuration
    # Example: postgresql://username:password@host:port/database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://voip_admin:secure_password_here@localhost:5432/voip_production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True, # Enable connection pool pre-ping
    }

    # Redis Configuration
    # Example: redis://:password@host:port/db
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    # If Redis has a password: 'redis://:your_redis_password_here@localhost:6379/0'


    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    # Ensure this is a strong, randomly generated key in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_HOURS', 1)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_DAYS', 30)))
    # For Flask-JWT-Extended
    JWT_TOKEN_LOCATION = ['headers', 'cookies'] # Allow tokens to be sent in headers or cookies
    JWT_COOKIE_SECURE = os.environ.get('JWT_COOKIE_SECURE', 'False').lower() == 'true' # True in production
    JWT_COOKIE_SAMESITE = 'Lax' # Or 'Strict' or 'None' (if 'None', JWT_COOKIE_SECURE must be True)


    # KYC Service Configuration (placeholders, replace with actual provider details)
    KYC_PROVIDER_API_KEY = os.environ.get('KYC_PROVIDER_API_KEY')
    KYC_PROVIDER_URL = os.environ.get('KYC_PROVIDER_URL')

    # SMS Service Configuration (placeholders)
    SMS_PROVIDER_API_KEY = os.environ.get('SMS_PROVIDER_API_KEY')
    SMS_PROVIDER_URL = os.environ.get('SMS_PROVIDER_URL')

    # DID Provider Configuration (placeholders)
    DID_PROVIDER_API_KEY = os.environ.get('DID_PROVIDER_API_KEY')
    DID_PROVIDER_URL = os.environ.get('DID_PROVIDER_URL')

    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/opt/voip-backend/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH_MB', 16)) * 1024 * 1024  # 16MB default

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or '/var/log/voip-backend/app.log' # Ensure directory exists and is writable

    # Celery Configuration (if used, details not fully specified in the document for Celery setup)
    # CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or REDIS_URL
    # CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or REDIS_URL

    # Application specific settings
    APP_NAME = "VoIP Business Solution Backend"
    APP_VERSION = "2.0"


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    JWT_COOKIE_SECURE = True # Ensure cookies are only sent over HTTPS
    # Example: override DATABASE_URL for production if it's different and not set by env
    # SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL') or Config.SQLALCHEMY_DATABASE_URI
    # Ensure LOG_LEVEL is appropriate for production, e.g., INFO or WARNING
    LOG_LEVEL = os.environ.get('LOG_LEVEL_PROD', 'INFO')
    # Ensure SECRET_KEY and JWT_SECRET_KEY are definitely set from environment in production
    if not os.environ.get('SECRET_KEY'):
        raise ValueError("SECRET_KEY not set for production environment")
    if not os.environ.get('JWT_SECRET_KEY'):
        raise ValueError("JWT_SECRET_KEY not set for production environment")


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    # Development specific settings, e.g., more verbose logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL_DEV', 'DEBUG')
    # Example: use a local dev database if needed
    # SQLALCHEMY_DATABASE_URI = 'postgresql://voip_dev:dev_password@localhost/voip_dev'


class TestingConfig(Config):
    DEBUG = True # Often True to get more error details during tests
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///:memory:' # Use in-memory SQLite for tests
    # Make tests run faster
    WTF_CSRF_ENABLED = False # Disable CSRF forms protection in tests
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    # Ensure JWT cookies are not marked secure if tests run over HTTP
    JWT_COOKIE_SECURE = False
    # Use a different upload folder for tests
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_uploads')


# Dictionary to access config classes by name
config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig,
    default=DevelopmentConfig
)

def get_config():
    env = os.getenv('FLASK_ENV', 'default')
    return config_by_name.get(env, DevelopmentConfig)

# Example usage in app.py:
# from config import get_config
# app.config.from_object(get_config())
