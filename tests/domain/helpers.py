from counter.domain.models import Prediction, Box

"""
Helper functions for creating domain objects in tests.
Makes test setup more concise and readable.
"""

def generate_prediction(class_name, score=1.0):
    """Creates a Prediction instance with a default empty bounding box."""
    return Prediction(class_name=class_name, score=score, box=Box(0, 0, 0, 0))