# Entrypoint for the Flask web application.
# Includes both the legacy object-count and new object-prediction endpoints.
from dataclasses import asdict
from io import BytesIO

from flask import Flask, request, jsonify

from counter import config

"""
Web Entrypoint Layer.
Exposes the application features via a REST API using Flask.
"""

def create_app():
    """Initializes the Flask application and seeds it with real or fake actions."""
    app = Flask(__name__)
    
    count_action = config.get_count_action()
    find_action = config.get_find_action()
    
    @app.route('/object-count', methods=['POST'])
    def object_detection():
        """
        Receives an image and threshold, returns summarized counts.
        Updates persistent storage with the new detection data.
        """
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
        
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        try:
            threshold = float(request.form.get('threshold', 0.5))
        except ValueError:
            return jsonify({"error": "Threshold must be a number"}), 400

        image = BytesIO()
        uploaded_file.save(image)
        count_response = count_action.execute(image, threshold)
        return jsonify(asdict(count_response))

    @app.route('/object-prediction', methods=['POST'])
    def object_prediction():
        """
        Receives an image and threshold, returns detailed predictions.
        Does NOT update persistent storage.
        """
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400
            
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        try:
            threshold = float(request.form.get('threshold', 0.5))
        except ValueError:
            return jsonify({"error": "Threshold must be a number"}), 400

        image = BytesIO()
        uploaded_file.save(image)
        predictions = find_action.execute(image, threshold)
        return jsonify([asdict(p) for p in predictions])
    
    return app

if __name__ == '__main__':
    # Start the Flask development server
    app = create_app()
    app.run('0.0.0.0', debug=True)
