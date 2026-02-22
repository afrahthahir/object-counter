import pytest
from counter.entrypoints.webapp import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_object_count_missing_file(client):
    response = client.post('/object-count', data={})
    assert response.status_code == 400
    assert response.json['error'] == "No file part in the request"

def test_object_count_invalid_threshold(client):
    data = {'threshold': 'invalid'}
    data['file'] = (open('README.md', 'rb'), 'test.txt') # Dummy file
    
    response = client.post('/object-count', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['error'] == "Threshold must be a number"

def test_object_prediction_missing_file(client):
    response = client.post('/object-prediction', data={})
    assert response.status_code == 400
    assert response.json['error'] == "No file part in the request"
