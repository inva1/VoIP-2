# voip_backend/tests/conftest.py

import pytest
from voip_backend.run import create_app
from voip_backend.config import TestingConfig
from voip_backend.extensions import db as _db


@pytest.fixture(scope='session')
def app():
    """Session-wide test Flask application."""
    _app = create_app(TestingConfig)
    ctx = _app.app_context()
    ctx.push()
    yield _app
    ctx.pop()


@pytest.fixture(autouse=True)
def db(app):
    """
    Per-test database setup: recreate all tables before each test
    and drop them after. This ensures complete isolation with SQLite.
    """
    _db.create_all()
    yield _db
    _db.session.remove()
    _db.drop_all()


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Test CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def new_user_payload():
    """Sample user registration payload."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def create_test_user(db, new_user_payload):
    """Create and return a test user."""
    from voip_backend.models.user_models import User
    user = User(
        username=new_user_payload['username'],
        email=new_user_payload['email'],
        first_name=new_user_payload['first_name'],
        last_name=new_user_payload['last_name']
    )
    user.set_password(new_user_payload['password'])
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def create_admin_user(db):
    """Create and return an admin user."""
    from voip_backend.models.user_models import User
    admin = User(
        username="adminuser",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role="admin"
    )
    admin.set_password("AdminPass123")
    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def auth_headers(client, create_test_user, new_user_payload):
    """Get JWT auth headers for the test user."""
    resp = client.post('/api/auth/login', json={
        'email': new_user_payload['email'],
        'password': new_user_payload['password']
    })
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_auth_headers(client, create_admin_user):
    """Get JWT auth headers for the admin user."""
    resp = client.post('/api/auth/login', json={
        'email': 'admin@example.com',
        'password': 'AdminPass123'
    })
    token = resp.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_plan(db):
    """Create a sample subscription plan."""
    from voip_backend.models.subscription_models import SubscriptionPlan
    plan = SubscriptionPlan(
        plan_code='BASIC_US',
        plan_name='Basic US Plan',
        description='Basic plan for US users',
        target_country='USA',
        monthly_fee=9.99,
        included_minutes=100,
        included_messages=50,
        overage_rate_voice=0.05,
        overage_rate_sms=0.02,
    )
    db.session.add(plan)
    db.session.commit()
    return plan


@pytest.fixture
def sample_did(db):
    """Create a sample available DID."""
    from voip_backend.models.did_models import DIDNumber
    did = DIDNumber(
        number='+12025551234',
        country_code='USA',
        area_code='202',
        number_type='local',
        provider='TestProvider',
        monthly_cost=4.99,
        status='available',
    )
    db.session.add(did)
    db.session.commit()
    return did
