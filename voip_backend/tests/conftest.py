# voip_backend/tests/conftest.py

import pytest
from voip_backend.run import create_app # Main app factory
from voip_backend.config import TestingConfig # Specific testing configuration
from voip_backend.extensions import db as _db # The SQLAlchemy db instance from your app

@pytest.fixture(scope='session')
def app():
    """
    Session-wide test Flask application.
    Uses TestingConfig which typically configures an in-memory SQLite database.
    """
    # _app = create_app(config_class=TestingConfig) # If create_app takes config_class
    _app = create_app(TestingConfig) # Pass the config object directly

    # Establish an application context before running the tests.
    ctx = _app.app_context()
    ctx.push()

    yield _app # Teardown is handled after the last test in the session

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """
    Session-wide test database.
    Ensures database is created and dropped once per session.
    """
    with app.app_context(): # Ensure we are within app context for db operations
        _db.create_all() # Create all tables based on models

    yield _db

    # Explicitly dropping is often not needed for in-memory SQLite as it vanishes,
    # but good practice for other DBs or if you want to be certain.
    # For SQLite in-memory, it's dropped when connection closes.
    # If using a persistent test DB:
    # _db.session.remove()
    # _db.drop_all()


@pytest.fixture(scope='function')
def session(db, app):
    """
    Function-scoped database session.
    Rolls back any changes after each test to ensure test isolation.
    """
    with app.app_context(): # Ensure app context for db session
        connection = db.engine.connect()
        transaction = connection.begin()

        # Bind the session to this transaction
        options = dict(bind=connection, binds={})
        sess = db.create_scoped_session(options=options)

        # Make this session the one used by db.session
        db.session = sess

        yield sess # Test runs with this session

        # Rollback and close
        sess.remove() # Or sess.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(app):
    """
    Test client for making requests to the Flask application.
    This uses the app fixture, so it operates within an app context.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Test CLI runner for invoking Flask CLI commands.
    """
    return app.test_cli_runner()


# Example fixture for creating a test user (can be expanded)
@pytest.fixture
def new_user_payload():
    """Provides a sample payload for creating a new user."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }

@pytest.fixture
def create_test_user(session, new_user_payload):
    """Fixture to create and save a test user."""
    from voip_backend.models.user_models import User

    # Check if user already exists to prevent issues if session fixture doesn't fully isolate
    user = User.query.filter_by(email=new_user_payload['email']).first()
    if user:
        return user # Return existing user if found (should ideally not happen with clean sessions)

    user = User(
        username=new_user_payload['username'],
        email=new_user_payload['email'],
        first_name=new_user_payload['first_name'],
        last_name=new_user_payload['last_name']
    )
    user.set_password(new_user_payload['password'])
    session.add(user)
    session.commit()
    return user

# Notes:
# - `scope='session'` means the fixture is created once per test session.
# - `scope='function'` means the fixture is created once per test function (default).
# - The `db` fixture depends on `app`. `session` depends on `db` and `app`.
# - The `session` fixture using transaction rollback is a common pattern for test isolation
#   with databases, ensuring each test starts with a clean slate without the overhead
#   of dropping and recreating tables for every test.
# - Ensure `TestingConfig` in `config.py` sets `SQLALCHEMY_DATABASE_URI` to an in-memory
#   SQLite database (e.g., 'sqlite:///:memory:') or a dedicated test database.
#   It should also set `TESTING = True`.
# - You might need to install `pytest-flask` if you haven't already (`pip install pytest-flask`).
#   However, these fixtures are written to work with standard pytest and Flask.
# - If your `create_app` expects `config_object` instead of `config_class`, adjust accordingly.
#   My `create_app` in `run.py` expects `config_object`.
# - The `_db` import alias is used to avoid conflict with the `db` fixture name.
# - The `create_test_user` fixture demonstrates how to create reusable test data setup.
