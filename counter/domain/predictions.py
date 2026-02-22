from functools import reduce
from typing import List

from counter.domain.models import Prediction, ObjectCount

"""
Utility functions for processing raw prediction data within the domain layer.
"""

def over_threshold(predictions: List[Prediction], threshold: float):
    """Filters a list of predictions, keeping only those with a score >= threshold."""
    return filter(lambda prediction: prediction.score >= threshold, predictions)


def count(predictions: List[Prediction]) -> List[ObjectCount]:
    """Aggregates a list of predictions into a list of ObjectCount (counts per category)."""
    object_classes = map(lambda prediction: prediction.class_name, predictions)
    object_classes_counter = reduce(__count_object_classes, object_classes, {})
    return [ObjectCount(object_class, occurrences) for object_class, occurrences in object_classes_counter.items()]


def __count_object_classes(class_counter: dict, object_class: str):
    """Helper function for reduce() that increments the frequency for a particular class."""
    class_counter[object_class] = class_counter.get(object_class, 0) + 1
    return class_counter
