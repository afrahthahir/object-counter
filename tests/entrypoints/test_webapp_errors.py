import pytest
from counter.entrypoints.webapp import create_app

"""
Integration tests for verifying API error handling and input validation.
Ensures the server returns meaningful 400 errors for bad requests.
"""

@pytest.fixture
def client():
    """Sets up a Flask test client."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_object_count_missing_file(client):
    """Verifies 400 error when the mandatory 'file' part is missing."""
    response = client.post('/object-count', data={})
    assert response.status_code == 400
    assert response.json['error'] == "No file part in the request"

def test_object_count_invalid_threshold(client):
    """Verifies 400 error when 'threshold' is not a valid floating point number."""
    data = {'threshold': 'invalid'}
    # Use any local file as a dummy upload
    data['file'] = (open('README.md', 'rb'), 'test.txt') 
    
    response = client.post('/object-count', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert response.json['error'] == "Threshold must be a number"

def test_object_prediction_missing_file(client):
    """Verifies 400 error for the prediction endpoint when 'file' is missing."""
    response = client.post('/object-prediction', data={})
    assert response.status_code == 400
    assert response.json['error'] == "No file part in the request"
