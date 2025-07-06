import os
from .app import create_app, db # Assuming app and db are in app.py
# Import models so Flask-Migrate can detect them
from .models.user_models import User, KYCRecord
from .models.subscription_models import SubscriptionPlan, UserSubscription
from .models.did_models import DIDNumber
from .models.call_models import CallDetailRecord, RegulatoryCDR
from .models.sms_models import SMSRecord

# Determine the configuration based on FLASK_ENV
# Default to DevelopmentConfig if FLASK_ENV is not set
flask_env = os.environ.get('FLASK_ENV', 'development')

if flask_env == 'production':
    from .config import ProductionConfig as AppConfig
elif flask_env == 'testing':
    from .config import TestingConfig as AppConfig
else:
    from .config import DevelopmentConfig as AppConfig

app = create_app(AppConfig)

# Example of how to add CLI commands for Flask-Migrate
# You might have a manage.py for this in larger apps,
# but for simplicity, it can be here or registered in create_app.

# @app.shell_context_processor
# def make_shell_context():
#     return {'db': db, 'User': User, 'KYCRecord': KYCRecord, # Add other models
#             'SubscriptionPlan': SubscriptionPlan, 'UserSubscription': UserSubscription,
#             'DIDNumber': DIDNumber, 'CallDetailRecord': CallDetailRecord,
#             'SMSRecord': SMSRecord, 'RegulatoryCDR': RegulatoryCDR}


if __name__ == '__main__':
    # This is primarily for development.
    # In production, Gunicorn will import 'app' from this module (or directly from app.py if structured differently)
    # and run it. Gunicorn typically looks for an 'app' callable or a WSGI application object.
    # The `app` variable here is the Flask application instance.

    # Ensure FLASK_APP=run.py (or your entry point) is set for flask commands
    # e.g., flask db init, flask db migrate, flask db upgrade

    # For Gunicorn, the command would be something like:
    # gunicorn -c gunicorn.conf.py run:app
    # where 'run' is this file (run.py) and 'app' is the Flask app instance created above.

    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

# Note: The provided design document has `run:app` for Gunicorn command.
# This means Gunicorn expects an `app` variable in `run.py` that is the Flask application.
# The current structure provides this.
# The Supervisor config also points to `run:app`.
# `environment=FLASK_ENV=production` in supervisor config will ensure ProductionConfig is loaded.
