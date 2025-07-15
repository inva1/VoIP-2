# voip_backend/api/__init__.py

# This file makes the 'api' directory a Python package.

"""
This package contains all the API blueprints for the VoIP backend application.
Each sub-package (e.g., auth, users, kyc) will define its own blueprint
and routes related to that specific domain.
"""

# You can import and register blueprints here in a main app factory,
# or register them directly from the app factory by importing from submodules.
# For example, in your main app.py or run.py:
#
# from voip_backend.api.auth.routes import auth_bp
# from voip_backend.api.users.routes import users_bp
# ...
#
# def register_blueprints(app):
#     app.register_blueprint(auth_bp, url_prefix='/api/auth')
#     app.register_blueprint(users_bp, url_prefix='/api/users')
#     ...
#
# This approach is generally preferred to keep __init__.py clean.
