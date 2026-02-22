from dataclasses import dataclass
from typing import List

"""
Domain models for the object counter application.
These are pure data structures representing the core concepts of the system.
"""

@dataclass
class Box:
    """Represents a bounding box in normalized coordinates (0.0 to 1.1)."""
    xmin: float
    ymin: float
    xmax: float
    ymax: float


@dataclass
class Prediction:
    """Represents a single object detection including its category, confidence score, and location."""
    class_name: str
    score: float
    box: Box


@dataclass
class ObjectCount:
    """Represents the count of detected objects for a specific category."""
    object_class: str
    count: int


@dataclass
class CountResponse:
    """The final response object combining the count from the current image and the historical totals."""
    current_objects: List[ObjectCount]
    total_objects: List[ObjectCount]
