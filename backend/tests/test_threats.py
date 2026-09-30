"""
Unit tests for Module 5: Emerging Threat Detector Service and Endpoints
"""

import pytest
from app import create_app
from modules.threats.threat_cluster_service import threat_service

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_clusters(client):
    res = client.get('/api/v1/threats/clusters')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert len(data["clusters"]) >= 3
    assert "drift_telemetry" in data
    assert data["drift_telemetry"]["baseline_accuracy_pct"] > 90

def test_approve_category(client):
    res = client.post('/api/v1/threats/approve-category', json={
        "cluster_id": "CLUST-07"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["cluster"]["status"] == "APPROVED"

def test_retrain_model(client):
    res = client.post('/api/v1/threats/retrain')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["new_accuracy_pct"] >= 95.0
