# voip_backend/tests/test_subscription_api.py

import pytest


class TestListPlans:
    def test_list_plans_empty(self, client):
        resp = client.get('/api/subscriptions/plans')
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_plans_with_data(self, client, sample_plan):
        resp = client.get('/api/subscriptions/plans')
        assert resp.status_code == 200
        plans = resp.get_json()
        assert len(plans) == 1
        assert plans[0]['plan_code'] == 'BASIC_US'

    def test_list_plans_filter_country(self, client, sample_plan):
        resp = client.get('/api/subscriptions/plans?country=USA')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

        resp = client.get('/api/subscriptions/plans?country=GBR')
        assert resp.status_code == 200
        assert len(resp.get_json()) == 0


class TestSubscribe:
    def test_subscribe_success(self, client, auth_headers, sample_plan):
        resp = client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        assert resp.status_code == 201
        assert resp.get_json()['subscription']['status'] == 'active'

    def test_subscribe_invalid_plan(self, client, auth_headers):
        resp = client.post('/api/subscriptions/subscribe', json={
            'plan_id': 9999
        }, headers=auth_headers)
        assert resp.status_code == 404

    def test_subscribe_duplicate(self, client, auth_headers, sample_plan):
        client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        resp = client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        assert resp.status_code == 409

    def test_subscribe_no_auth(self, client, sample_plan):
        resp = client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        })
        assert resp.status_code == 401


class TestCurrentSubscription:
    def test_no_subscription(self, client, auth_headers):
        resp = client.get('/api/subscriptions/current', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['message'] == 'No active subscription.'

    def test_with_subscription(self, client, auth_headers, sample_plan):
        client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        resp = client.get('/api/subscriptions/current', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['plan_id'] == sample_plan.id


class TestCancelSubscription:
    def test_cancel_success(self, client, auth_headers, sample_plan):
        client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        resp = client.put('/api/subscriptions/cancel', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['subscription']['status'] == 'cancelled'

    def test_cancel_no_subscription(self, client, auth_headers):
        resp = client.put('/api/subscriptions/cancel', headers=auth_headers)
        assert resp.status_code == 404


class TestUsage:
    def test_usage_with_subscription(self, client, auth_headers, sample_plan):
        client.post('/api/subscriptions/subscribe', json={
            'plan_id': sample_plan.id
        }, headers=auth_headers)
        resp = client.get('/api/subscriptions/usage', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['remaining_minutes'] == 100
        assert data['remaining_messages'] == 50
