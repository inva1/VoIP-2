# voip_backend/models/__init__.py

# This file makes the 'models' directory a Python package.

# You can import specific models here to make them easier to access, e.g.:
# from .user_models import User
# from .kyc_models import KYCRecord
# ... and so on.

# Or, more commonly, you'd import the `db` instance here if it's defined in this package,
# but we'll define it in `extensions.py` to avoid circular imports with blueprints/app.

# For now, this file can remain empty or just contain a docstring.
"""
SQLAlchemy models for the VoIP Backend application.
Each file in this package typically defines models related to a specific
functional area (e.g., users, subscriptions, calls).
"""
