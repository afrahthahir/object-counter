# Unit tests for domain actions, ensuring logic is correct in isolation.
from unittest.mock import Mock

import pytest

from counter.domain.actions import CountDetectedObjects
from counter.domain.models import ObjectCount
from tests.domain.helpers import generate_prediction


class TestCountDetectedObjects:
    @pytest.fixture
    def find_action(self) -> Mock:
        find_action = Mock()
        find_action.execute.return_value = [generate_prediction('cat', 0.9),
                                            generate_prediction('cat', 0.8),
                                            generate_prediction('dog', 0.8),
                                            generate_prediction('rabbit', 0.9)]
        return find_action

    @pytest.fixture
    def count_object_repo(self) -> Mock:
        return Mock()

    def test_count_valid_predictions(self, find_action, count_object_repo) -> None:
        response = CountDetectedObjects(find_action, count_object_repo).execute(None, 0.5)
        assert sorted(response.current_objects, key=lambda x: x.object_class) == \
            [ObjectCount('cat', 2), ObjectCount('dog', 1), ObjectCount('rabbit', 1)]

    def test_update_count_object_repo(self, find_action, count_object_repo):
        find_action.execute.return_value = [generate_prediction('cat', 0.9),
                                            generate_prediction('cat', 0.8),
                                            generate_prediction('dog', 0.8),
                                            generate_prediction('dog', 0.1),
                                            generate_prediction('rabbit', 0.9)]
        CountDetectedObjects(find_action, count_object_repo).execute(None, 0)
        count_object_repo.update_values.assert_called_with(
            [ObjectCount('cat', 2), ObjectCount('dog', 2), ObjectCount('rabbit', 1)])
