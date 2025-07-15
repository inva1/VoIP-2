# voip_backend/tests/test_auth_api.py

import json
import pytest
from flask_jwt_extended import decode_token
from voip_backend.models.user_models import User

# Fixtures like `client`, `session`, `new_user_payload`, `create_test_user` are from conftest.py

# --- Registration Tests (/api/auth/register) ---

def test_register_user_success(client, session, new_user_payload):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json=new_user_payload)

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "User registered successfully."
    assert 'user' in json_data
    assert json_data['user']['username'] == new_user_payload['username']
    assert json_data['user']['email'] == new_user_payload['email']
    assert 'id' in json_data['user']

    # Verify user is in database
    user = User.query.filter_by(email=new_user_payload['email']).first()
    assert user is not None
    assert user.username == new_user_payload['username']

def test_register_user_missing_fields(client):
    """Test registration with missing required fields."""
    payload = {"username": "test", "email": "test@example.com"} # Missing password
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 422
    json_data = response.get_json()
    assert "password" in json_data['messages']

def test_register_user_invalid_email(client, new_user_payload):
    """Test registration with an invalid email format."""
    payload = new_user_payload.copy()
    payload['email'] = "not-an-email"
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 422
    json_data = response.get_json()
    assert "email" in json_data['messages']

def test_register_user_password_too_short(client, new_user_payload):
    """Test registration with a password that's too short."""
    payload = new_user_payload.copy()
    payload['password'] = "short"
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 422
    json_data = response.get_json()
    assert "password" in json_data['messages'] # Assuming custom validator message implies this

def test_register_user_duplicate_username(client, create_test_user, new_user_payload):
    """Test registration with a username that already exists."""
    # create_test_user fixture already created a user with new_user_payload['username']
    payload = new_user_payload.copy()
    payload['email'] = "anotheremail@example.com" # Different email
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 409
    json_data = response.get_json()
    assert "username" in json_data['messages']

def test_register_user_duplicate_email(client, create_test_user, new_user_payload):
    """Test registration with an email that already exists."""
    payload = new_user_payload.copy()
    payload['username'] = "anotherusername" # Different username
    response = client.post('/api/auth/register', json=payload)
    assert response.status_code == 409
    json_data = response.get_json()
    assert "email" in json_data['messages']

# --- Login Tests (/api/auth/login) ---

