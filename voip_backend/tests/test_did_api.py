# voip_backend/tests/test_did_api.py

import pytest


class TestAvailableDIDs:
    def test_list_available_empty(self, client, auth_headers):
        resp = client.get('/api/dids/available', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_list_available_with_data(self, client, auth_headers, sample_did):
        resp = client.get('/api/dids/available', headers=auth_headers)
        assert resp.status_code == 200
        dids = resp.get_json()
        assert len(dids) == 1
        assert dids[0]['number'] == '+12025551234'

    def test_filter_by_country(self, client, auth_headers, sample_did):
        resp = client.get('/api/dids/available?country=USA', headers=auth_headers)
        assert len(resp.get_json()) == 1

        resp = client.get('/api/dids/available?country=GBR', headers=auth_headers)
        assert len(resp.get_json()) == 0


class TestAssignDID:
    def test_assign_success(self, client, auth_headers, sample_did):
        resp = client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['did']['status'] == 'assigned'

    def test_assign_already_assigned(self, client, auth_headers, sample_did):
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        resp = client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        assert resp.status_code == 409

    def test_assign_nonexistent(self, client, auth_headers):
        resp = client.post('/api/dids/assign', json={
            'did_id': 9999
        }, headers=auth_headers)
        assert resp.status_code == 404


class TestMyNumbers:
    def test_my_numbers_empty(self, client, auth_headers):
        resp = client.get('/api/dids/my-numbers', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_my_numbers_after_assign(self, client, auth_headers, sample_did):
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        resp = client.get('/api/dids/my-numbers', headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1


class TestReleaseDID:
    def test_release_success(self, client, auth_headers, sample_did):
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=auth_headers)
        resp = client.delete(f'/api/dids/release/{sample_did.id}', headers=auth_headers)
        assert resp.status_code == 200

    def test_release_not_owned(self, client, auth_headers, admin_auth_headers, sample_did):
        # Assign to admin
        client.post('/api/dids/assign', json={
            'did_id': sample_did.id
        }, headers=admin_auth_headers)
        # Try to release as regular user
        resp = client.delete(f'/api/dids/release/{sample_did.id}', headers=auth_headers)
        assert resp.status_code == 403
