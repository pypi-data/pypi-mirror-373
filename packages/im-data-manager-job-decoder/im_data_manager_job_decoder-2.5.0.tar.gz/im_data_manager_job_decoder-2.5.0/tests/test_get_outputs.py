# Tests for the decoder's get_outputs() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_outputs_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    outputs = decoder.get_outputs(job_definition)

    # Assert
    assert outputs == {}


def test_get_outputs():
    # Arrange
    job_definition: Dict = {
        "variables": {
            "outputs": {
                "properties": {
                    "pdbFile": {
                        "title": "PDB File",
                        "mime-types": ["chemical/x-pdb"],
                        "type": "file",
                    }
                }
            }
        }
    }

    # Act
    outputs = decoder.get_outputs(job_definition)

    # Assert
    assert outputs
    assert "pdbFile" in outputs
    assert outputs["pdbFile"]["title"] == "PDB File"
    assert outputs["pdbFile"]["mime-types"] == ["chemical/x-pdb"]
    assert outputs["pdbFile"]["type"] == "file"
