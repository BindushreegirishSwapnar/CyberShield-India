import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_weather_forecast_endpoint(client):
    res = client.get('/api/v1/weather/forecast?state=Karnataka&age_group=Senior+Citizen+(60%2B)')
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'current_weather' in data
    assert 'risk_temperature' in data['current_weather']
    assert 0 <= data['current_weather']['risk_temperature'] <= 100
    assert 'seven_day_outlook' in data
    assert len(data['seven_day_outlook']) == 7
    assert 'personalized_advisory' in data
    assert data['is_synthetic'] is True

def test_weather_subscribe_endpoint(client):
    res = client.post('/api/v1/weather/subscribe', json={
        "state": "Maharashtra",
        "age_group": "Working Professional (26-59)"
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['status'] == 'success'
    assert 'active_subscription' in data
