# voip_backend/tests/test_kyc_api.py

import pytest


class TestKYCSubmit:
    def test_submit_kyc_success(self, client, auth_headers):
        resp = client.post('/api/kyc/submit', json={
            'document_type': 'passport',
            'document_number': 'AB123456',
            'document_country': 'USA',
            'document_front_url': 'https://storage.example.com/front.jpg',
            'selfie_url': 'https://storage.example.com/selfie.jpg'
        }, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['kyc_record']['verification_status'] == 'pending'

    def test_submit_kyc_invalid_doc_type(self, client, auth_headers):
        resp = client.post('/api/kyc/submit', json={
            'document_type': 'invalid_type',
            'document_number': 'AB123456',
            'document_country': 'USA'
        }, headers=auth_headers)
        assert resp.status_code == 422

    def test_submit_kyc_missing_fields(self, client, auth_headers):
        resp = client.post('/api/kyc/submit', json={}, headers=auth_headers)
        assert resp.status_code in (400, 422)

    def test_submit_kyc_duplicate_pending(self, client, auth_headers):
        client.post('/api/kyc/submit', json={
            'document_type': 'passport',
            'document_number': 'AB123456',
            'document_country': 'USA'
        }, headers=auth_headers)
        # Second submission should be rejected
        resp = client.post('/api/kyc/submit', json={
            'document_type': 'national_id',
            'document_number': 'CD789012',
            'document_country': 'USA'
        }, headers=auth_headers)
        assert resp.status_code == 409

    def test_submit_kyc_no_auth(self, client):
        resp = client.post('/api/kyc/submit', json={
            'document_type': 'passport',
            'document_number': 'AB123456',
            'document_country': 'USA'
        })
        assert resp.status_code == 401


class TestKYCStatus:
    def test_get_kyc_status(self, client, auth_headers):
        resp = client.get('/api/kyc/status', headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data['kyc_status'] == 'pending'


class TestKYCRecords:
    def test_get_kyc_records_empty(self, client, auth_headers):
        resp = client.get('/api/kyc/records', headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_get_kyc_records_after_submit(self, client, auth_headers):
        client.post('/api/kyc/submit', json={
            'document_type': 'passport',
            'document_number': 'AB123456',
            'document_country': 'USA'
        }, headers=auth_headers)
        resp = client.get('/api/kyc/records', headers=auth_headers)
        assert resp.status_code == 200
        records = resp.get_json()
        assert len(records) == 1


class TestKYCReview:
    def test_review_kyc_approve(self, client, admin_auth_headers, auth_headers):
        # Submit KYC as regular user
        submit_resp = client.post('/api/kyc/submit', json={
            'document_type': 'passport',
            'document_number': 'AB123456',
            'document_country': 'USA'
        }, headers=auth_headers)
        record_id = submit_resp.get_json()['kyc_record']['id']

        # Review as admin
        resp = client.put(f'/api/kyc/review/{record_id}', json={
            'verification_status': 'approved',
            'risk_score': 10,
            'notes': 'Looks good.'
        }, headers=admin_auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()['kyc_record']['verification_status'] == 'approved'

    def test_review_kyc_non_admin(self, client, auth_headers):
        resp = client.put('/api/kyc/review/1', json={
            'verification_status': 'approved'
        }, headers=auth_headers)
        assert resp.status_code == 403
