import os
from flask import Flask, jsonify, current_app
from .config import get_config
from .extensions import db, migrate, bcrypt, jwt, ma, cors
import redis


def create_app(config_object=None):
    """Application factory."""
    app = Flask(__name__)

    if config_object is None:
        app.config.from_object(get_config())
    else:
        app.config.from_object(config_object)

    # Call init_app if the config class defines it (e.g. ProductionConfig)
    if hasattr(config_object, 'init_app'):
        config_object.init_app(app)

    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # Import all models to register them with SQLAlchemy
    with app.app_context():
        from voip_backend.models import (  # noqa: F401
            User, KYCRecord, SubscriptionPlan, UserSubscription,
            DIDNumber, CallRecord, SMSRecord, RegulatoryCDR
        )

    # Initialize Redis
    if app.config.get("REDIS_URL"):
        try:
            app.extensions['redis_client'] = redis.from_url(
                app.config["REDIS_URL"], decode_responses=True
            )
            app.extensions['redis_client'].ping()
            app.logger.info("Successfully connected to Redis.")
        except (redis.exceptions.ConnectionError, redis.exceptions.ResponseError) as e:
            app.logger.warning(f"Could not connect to Redis: {e}. JWT blocklisting disabled.")
            app.extensions['redis_client'] = None
    else:
        app.extensions['redis_client'] = None

    # JWT blocklist check
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict):
        jti = jwt_payload["jti"]
        r = current_app.extensions.get('redis_client')
        if r:
            try:
                return r.get(f"jti:{jti}") is not None
            except redis.exceptions.RedisError:
                return True  # Fail closed
        return False

    # Setup logging
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler

        log_file = app.config.get('LOG_FILE', 'logs/app.log')
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(app.config.get('LOG_LEVEL', 'INFO'))
        app.logger.info(f'{app.config.get("APP_NAME")} startup')

    # Register Blueprints
    from voip_backend.api.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from voip_backend.api.users.routes import users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')

    from voip_backend.api.kyc.routes import kyc_bp
    app.register_blueprint(kyc_bp, url_prefix='/api/kyc')

    from voip_backend.api.subscriptions.routes import subscriptions_bp
    app.register_blueprint(subscriptions_bp, url_prefix='/api/subscriptions')

    from voip_backend.api.dids.routes import dids_bp
    app.register_blueprint(dids_bp, url_prefix='/api/dids')

    from voip_backend.api.calls.routes import calls_bp
    app.register_blueprint(calls_bp, url_prefix='/api/calls')

    from voip_backend.api.sms.routes import sms_bp
    app.register_blueprint(sms_bp, url_prefix='/api/sms')

    from voip_backend.api.admin.routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Health check
    @app.route('/health')
    def health_check():
        return jsonify(status="UP", version=app.config.get("APP_VERSION", "0.1.0")), 200

    @app.route('/')
    def index():
        return jsonify(message=f"Welcome to {app.config.get('APP_NAME')} v{app.config.get('APP_VERSION')}!"), 200

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Not Found", "message": str(error)}), 404

    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Server Error: {error}", exc_info=True)
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "message": "An unexpected error occurred."}), 500

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({"error": "Bad Request", "message": str(error.description if hasattr(error, 'description') else error)}), 400

    @app.errorhandler(422)
    def unprocessable_entity_error(error):
        messages = getattr(error, 'data', {}).get('messages', 'Invalid request.')
        return jsonify({"error": "Unprocessable Entity", "messages": messages}), 422

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from voip_backend.models import (
            User, KYCRecord, SubscriptionPlan, UserSubscription,
            DIDNumber, CallRecord, SMSRecord, RegulatoryCDR
        )
        return {
            'db': db, 'User': User, 'KYCRecord': KYCRecord,
            'SubscriptionPlan': SubscriptionPlan, 'UserSubscription': UserSubscription,
            'DIDNumber': DIDNumber, 'CallRecord': CallRecord,
            'SMSRecord': SMSRecord, 'RegulatoryCDR': RegulatoryCDR,
        }

    return app


# Module-level app for Gunicorn: run:app
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("FLASK_RUN_PORT", 5000)), debug=True)
