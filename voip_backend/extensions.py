# voip_backend/extensions.py
"""
Flask extensions instances.

This module centralizes the initialization of Flask extensions to avoid circular imports
and provide a single point of reference for them. Extensions are initialized here
but configured and registered with the Flask app instance in the application factory
(e.g., in run.py or app.py).
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import redis

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
ma = Marshmallow()
cors = CORS()

# Redis client for JWT blocklisting and potentially other caching
# This will be instantiated in the app factory (create_app)
# and can be stored on app.extensions['redis_client'] if needed globally.
# For direct use in JWT callbacks, we'll access it via current_app.

# You could also add other extensions here if needed, e.g.:
# from flask_caching import Cache
# cache = Cache()
#
# from flask_mail import Mail
# mail = Mail()
#
# from celery import Celery # If using Celery
# celery = Celery() # Celery instance needs further configuration

# How to use in your app factory (e.g., create_app function):
#
# from .extensions import db, migrate, bcrypt, jwt, ma, cors
#
# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config) # Load your config
#
#     db.init_app(app)
#     migrate.init_app(app, db)
#     bcrypt.init_app(app)
#     jwt.init_app(app)
#     ma.init_app(app)
#     cors.init_app(app, resources={r"/api/*": {"origins": "*"}}) # Example CORS config
#
#     # Register blueprints, error handlers, etc.
#
#     return app
