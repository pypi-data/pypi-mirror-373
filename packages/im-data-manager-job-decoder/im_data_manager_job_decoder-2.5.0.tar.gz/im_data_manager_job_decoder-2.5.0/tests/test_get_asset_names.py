# Tests for the decoder's get_asset_names() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_asset_names():
    # Arrange
    job_definition: Dict = {
        "image": {
            "environment": [
                {
                    "name": "BLOB",
                    "value-from": {"account-server-asset": {"name": "asset-a"}},
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
    asset_names = decoder.get_asset_names(job_definition)

    # Assert
    assert len(asset_names) == 2
    assert "asset-a" in asset_names
    assert "asset-b" in asset_names
