# voip_backend/tests/test_user_api.py

import json
import pytest
from voip_backend.models.user_models import User

# Fixtures `client`, `session`, `new_user_payload`, `create_test_user` from conftest.py

# --- Helper to get auth headers ---
def get_auth_headers(client, email, password):
    """Logs in a user and returns JWT access token in auth headers."""
    login_payload = {"email": email, "password": password}
    response = client.post('/api/auth/login', json=login_payload)
    if response.status_code != 200:
        raise Exception(f"Login failed for token generation: {response.get_data(as_text=True)}")
    access_token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {access_token}'}

# --- Get User Profile Tests (/api/users/me) ---

def test_get_user_profile_success(client, create_test_user, new_user_payload):
    """Test successfully getting the current user's profile."""
    user = create_test_user # Ensure user exists
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    response = client.get('/api/users/me', headers=headers)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['username'] == new_user_payload['username']
    assert json_data['email'] == new_user_payload['email']
    assert json_data['first_name'] == new_user_payload['first_name']
    assert 'password_hash' not in json_data # Ensure sensitive data is not exposed

def test_get_user_profile_no_auth(client):
    """Test getting user profile without authentication token."""
    response = client.get('/api/users/me')
    assert response.status_code == 401 # Missing Authorization Header
    json_data = response.get_json()
    assert "Missing Authorization Header" in json_data.get("msg", "")

def test_get_user_profile_invalid_token(client):
    """Test getting user profile with an invalid token."""
    headers = {'Authorization': 'Bearer invalidtoken'}
    response = client.get('/api/users/me', headers=headers)
    assert response.status_code == 422 # Invalid token format
    json_data = response.get_json()
    assert "Invalid header padding" in json_data.get("msg","") # Example msg

# --- Update User Profile Tests (/api/users/me) ---

def test_update_user_profile_success(client, create_test_user, new_user_payload, session):
    """Test successfully updating parts of the user's profile."""
    user = create_test_user
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    update_payload = {
        "first_name": "UpdatedFirstName",
        "phone_number": "1234567890"
    }
    response = client.put('/api/users/me', headers=headers, json=update_payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "Profile updated successfully."
    assert json_data['user']['first_name'] == "UpdatedFirstName"
    assert json_data['user']['phone_number'] == "1234567890"
    assert json_data['user']['last_name'] == new_user_payload['last_name'] # Unchanged

    # Verify in DB
    updated_user = session.query(User).get(user.id)
    assert updated_user.first_name == "UpdatedFirstName"
    assert updated_user.phone_number == "1234567890"

def test_update_user_profile_partial_update(client, create_test_user, new_user_payload, session):
    """Test updating only one field of the user's profile."""
    user = create_test_user
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    update_payload = {"country_code": "USA"}
    response = client.put('/api/users/me', headers=headers, json=update_payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['user']['country_code'] == "USA"
    assert json_data['user']['first_name'] == new_user_payload['first_name'] # Unchanged

    updated_user = session.query(User).get(user.id)
    assert updated_user.country_code == "USA"

def test_update_user_profile_invalid_data(client, create_test_user, new_user_payload):
    """Test updating profile with invalid data (e.g., too long string)."""
    user = create_test_user
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    update_payload = {"first_name": "a" * 101} # Assuming max_length is 100
    response = client.put('/api/users/me', headers=headers, json=update_payload)

    assert response.status_code == 422
    json_data = response.get_json()
    assert "first_name" in json_data['messages']

def test_update_user_profile_no_data(client, create_test_user, new_user_payload):
    """Test updating profile with an empty JSON payload."""
    user = create_test_user
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    response = client.put('/api/users/me', headers=headers, json={})
    # The current implementation returns 200 with "No update data provided."
    # Depending on desired behavior, this could also be a 400.
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == "No update data provided."


def test_update_user_profile_no_auth(client):
    """Test updating profile without authentication."""
    update_payload = {"first_name": "AnonymousUpdate"}
    response = client.put('/api/users/me', json=update_payload)
    assert response.status_code == 401

def test_update_user_profile_attempt_to_update_restricted_fields(client, create_test_user, new_user_payload, session):
    """Test attempting to update fields not allowed by UserUpdateSchema (e.g., email, username)."""
    user = create_test_user
    headers = get_auth_headers(client, new_user_payload['email'], new_user_payload['password'])

    update_payload = {
        "email": "new_email_should_be_ignored@example.com",
        "username": "new_username_should_be_ignored",
        "first_name": "StillUpdatedFirstName" # A valid field to ensure others are ignored
    }
    response = client.put('/api/users/me', headers=headers, json=update_payload)

    assert response.status_code == 200 # Schema ignores unknown fields by default
    json_data = response.get_json()
    assert json_data['user']['first_name'] == "StillUpdatedFirstName"
    assert json_data['user']['email'] == new_user_payload['email'] # Should be unchanged
    assert json_data['user']['username'] == new_user_payload['username'] # Should be unchanged

    # Verify in DB
    db_user = session.query(User).get(user.id)
    assert db_user.first_name == "StillUpdatedFirstName"
    assert db_user.email == new_user_payload['email']
    assert db_user.username == new_user_payload['username']

# Add more tests as needed:
# - Test behavior for inactive users trying to update profile (should be forbidden).
# - Test specific validation rules in UserUpdateSchema if more are added.
