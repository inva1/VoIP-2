# voip_backend/tests/test_admin_api.py

import pytest


class TestAdminUsers:
    def test_list_users_as_admin(self, client, admin_auth_headers, create_test_user):
        resp = client.get('/api/admin/users', headers=admin_auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['total'] >= 2  # admin + test user

    def test_list_users_search(self, client, admin_auth_headers, create_test_user):
        resp = client.get('/api/admin/users?search=testuser', headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['total'] == 1

    def test_list_users_non_admin(self, client, auth_headers):
        resp = client.get('/api/admin/users', headers=auth_headers)
        assert resp.status_code == 403

    def test_list_users_no_auth(self, client):
        resp = client.get('/api/admin/users')
        assert resp.status_code == 401


class TestAdminUserStatus:
    def test_deactivate_user(self, client, admin_auth_headers, create_test_user):
        resp = client.put(f'/api/admin/users/{create_test_user.id}/status', json={
            'is_active': False
        }, headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['user']['is_active'] is False

    def test_activate_user(self, client, admin_auth_headers, create_test_user, db):
        create_test_user.is_active = False
        db.session.commit()
        resp = client.put(f'/api/admin/users/{create_test_user.id}/status', json={
            'is_active': True
        }, headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['user']['is_active'] is True

    def test_deactivate_user_non_admin(self, client, auth_headers, create_admin_user):
        resp = client.put(f'/api/admin/users/{create_admin_user.id}/status', json={
            'is_active': False
        }, headers=auth_headers)
        assert resp.status_code == 403


class TestAdminStats:
    def test_system_stats(self, client, admin_auth_headers, create_test_user):
        resp = client.get('/api/admin/stats', headers=admin_auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'total_users' in data
        assert 'active_subscriptions' in data
        assert 'pending_kyc' in data

    def test_stats_non_admin(self, client, auth_headers):
        resp = client.get('/api/admin/stats', headers=auth_headers)
        assert resp.status_code == 403


class TestAdminPlans:
    def test_create_plan(self, client, admin_auth_headers):
        resp = client.post('/api/admin/plans', json={
            'plan_code': 'PRO_UK',
            'plan_name': 'Pro UK Plan',
            'monthly_fee': 29.99,
            'included_minutes': 500,
            'included_messages': 200
        }, headers=admin_auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()['plan']['plan_code'] == 'PRO_UK'

    def test_create_plan_duplicate(self, client, admin_auth_headers):
        client.post('/api/admin/plans', json={
            'plan_code': 'DUP_PLAN',
            'plan_name': 'Duplicate',
            'monthly_fee': 5.0,
            'included_minutes': 10,
            'included_messages': 5
        }, headers=admin_auth_headers)
        resp = client.post('/api/admin/plans', json={
            'plan_code': 'DUP_PLAN',
            'plan_name': 'Another',
            'monthly_fee': 5.0,
            'included_minutes': 10,
            'included_messages': 5
        }, headers=admin_auth_headers)
        assert resp.status_code == 409

    def test_create_plan_non_admin(self, client, auth_headers):
        resp = client.post('/api/admin/plans', json={
            'plan_code': 'SNEAKY',
            'plan_name': 'Sneaky Plan',
            'monthly_fee': 0.01,
            'included_minutes': 9999,
            'included_messages': 9999
        }, headers=auth_headers)
        assert resp.status_code == 403

    def test_update_plan(self, client, admin_auth_headers, sample_plan):
        resp = client.put(f'/api/admin/plans/{sample_plan.id}', json={
            'plan_name': 'Updated Plan Name',
            'monthly_fee': 14.99
        }, headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['plan']['plan_name'] == 'Updated Plan Name'
