"""
Unit tests for Module 4: Money Trail Service and Endpoints
"""

import pytest
from app import create_app
from modules.moneytrail.moneytrail_service import moneytrail_service

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_fund_trail(client):
    res = client.get('/api/v1/moneytrail/trail/CR-2026-98214')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    trail = data["data"]
    assert len(trail["nodes"]) >= 5
    assert len(trail["links"]) >= 5
    assert len(trail["freeze_priority_ranking"]) > 0
    top = trail["freeze_priority_ranking"][0]
    assert top["freeze_priority_score"] >= 80

def test_simulate_dispersion(client):
    res = client.post('/api/v1/moneytrail/simulate', json={
        "case_id": "CR-2026-98214",
        "minutes_elapsed": 45
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    sim = data["data"]
    assert sim["minutes_elapsed"] == 45
    assert "recoverable_amount" in sim
    assert sim["drain_status"] == "GOLDEN_HOUR_ACTIVE"

def test_generate_statutory_notice(client):
    res = client.post('/api/v1/moneytrail/generate-notice', json={
        "case_id": "CR-2026-98214",
        "mule_account": "104928172901",
        "bank_name": "Canara Bank",
        "officer_name": "Inspector Rajesh Kumar",
        "badge_no": "KA-CYBER-8841"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    notice = data["data"]
    assert "SECTION 94 BNSS" in notice["notice_text"].upper()
    assert "Section 79(3)(b)" in notice["notice_text"]
    assert len(notice["digital_seal_hash"]) == 64

