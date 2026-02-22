from typing import List

from PIL import Image

from counter.debug import draw
from counter.domain.models import CountResponse, Prediction
from counter.domain.ports import ObjectDetector, ObjectCountRepo
from counter.domain.predictions import over_threshold, count

"""
Business logic (Use Cases) for the application.
According to Hexagonal Architecture, these are the Application Services that orchestrate the use of domain logic.
"""

class FindDetectedObjects:
    """Use case to detect objects in an image and filter them by a threshold."""
    def __init__(self, object_detector: ObjectDetector):
        self.__object_detector = object_detector

    def execute(self, image, threshold) -> List[Prediction]:
        """Orchestrates prediction, filtering, and optional debug visualization."""
        predictions = self.__object_detector.predict(image)
        self.__debug_image(image, predictions, "all_predictions.jpg")
        valid_predictions = list(over_threshold(predictions, threshold=threshold))
        self.__debug_image(image, valid_predictions, f"valid_predictions_with_threshold_{threshold}.jpg")
        return valid_predictions

    @staticmethod
    def __debug_image(image, predictions, image_name):
        """Internal helper to draw bounding boxes on an image for debugging purposes."""
        if __debug__ and image is not None:
            image = Image.open(image)
            draw(predictions, image, image_name)


class CountDetectedObjects:
    """Use case to count detected objects and update the persistent repository."""
    def __init__(self, find_action: FindDetectedObjects, object_count_repo: ObjectCountRepo):
        self.__find_action = find_action
        self.__object_count_repo = object_count_repo

    def execute(self, image, threshold) -> CountResponse:
        """Finds objects, updates their global counts, and returns a summary response."""
        predictions = self.__find_action.execute(image, threshold)
        object_counts = count(predictions)
        self.__object_count_repo.update_values(object_counts)
        total_objects = self.__object_count_repo.read_values()
        return CountResponse(current_objects=object_counts, total_objects=total_objects)
