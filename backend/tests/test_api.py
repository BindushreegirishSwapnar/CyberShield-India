import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_root_endpoint(client):
    res = client.get('/')
    assert res.status_code == 200
    data = res.get_json()
    assert "CyberShield India" in data["project"]
    assert data["status"] == "online"

def test_provenance_endpoint(client):
    res = client.get('/api/v1/provenance')
    assert res.status_code == 200
    data = res.get_json()
    assert "provenance_metadata" in data
    assert data["provenance_metadata"]["india_complaint_dataset"]["total_records"] >= 5000

def test_system_health(client):
    res = client.get('/api/v1/system/health')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["services"]["database"]["status"] == "CONNECTED"
    assert data["services"]["ml_model"]["status"] == "READY"

def test_model_metrics(client):
    res = client.get('/api/v1/system/model-metrics')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "champion_algorithm" in data["data"]
    assert data["data"]["performance"]["accuracy"] >= 85.0

def test_cases_pagination_and_filter(client):
    res = client.get('/api/v1/cases?page=1&page_size=10')
    assert res.status_code == 200
    data = res.get_json()
    assert "data" in data
    assert len(data["data"]) == 10
    assert data["total"] >= 5000

def test_link_analysis_graph(client):
    res = client.get('/api/v1/intelligence/link-graph')
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert "nodes" in data
    assert "links" in data
    assert "clusters" in data
    assert len(data["clusters"]) > 0

def test_auth_login_validation(client):
    res = client.post('/api/v1/auth/login', json={"username": "admin", "password": "WrongPassword"})
    assert res.status_code == 401
