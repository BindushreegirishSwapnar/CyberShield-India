"""
Unit tests for Module 6: Agentic Copilot Service and Endpoints
"""

import pytest
from app import create_app
from modules.agent.agent_service import agent_service

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_nl_bi_chart_generation(client):
    res = client.post('/api/v1/agent/chat', json={
        "prompt": "Show me a pie chart of top scam categories in Maharashtra where amount > 1 lakh"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["thinking_steps"]) >= 2
    assert data["inline_chart"] is not None
    assert data["inline_chart"]["chart_type"] == "pie"
    assert len(data["inline_chart"]["data"]) > 0

def test_case_diary_drafting(client):
    res = client.post('/api/v1/agent/chat', json={
        "prompt": "Draft Section 173 BNSS case diary for case CR-2026-98214"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["case_diary"] is not None
    assert "SECTION 173 BNSS" in data["case_diary"].upper()

def test_quick_command(client):
    res = client.post('/api/v1/agent/quick-command', json={
        "query": "Freeze"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["count"] >= 1
