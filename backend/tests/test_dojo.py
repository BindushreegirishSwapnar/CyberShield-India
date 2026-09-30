"""
Tests for Module 2: Scam Dojo Service and Endpoints
"""

import pytest
from app import create_app
from modules.dojo.dojo_service import dojo_service

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_scenarios(client):
    res = client.get('/api/v1/dojo/scenarios')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 4
    scenarios = {s["id"]: s for s in data["data"]}
    assert "digital_arrest" in scenarios
    assert "bank_kyc" in scenarios
    assert "AUTHORITY" in scenarios["digital_arrest"]["red_flags"]

def test_dojo_chat_resilient_turn(client):
    payload = {
        "scenario_id": "digital_arrest",
        "conversation_history": [
            {"role": "scammer", "content": "This is Mumbai Police. You are under Digital Arrest."}
        ],
        "user_message": "Digital arrest is illegal. I am calling helpline 1930 and visiting my local police station.",
        "elder_mode": False
    }
    res = client.post('/api/v1/dojo/chat', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    coach = data["data"]["coach_analysis"]
    assert "AUTHORITY" in coach["detected_red_flags"]
    assert coach["citizen_resilience_delta"] > 0
    assert len(data["data"]["suggested_counters"]) > 0

def test_dojo_final_evaluation(client):
    payload = {
        "scenario_id": "bank_kyc",
        "total_score": 45,
        "turns_played": 3,
        "elder_mode": False
    }
    res = client.post('/api/v1/dojo/evaluate', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["immunity_score"] >= 75
    assert "badge_name" in data
    assert "certificate" in data
    assert "cert_id" in data["certificate"]
