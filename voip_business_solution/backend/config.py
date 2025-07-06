import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'postgresql://voip_admin:password@localhost/voip_production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Redis Configuration
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'

    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-change-in-production'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # KYC Service Configuration
    KYC_PROVIDER_API_KEY = os.environ.get('KYC_PROVIDER_API_KEY')
    KYC_PROVIDER_URL = os.environ.get('KYC_PROVIDER_URL')

    # SMS Service Configuration
    SMS_PROVIDER_API_KEY = os.environ.get('SMS_PROVIDER_API_KEY')
    SMS_PROVIDER_URL = os.environ.get('SMS_PROVIDER_URL')

    # DID Provider Configuration
    DID_PROVIDER_API_KEY = os.environ.get('DID_PROVIDER_API_KEY')
    DID_PROVIDER_URL = os.environ.get('DID_PROVIDER_URL')

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'logs', 'app.log'))

    # Ensure upload and log directories exist
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    # Add any production-specific overrides here
    # For example, adjust logging levels or specific service URLs
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'ERROR'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'postgresql://voip_admin:password@localhost/voip_dev'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite for tests
    WTF_CSRF_ENABLED = False # Disable CSRF for testing forms if Flask-WTF is used
    # Ensure UPLOAD_FOLDER and LOG_FILE are set for testing, possibly to temp dirs
    UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_uploads'))
    LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'test_logs', 'app_test.log'))

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

# Helper to get config object based on environment variable
def get_config():
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    return DevelopmentConfig

config = get_config()