def test_login_user_success(client, create_test_user, new_user_payload):
    """Test successful user login."""
    login_payload = {
        "email": new_user_payload['email'],
        "password": new_user_payload['password']
    }
    response = client.post('/api/auth/login', json=login_payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Login successful."
    assert 'access_token' in json_data
    assert 'refresh_token' in json_data
    assert 'user' in json_data
    assert json_data['user']['email'] == new_user_payload['email']

    # Verify last_login was updated (difficult to assert exact time without mocking)
    user = User.query.filter_by(email=new_user_payload['email']).first()
    assert user.last_login is not None

def test_login_user_wrong_password(client, create_test_user, new_user_payload):
    """Test login with an incorrect password."""
    login_payload = {
        "email": new_user_payload['email'],
        "password": "wrongpassword"
    }
    response = client.post('/api/auth/login', json=login_payload)
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "Invalid email or password."

def test_login_user_nonexistent_email(client, new_user_payload):
    """Test login with an email that does not exist."""
    login_payload = {
        "email": "nonexistent@example.com",
        "password": new_user_payload['password']
    }
    response = client.post('/api/auth/login', json=login_payload)
    assert response.status_code == 401 # Or 404 if you distinguish, but 401 is common for auth failure
    json_data = response.get_json()
    assert json_data['message'] == "Invalid email or password."

def test_login_user_inactive(client, session, new_user_payload):
    """Test login for an inactive user."""
    user = User(
        username="inactiveuser", email="inactive@example.com", is_active=False
    )
    user.set_password(new_user_payload["password"])
    session.add(user)
    session.commit()

    login_payload = {"email": "inactive@example.com", "password": new_user_payload["password"]}
    response = client.post('/api/auth/login', json=login_payload)
    assert response.status_code == 401
    json_data = response.get_json()
    assert json_data['message'] == "Account is inactive."


# --- Token Refresh Tests (/api/auth/refresh) ---

def test_refresh_token_success(client, create_test_user, new_user_payload):
    """Test successful token refresh."""
    # First, log in to get a refresh token
    login_payload = {"email": new_user_payload['email'], "password": new_user_payload['password']}
    login_response = client.post('/api/auth/login', json=login_payload)
    assert login_response.status_code == 200
    refresh_token = login_response.get_json()['refresh_token']

    # Use the refresh token to get a new access token
    refresh_response = client.post(
        '/api/auth/refresh',
        headers={'Authorization': f'Bearer {refresh_token}'}
    )
    assert refresh_response.status_code == 200
    json_data = refresh_response.get_json()
    assert 'access_token' in json_data

def test_refresh_token_with_access_token_fails(client, create_test_user, new_user_payload):
    """Test attempting to refresh using an access token (should fail)."""
    login_payload = {"email": new_user_payload['email'], "password": new_user_payload['password']}
    login_response = client.post('/api/auth/login', json=login_payload)
    access_token = login_response.get_json()['access_token']

    refresh_response = client.post(
        '/api/auth/refresh',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    assert refresh_response.status_code == 422 # "Only refresh tokens are allowed"
    json_data = refresh_response.get_json()
    assert "Only refresh tokens are allowed" in json_data.get("msg", "")


def test_refresh_token_no_token(client):
    """Test refresh endpoint without providing a token."""
    response = client.post('/api/auth/refresh')
    assert response.status_code == 401 # "Missing Authorization Header"
    json_data = response.get_json()
    assert "Missing Authorization Header" in json_data.get("msg", "")


def test_refresh_token_invalid_token(client):
    """Test refresh endpoint with an invalid/malformed token."""
    response = client.post(
        '/api/auth/refresh',
        headers={'Authorization': 'Bearer invalidtokenstring'}
    )
    assert response.status_code == 422 # "Invalid token format" or similar
    json_data = response.get_json()
    assert "Invalid header padding" in json_data.get("msg", "") # Example msg for bad token


# --- Logout Tests (/api/auth/logout) ---
# These tests depend on Redis being available and configured for blocklisting.
# The conftest.py currently doesn't mock Redis for JWT blocklist.
# For true unit tests, Redis interactions should be mocked.
# For integration-style tests (as these are becoming), a test Redis instance is needed.
# Assuming TestingConfig might point to a real (test) Redis or these tests might need adjustment.

@pytest.mark.usefixtures("app_context") # Ensure app context for config access
def test_logout_user_success_with_access_token(client, create_test_user, new_user_payload, app):
    """Test successful logout using an access token."""
    # Login to get tokens
    login_payload = {"email": new_user_payload['email'], "password": new_user_payload['password']}
    login_res = client.post('/api/auth/login', json=login_payload)
    access_token = login_res.get_json()['access_token']

    # Logout
    logout_res = client.post('/api/auth/logout', headers={'Authorization': f'Bearer {access_token}'})
    assert logout_res.status_code == 200
    assert logout_res.get_json()['message'] == "Logout successful. Token has been invalidated."

    # Verify token is blocklisted (check Redis - requires Redis client and app context)
    # This part is more of an integration test.
    redis_cli = app.extensions.get('redis_client')
    if redis_cli: # Only run if Redis is configured
        decoded_token = decode_token(access_token)
        jti = decoded_token['jti']
        assert redis_cli.get(f"jti:{jti}") == "revoked"
    else:
        pytest.skip("Redis client not configured, skipping blocklist check for logout.")


@pytest.mark.usefixtures("app_context")
def test_logout_user_success_with_refresh_token(client, create_test_user, new_user_payload, app):
    """Test successful logout using a refresh token."""
    login_payload = {"email": new_user_payload['email'], "password": new_user_payload['password']}
    login_res = client.post('/api/auth/login', json=login_payload)
    refresh_token = login_res.get_json()['refresh_token']

    logout_res = client.post('/api/auth/logout', headers={'Authorization': f'Bearer {refresh_token}'})
    assert logout_res.status_code == 200
    assert logout_res.get_json()['message'] == "Logout successful. Token has been invalidated."

    redis_cli = app.extensions.get('redis_client')
    if redis_cli:
        decoded_token = decode_token(refresh_token)
        jti = decoded_token['jti']
        assert redis_cli.get(f"jti:{jti}") == "revoked"
    else:
        pytest.skip("Redis client not configured, skipping blocklist check for logout.")


def test_logout_user_no_token(client):
    """Test logout without providing a token."""
    response = client.post('/api/auth/logout')
    assert response.status_code == 401 # Missing Authorization Header
    json_data = response.get_json()
    assert "Missing Authorization Header" in json_data.get("msg", "")


# Fixture to push app context for tests that need it directly for config/extensions
@pytest.fixture
def app_context(app):
    with app.app_context():
        yield
