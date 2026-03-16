# voip_backend/tests/test_user_models.py

import pytest
from voip_backend.models.user_models import User
from voip_backend.extensions import db as dbs # Use alias to avoid conflict with db fixture

# Note: The 'session' fixture from conftest.py handles database setup and teardown (rollback)
# for each test function, ensuring test isolation.

def test_new_user_creation(session, new_user_payload):
    """
    Test creating a new User instance and saving it to the database.
    """
    user = User(
        username=new_user_payload['username'],
        email=new_user_payload['email'],
        first_name=new_user_payload['first_name'],
        last_name=new_user_payload['last_name']
    )
    user.set_password(new_user_payload['password']) # Use the method from User model

    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.username == new_user_payload['username']
    assert user.email == new_user_payload['email']
    assert user.first_name == new_user_payload['first_name']
    assert user.last_name == new_user_payload['last_name']
    assert user.is_active is True
    assert user.kyc_status == 'pending'
    assert user.password_hash is not None
    assert user.password_hash != new_user_payload['password'] # Ensure it's hashed

def test_user_password_hashing_and_checking(new_user_payload):
    """
    Test the set_password and check_password methods of the User model.
    This test doesn't need db interaction if methods are pure.
    """
    user = User()
    plain_password = new_user_payload['password']

    user.set_password(plain_password)
    assert user.password_hash is not None
    assert user.password_hash != plain_password

    assert user.check_password(plain_password) is True
    assert user.check_password("wrongpassword") is False
    assert user.check_password("") is False

def test_user_full_name_property(new_user_payload):
    """
    Test the full_name property of the User model.
    """
    # Case 1: Both first and last name are present
    user1 = User(first_name="John", last_name="Doe", username="johndoe")
    assert user1.full_name == "John Doe"

    # Case 2: Only first name is present
    user2 = User(first_name="Alice", username="alice")
    assert user2.full_name == "Alice"

    # Case 3: Only last name is present
    user3 = User(last_name="Smith", username="smith")
    assert user3.full_name == "Smith"

    # Case 4: Neither first nor last name is present, should return username
    user4 = User(username="testuser")
    assert user4.full_name == "testuser"

    # Case 5: All are None (should ideally not happen for username)
    user5 = User(username="fallback_user") # Username is required by model for DB
    user5.first_name = None
    user5.last_name = None
    assert user5.full_name == "fallback_user"


def test_user_repr_method(new_user_payload):
    """
    Test the __repr__ method of the User model.
    """
    user = User(id=1, username=new_user_payload['username'], email=new_user_payload['email'])
    expected_repr = f"<User id=1 username='{new_user_payload['username']}' email='{new_user_payload['email']}'>"
    assert repr(user) == expected_repr

def test_user_defaults(session):
    """
    Test default values for User model fields.
    """
    user = User(username="defaultuser", email="default@example.com")
    user.set_password("DefaultPass123")

    session.add(user)
    session.commit()

    assert user.is_active is True
    assert user.kyc_status == 'pending'
    assert user.created_at is not None
    assert user.updated_at is not None

def test_user_unique_constraints(session, new_user_payload, create_test_user):
    """
    Test unique constraints for username and email.
    Uses the create_test_user fixture to ensure one user is already in the DB.
    """
    # create_test_user fixture has already added a user with new_user_payload details.

    # Attempt to create a user with the same username
    user_same_username = User(
        username=new_user_payload['username'], # Same username
        email="another@example.com",
        password_hash="anotherhash" # Not using set_password to simplify for constraint test
    )
    session.add(user_same_username)
    with pytest.raises(Exception): # SQLAlchemy raises IntegrityError (or specific DB driver error)
        session.commit()
    session.rollback() # Important to rollback after expected error

    # Attempt to create a user with the same email
    user_same_email = User(
        username="anotheruser",
        email=new_user_payload['email'], # Same email
        password_hash="yetanotherhash"
    )
    session.add(user_same_email)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

# Add more tests as needed:
# - Test relationships if they have specific logic in the User model.
# - Test any other custom methods or properties on the User model.
# - Test behavior of onupdate for updated_at field.

def test_user_updated_at_on_change(session, create_test_user):
    """
    Test that updated_at is modified when a user record changes.
    """
    user = create_test_user # Get the user created by the fixture

    # Ensure user is in session or re-fetch
    user_from_db = session.query(User).get(user.id)
    assert user_from_db is not None

    original_updated_at = user_from_db.updated_at
    assert original_updated_at is not None

    # Make a change
    user_from_db.first_name = "UpdatedFirstName"
    session.commit()

    # Re-fetch or check current instance if session refreshes it
    session.refresh(user_from_db) # Ensure we get the DB-generated updated_at
    new_updated_at = user_from_db.updated_at

    assert new_updated_at is not None
    assert new_updated_at > original_updated_at

# Note: The `dbs` alias for `db` from extensions is used to avoid fixture name collision.
# In actual model code, it's just `db`. This is a test-specific aliasing.
# In `user_models.py` it's `from voip_backend.extensions import db`.
# If running this test directly, ensure the path allows `voip_backend` to be imported.
# Typically run with `pytest` from the root of the project or `voip_backend` parent dir.
