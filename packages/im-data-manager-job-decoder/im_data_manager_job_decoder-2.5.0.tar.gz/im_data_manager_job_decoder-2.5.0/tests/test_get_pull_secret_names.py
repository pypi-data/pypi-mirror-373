# Tests for the decoder's get_pull_secret_names() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_asset_names():
    # Arrange
    job_definition: Dict = {
        "image": {"pull-secret": "secret-a"},
    }

    # Act
    secret_names = decoder.get_pull_secret_names(job_definition)

    # Assert
    assert len(secret_names) == 1
    assert "secret-a" in secret_names
