import os
from flask import Flask, jsonify
from .config import get_config # Use get_config to load based on FLASK_ENV
# Import extensions if you initialize them here, e.g.:
# from .extensions import db, migrate, jwt, cors, celery (if you create an extensions.py)
# from redis import Redis

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
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Initialize extensions
    # Example:
    # db.init_app(app)
    # migrate.init_app(app, db)
    # jwt.init_app(app)
    # cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Configure CORS properly

    # Setup logging (basic example, can be more sophisticated)
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler

        log_dir = os.path.dirname(app.config['LOG_FILE'])
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(app.config['LOG_FILE'],
                                           maxBytes=app.config.get('LOG_FILE_MAX_BYTES', 1024 * 1024 * 10), # 10MB
                                           backupCount=app.config.get('LOG_FILE_BACKUP_COUNT', 5))
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config['LOG_LEVEL'])
        app.logger.info(f'{app.config["APP_NAME"]} startup')


    # Register Blueprints for different parts of the application
    # from .api.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # from .api.users import users_bp
    # app.register_blueprint(users_bp, url_prefix='/api/users')

    # from .api.subscriptions import subscriptions_bp
    # app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')

    # from .api.kyc import kyc_bp
    # app.register_blueprint(kyc_bp, url_prefix='/api/kyc')

    # from .api.calls import calls_bp
    # app.register_blueprint(calls_bp, url_prefix='/api/calls')

    # from .api.sms import sms_bp
    # app.register_blueprint(sms_bp, url_prefix='/api/sms')

    # A simple health check endpoint
    @app.route('/health')
    def health_check():
        # Could add checks for DB, Redis connectivity here
        return jsonify(status="UP", version=app.config["APP_VERSION"]), 200

    @app.route('/')
    def index():
        return jsonify(message=f"Welcome to {app.config['APP_NAME']} v{app.config['APP_VERSION']}!"), 200

    # Global error handlers (optional, but good practice)
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        # Log the error internally
        app.logger.error(f"Server Error: {error}", exc_info=True)
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500


    # Shell context for flask cli (e.g., flask shell)
    # @app.shell_context_processor
    # def make_shell_context():
    #     return {'db': db, 'User': User, 'SubscriptionPlan': SubscriptionPlan} # Example models

    return app

# This is the 'app' object Gunicorn will look for if 'run:app' is specified.
app = create_app()

if __name__ == '__main__':
    # For local development only (FLASK_ENV=development)
    # Gunicorn should be used for production.
    flask_env = os.getenv('FLASK_ENV')
    config = get_config()
    if flask_env == 'dev' or config.DEBUG:
        app.run(host='0.0.0.0', port=config.get('FLASK_RUN_PORT', 5000), debug=True)
    else:
        print("Running in production mode. Use Gunicorn to serve the application.")
        # Fallback for direct execution in a non-dev environment, though Gunicorn is preferred.
        app.run(host='0.0.0.0', port=config.get('FLASK_RUN_PORT', 5000))
