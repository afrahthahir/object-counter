# Integration test for the new prediction endpoint.
# Simulates a full HTTP request/response cycle using the Flask test client.
import io
import json
import pytest
from pathlib import Path

from counter.entrypoints.webapp import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def image_path():
    ref_dir = Path(__file__).parent
    return ref_dir.parent.parent / "resources" / "images" / "boy.jpg"

def test_object_prediction(client, image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = io.BytesIO(image_data)

    data = {
        'threshold': '0.1',
    }
    data['file'] = (image, 'test.jpg')

    response = client.post('/object-prediction', data=data,
                           content_type='multipart/form-data', buffered=True)

    assert response.status_code == 200
    predictions = json.loads(response.data)
    assert isinstance(predictions, list)
    if len(predictions) > 0:
        prediction = predictions[0]
        assert 'class_name' in prediction
        assert 'score' in prediction
        assert 'box' in prediction
        assert 'xmin' in prediction['box']
