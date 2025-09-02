# Tests for the decoder's get_jobs_replaced() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_jobs_replaced_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    replaced = decoder.get_jobs_replaced(job_definition)

    # Assert
    assert replaced is None


def test_get_jobs_replaced():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {
        "replaces": [
            {"collection": "c-1", "job": "j-1"},
            {"collection": "c-1", "job": "j-2"},
        ]
    }

    # Act
    replaced = decoder.get_jobs_replaced(job_definition)

    # Assert
    assert replaced
    assert len(replaced) == 2
    assert "c-1|j-1" in replaced
    assert "c-1|j-2" in replaced
