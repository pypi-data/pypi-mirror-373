# Tests for the decoder's get_environment_assets() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_environment_assets():
    # Arrange
    job_definition: Dict = {
        "image": {
            "environment": [
                {
                    "name": "BLOB",
                    "value-from": {"account-server-asset": {"name": "asset-c"}},
                }
            ],
            "file": [
                {
                    "name": "/tmp/blob-1.txt",
                    "content-from": {"account-server-asset": {"name": "asset-a"}},
                },
                {
                    "name": "/tmp/blob-2.txt",
                    "content-from": {"account-server-asset": {"name": "asset-b"}},
                },
            ],
        },
    }

    # Act
    env_assets = decoder.get_environment_assets(job_definition)

    # Assert
    assert len(env_assets) == 1
    assert env_assets[0]["asset-name"] == "asset-c"
    assert env_assets[0]["variable"] == "BLOB"
