# voip_backend/tests/test_user_models.py

import pytest
from voip_backend.models.user_models import User


class TestUserModel:
    def test_create_user(self, db):
        user = User(username='newuser', email='new@test.com')
        user.set_password('Test1234')
        db.session.add(user)
        db.session.flush()
        assert user.id is not None
        assert user.username == 'newuser'

    def test_password_hashing(self, db):
        user = User(username='hashtest', email='hash@test.com')
        user.set_password('MyPassword123')
        assert user.password_hash != 'MyPassword123'
        assert user.check_password('MyPassword123')
        assert not user.check_password('WrongPassword')

    def test_full_name_both(self, db):
        user = User(username='fn', email='fn@test.com', first_name='John', last_name='Doe')
        assert user.full_name == 'John Doe'

    def test_full_name_first_only(self, db):
        user = User(username='fn2', email='fn2@test.com', first_name='John')
        assert user.full_name == 'John'

    def test_full_name_fallback(self, db):
        user = User(username='fn3', email='fn3@test.com')
        assert user.full_name == 'fn3'

    def test_repr(self, db):
        user = User(username='reprtest', email='repr@test.com')
        assert 'reprtest' in repr(user)

    def test_defaults(self, db):
        user = User(username='defaults', email='def@test.com')
        user.set_password('Pass1234')
        db.session.add(user)
        db.session.flush()
        assert user.is_active is True
        assert user.kyc_status == 'pending'
        assert user.role == 'user'

    def test_is_admin(self, db):
        user = User(username='adm', email='adm@test.com', role='admin')
        assert user.is_admin is True

    def test_is_not_admin(self, db):
        user = User(username='reg', email='reg@test.com')
        assert user.is_admin is False
