# voip_backend/tests/test_user_api.py

import pytest


class TestGetProfile:
    def test_get_profile_success(self, client, auth_headers):
        resp = client.get('/api/users/me', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['username'] == 'testuser'
        assert data['email'] == 'test@example.com'
        assert 'password_hash' not in data

    def test_get_profile_no_token(self, client):
        resp = client.get('/api/users/me')
        assert resp.status_code == 401


class TestUpdateProfile:
    def test_update_profile_success(self, client, auth_headers):
        resp = client.put('/api/users/me', json={
            'first_name': 'Updated',
            'last_name': 'Name'
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['first_name'] == 'Updated'

    def test_update_profile_partial(self, client, auth_headers):
        resp = client.put('/api/users/me', json={
            'phone_number': '+1234567890'
        }, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['phone_number'] == '+1234567890'

    def test_update_profile_no_token(self, client):
        resp = client.put('/api/users/me', json={'first_name': 'X'})
        assert resp.status_code == 401

    def test_update_restricted_fields(self, client, auth_headers):
        resp = client.put('/api/users/me', json={
            'username': 'hackerusername',
            'email': 'hacker@example.com'
        }, headers=auth_headers)
        # Should succeed but not update restricted fields
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
