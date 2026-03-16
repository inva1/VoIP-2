# voip_backend/tests/test_call_sms_api.py

import pytest


class TestCallHistory:
    def test_call_history_empty(self, client, auth_headers):
        resp = client.get('/api/calls/history', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['calls'] == []
        assert data['total'] == 0

    def test_call_history_no_auth(self, client):
        resp = client.get('/api/calls/history')
        assert resp.status_code == 401


class TestSMSSend:
    def test_send_sms_no_did(self, client, auth_headers):
        """Should fail if user has no DID assigned."""
        resp = client.post('/api/sms/send', json={
            'to_number': '+14155551234',
            'message_text': 'Hello!'
        }, headers=auth_headers)
        assert resp.status_code == 412  # No DID assigned

    def test_send_sms_success(self, client, auth_headers, sample_did):
        # Assign DID first
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        # Send SMS
        resp = client.post('/api/sms/send', json={
            'to_number': '+14155551234',
            'message_text': 'Hello from VoIP!'
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['sms']['status'] == 'sent'
        assert data['sms']['direction'] == 'outbound'

    def test_send_sms_missing_fields(self, client, auth_headers):
        resp = client.post('/api/sms/send', json={}, headers=auth_headers)
        assert resp.status_code in (400, 422)

    def test_send_sms_no_auth(self, client):
        resp = client.post('/api/sms/send', json={
            'to_number': '+14155551234',
            'message_text': 'Hello!'
        })
        assert resp.status_code == 401


class TestSMSHistory:
    def test_sms_history_empty(self, client, auth_headers):
        resp = client.get('/api/sms/history', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['messages'] == []

    def test_sms_history_after_send(self, client, auth_headers, sample_did):
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        client.post('/api/sms/send', json={
            'to_number': '+14155551234',
            'message_text': 'Test message'
        }, headers=auth_headers)
        resp = client.get('/api/sms/history', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['total'] == 1
