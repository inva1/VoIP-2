import logging
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
# from flask_jwt_extended import JWTManager # Will be added later

from .config import config # Use the config object directly

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()
# jwt = JWTManager() # Will be added later

def create_app(config_class=config):
    """
    Application factory function.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions here
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Example CORS config
    # jwt.init_app(app) # Will be added later

    # Register blueprints here
    # from .routes.auth_routes import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # from .routes.user_routes import user_bp
    # app.register_blueprint(user_bp, url_prefix='/api/users')

    # ... other blueprints

    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists(os.path.dirname(app.config['LOG_FILE'])):
            os.makedirs(os.path.dirname(app.config['LOG_FILE']))

        file_handler = logging.FileHandler(app.config['LOG_FILE'])
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper(), logging.INFO))
        app.logger.info('VoIP Backend startup')

    @app.route('/health')
    def health_check():
        return "OK", 200

    return app

# To run the app (example, usually done with run.py or Gunicorn)
# if __name__ == '__main__':
#     app = create_app()
#     app.run()
