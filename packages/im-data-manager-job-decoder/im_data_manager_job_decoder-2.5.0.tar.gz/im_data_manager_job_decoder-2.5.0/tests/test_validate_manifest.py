# Tests for the schema validator.
from typing import Any, Dict
from copy import deepcopy

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder

# A minimal Job Definition.
# Tests can use this and adjust accordingly.
_MINIMAL: Dict[str, Any] = {
    "kind": "DataManagerManifest",
    "kind-version": "2021.1",
    "job-definition-files": ["blob.yaml", "blob.yml"],
}


def test_validate_minimal():
    # Arrange

    # Act
    error = decoder.validate_manifest_schema(_MINIMAL)

    # Assert
    assert error is None
