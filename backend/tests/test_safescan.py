"""
Unit tests for Module 3: Safe-Scan Service and Endpoints
"""

import pytest
from app import create_app
from modules.safescan.safescan_service import safescan_service

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_lookalike_domain_detection():
    # Official domain
    res_off = safescan_service.check_lookalike_domain("https://www.sbi.co.in/portal")
    assert res_off["is_official"] is True
    assert res_off["risk_rating"] == "SAFE"

    # Impersonation lookalike domain
    res_fake = safescan_service.check_lookalike_domain("http://sbi-kyc-verification.xyz/login")
    assert res_fake["is_lookalike"] is True
    assert res_fake["risk_rating"] in ("SUSPICIOUS", "DANGEROUS")

def test_upi_qr_parsing():
    # Mismatch: Institutional Name with Personal VPA
    fake_qr = "upi://pay?pa=fraudster99@ybl&pn=Mahavitaran%20Electricity%20Board&am=1200&cu=INR"
    parsed = safescan_service.parse_upi_qr(fake_qr)
    assert parsed["is_valid_upi_qr"] is True
    assert parsed["mismatch_detected"] is True
    assert parsed["risk_verdict"] in ("SUSPICIOUS", "MALICIOUS")

def test_lookup_endpoint(client):
    res = client.post('/api/v1/safescan/lookup', json={
        "entity_type": "phone",
        "entity_value": "9876543210"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "verdict" in data["data"]
    assert "complaint_count" in data["data"]

def test_ocr_analyze_endpoint(client):
    ocr_sample = "Urgent: Your SBI NetBanking locked. Update KYC at http://sbi-account-kyc.com or call 9876543210. Pay fine to billpay@okhdfcbank."
    res = client.post('/api/v1/safescan/ocr-analyze', json={
        "text": ocr_sample
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["data"]["entities_found"]["phones_count"] >= 1
    assert data["data"]["entities_found"]["upis_count"] >= 1
    assert data["data"]["overall_verdict"] in ("MALICIOUS", "SUSPICIOUS")
