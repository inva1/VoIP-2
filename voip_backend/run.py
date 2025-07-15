import os
from flask import Flask, jsonify, current_app
from .config import get_config
from .extensions import db, migrate, bcrypt, jwt, ma, cors # redis_client removed from here
import redis # Import redis directly

# Import models here to register them with SQLAlchemy,
# or ensure they are imported before db.create_all() or migrations run.
# For example, if you have a `models` package:
from .models import user_models # This will make User model known to SQLAlchemy via db instance

def create_app(config_object=None):
    """
    Application factory, used to create and configure the Flask app.
    """
    app = Flask(__name__)

    if config_object is None:
        app.config.from_object(get_config())
    else:
        app.config.from_object(config_object)

    # Ensure instance folder exists if using instance-relative config
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass # Should not happen with exist_ok=True

    # Initialize Flask extensions with the app instance
    db.init_app(app)
    migrate.init_app(app, db) # Initialize Flask-Migrate
    bcrypt.init_app(app)      # Initialize Flask-Bcrypt
    jwt.init_app(app)         # Initialize Flask-JWT-Extended
    ma.init_app(app)          # Initialize Flask-Marshmallow

    # Configure CORS - allow all origins for /api/* routes as an example.
    # For production, specify allowed origins.
    # For production, specify allowed origins.
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize Redis client and store it on app.extensions
    # This makes it accessible via current_app.extensions['redis_client']
    if app.config.get("REDIS_URL"):
        try:
            app.extensions['redis_client'] = redis.from_url(
                app.config["REDIS_URL"],
                decode_responses=True # Ensure keys and values are strings
            )
            # Test Redis connection
            app.extensions['redis_client'].ping()
            app.logger.info("Successfully connected to Redis for JWT blocklist.")
        except redis.exceptions.ConnectionError as e:
            app.logger.error(f"Could not connect to Redis: {e}. JWT blocklisting will not work.")
            app.extensions['redis_client'] = None # Ensure it's None if connection fails
    else:
        app.logger.warning("REDIS_URL not configured. JWT blocklisting will not work.")
        app.extensions['redis_client'] = None


    # Configure JWT blocklisting
    # This callback will be called whenever a protected endpoint is accessed,
    # and will check if the JWT has been revoked.
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        if current_app.extensions.get('redis_client'):
            try:
                token_is_revoked = current_app.extensions['redis_client'].get(f"jti:{jti}")
                return token_is_revoked is not None
            except redis.exceptions.RedisError as e:
                current_app.logger.error(f"Redis error checking token blocklist for jti {jti}: {e}")
                # Fallback behavior: if Redis is down, consider all tokens as potentially valid
                # or invalid based on security posture. For higher security, return True (token revoked).
                # For higher availability (at risk of allowing revoked tokens), return False.
                return True # Fail closed: if blocklist check fails, assume token is effectively revoked.
        else:
            # No Redis client configured, so blocklisting is not active.
            # Depending on policy, you might want to log a warning or even prevent logins.
            # For now, assume tokens are not blocklisted if Redis isn't available/configured.
            # However, if JWT_BLOCKLIST_ENABLED is True, this might lead to unexpected behavior.
            # It's better to ensure Redis is up or handle this more gracefully.
            current_app.logger.warning(f"Redis client not available for blocklist check of jti {jti}. Assuming token is valid.")
            return False


    # Setup logging (basic example, can be more sophisticated)
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler

        log_dir = os.path.dirname(app.config.get('LOG_FILE', 'logs/app.log')) # Default log file
        if log_dir and not os.path.exists(log_dir): # Ensure log_dir is not empty
            os.makedirs(log_dir, exist_ok=True)

        if app.config.get('LOG_FILE'):
            file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                               maxBytes=app.config.get('LOG_FILE_MAX_BYTES', 1024 * 1024 * 10), # 10MB
                                               backupCount=app.config.get('LOG_FILE_BACKUP_COUNT', 5))
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            app.logger.addHandler(file_handler)

        app.logger.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
        app.logger.info(f'{app.config.get("APP_NAME", "Flask App")} startup')


    # Register Blueprints for different parts of the application
    from voip_backend.api.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from voip_backend.api.users.routes import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    #
    # (Other blueprints will be created and registered in later steps)


    # A simple health check endpoint
    @app.route('/health')
    def health_check():
        # Could add checks for DB, Redis connectivity here
        return jsonify(status="UP", version=app.config.get("APP_VERSION", "0.1.0")), 200

    @app.route('/')
    def index():
        return jsonify(message=f"Welcome to {app.config.get('APP_NAME','Flask App')} v{app.config.get('APP_VERSION','0.1.0')}!"), 200

    # Global error handlers (optional, but good practice)
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log the error internally
        app.logger.error(f"Server Error: {error}", exc_info=True)
        db.session.rollback() # Rollback session in case of DB error leading to 500
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        # Specific handling for 400 errors, often related to request data
        return jsonify({"error": "Bad Request", "message": str(error.description if hasattr(error, 'description') else error)}), 400

    @app.errorhandler(422) # Unprocessable Entity - often from Marshmallow validation
    def unprocessable_entity_error(error):
        # error.data.get("messages", {}) if using webargs or similar that populates this
        messages = getattr(error, 'data', {}).get('messages', 'Invalid request.')
        return jsonify({"error": "Unprocessable Entity", "messages": messages}), 422


    # Shell context for flask cli (e.g., flask shell)
    # This makes db and models available in `flask shell` without explicit imports.
    @app.shell_context_processor
    def make_shell_context():
        # Import models here for shell context
        from .models.user_models import User
        # Add other models as they are created:
        # from .models.kyc_models import KYCRecord
        # from .models.subscription_models import SubscriptionPlan, UserSubscription
        # from .models.did_models import DIDNumber
        # from .models.call_sms_models import CallRecord, SMSRecord

        return {
            'db': db,
            'User': User,
            # 'KYCRecord': KYCRecord,
            # 'SubscriptionPlan': SubscriptionPlan,
            # 'UserSubscription': UserSubscription,
            # 'DIDNumber': DIDNumber,
            # 'CallRecord': CallRecord,
            # 'SMSRecord': SMSRecord,
        }

    return app

# This is the 'app' object Gunicorn will look for if 'run:app' is specified.
# This is also what `flask run` command will use if FLASK_APP=voip_backend/run.py is set.
app = create_app()

if __name__ == '__main__':
    # For local development only (FLASK_ENV=development or FLASK_DEBUG=1)
    # Gunicorn should be used for production.
    # The `flask run` command is preferred over app.run() for development.
    # To use `flask run`, set FLASK_APP=voip_backend/run.py and FLASK_ENV=dev (or development)
    # Then run `flask run --host=0.0.0.0 --port=5000`

    # This __main__ block provides a fallback if script is run directly (python run.py)
    current_config = get_config()
    if current_config.DEBUG:
        app.run(host='0.0.0.0', port=int(os.environ.get("FLASK_RUN_PORT", 5000)), debug=True)
    else:
        # In a non-debug environment, direct execution of app.run() is discouraged.
        # Gunicorn is configured via gunicorn.conf.py and supervisor.
        print("Running in non-debug mode. Use Gunicorn or `flask run` for development.")
        app.run(host='0.0.0.0', port=int(os.environ.get("FLASK_RUN_PORT", 5000)), debug=False)
