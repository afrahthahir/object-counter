# Entrypoint for the Flask web application.
# Includes both the legacy object-count and new object-prediction endpoints.
from dataclasses import asdict
from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

def create_app():
    
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    find_action = config.get_find_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        
        threshold = float(request.form.get('threshold', 0.5))
        uploaded_file = request.files['file']
        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(asdict(count_response))

    @app.route('/object-prediction', methods=['POST'])
    def object_prediction():
        threshold = float(request.form.get('threshold', 0.5))
        uploaded_file = request.files['file']
        image = BytesIO()
        uploaded_file.save(image)
        predictions = find_action.execute(image, threshold)
        return jsonify([asdict(p) for p in predictions])
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run('0.0.0.0', debug=True)
