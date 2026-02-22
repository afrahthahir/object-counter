from abc import ABC, abstractmethod
from typing import BinaryIO, List

from counter.domain.models import Prediction, ObjectCount

"""
Ports (Interfaces) for the application.
According to Hexagonal Architecture, these define the contracts that adapters must implement.
"""

class ObjectDetector(ABC):
    """Port for object detection services. Adapters can be TensorFlow Serving, PyTorch, or Fakes."""
    @abstractmethod
    def predict(self, image: BinaryIO) -> List[Prediction]:
        """Runs the detection model on an image and returns a list of domain Predictions."""
        raise NotImplementedError


class ObjectCountRepo(ABC):
    """Port for persistent storage of object counts. Adapters can be MongoDB, Postgres, or In-Memory."""
    @abstractmethod
    def read_values(self, object_classes: List[str] = None) -> List[ObjectCount]:
        """Retrieves accumulated counts, optionally filtered by class names."""
        raise NotImplementedError

    @abstractmethod
    def update_values(self, new_values: List[ObjectCount]):
        """Increments or sets the persistent counts with new detection data."""
        raise NotImplementedError

