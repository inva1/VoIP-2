# voip_backend/tests/test_auth_api.py

import pytest


class TestRegister:
    def test_register_success(self, client, new_user_payload):
        resp = client.post('/api/auth/register', json=new_user_payload)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['message'] == 'User registered successfully.'
        assert data['user']['username'] == new_user_payload['username']

    def test_register_missing_fields(self, client):
        resp = client.post('/api/auth/register', json={"username": "onlyname"})
        assert resp.status_code == 422

    def test_register_invalid_email(self, client, new_user_payload):
        payload = {**new_user_payload, 'email': 'not-an-email'}
        resp = client.post('/api/auth/register', json=payload)
        assert resp.status_code == 422

    def test_register_weak_password(self, client, new_user_payload):
        payload = {**new_user_payload, 'password': 'short'}
        resp = client.post('/api/auth/register', json=payload)
        assert resp.status_code == 422

    def test_register_duplicate_username(self, client, create_test_user, new_user_payload):
        payload = {**new_user_payload, 'email': 'different@example.com'}
        resp = client.post('/api/auth/register', json=payload)
        assert resp.status_code == 409

    def test_register_duplicate_email(self, client, create_test_user, new_user_payload):
        payload = {**new_user_payload, 'username': 'different_user'}
        resp = client.post('/api/auth/register', json=payload)
        assert resp.status_code == 409

    def test_register_no_body(self, client):
        resp = client.post('/api/auth/register', content_type='application/json')
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client, create_test_user, new_user_payload):
        resp = client.post('/api/auth/login', json={
            'email': new_user_payload['email'],
            'password': new_user_payload['password']
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_wrong_password(self, client, create_test_user, new_user_payload):
        resp = client.post('/api/auth/login', json={
            'email': new_user_payload['email'],
            'password': 'WrongPassword123'
        })
        assert resp.status_code == 401

    def test_login_nonexistent_email(self, client):
        resp = client.post('/api/auth/login', json={
            'email': 'nobody@example.com',
            'password': 'whatever'
        })
        assert resp.status_code == 401

    def test_login_inactive_user(self, client, create_test_user, new_user_payload, db):
        create_test_user.is_active = False
        db.session.commit()
        resp = client.post('/api/auth/login', json={
            'email': new_user_payload['email'],
            'password': new_user_payload['password']
        })
        assert resp.status_code == 401

    def test_login_no_body(self, client):
        resp = client.post('/api/auth/login', content_type='application/json')
        assert resp.status_code == 400


class TestRefresh:
    def test_refresh_success(self, client, create_test_user, new_user_payload):
        login = client.post('/api/auth/login', json={
            'email': new_user_payload['email'],
            'password': new_user_payload['password']
        })
        refresh_token = login.get_json()['refresh_token']
        resp = client.post('/api/auth/refresh', headers={
            'Authorization': f'Bearer {refresh_token}'
        })
        assert resp.status_code == 200
        assert 'access_token' in resp.get_json()

    def test_refresh_with_access_token(self, client, auth_headers):
        resp = client.post('/api/auth/refresh', headers=auth_headers)
        assert resp.status_code == 422  # Wrong token type
