# Tests for the decoder's get_inputs() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_inputs_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    inputs = decoder.get_inputs(job_definition)

    # Assert
    assert inputs == {}


def test_get_inputs():
    # Arrange
    job_definition: Dict = {
        "variables": {
            "inputs": {
                "properties": {
                    "inputFile": {
                        "title": "PDB File",
                        "mime-types": ["chemical/x-pdb"],
                        "type": "file",
                    }
                }
            }
        }
    }

    # Act
    inputs = decoder.get_inputs(job_definition)

    # Assert
    assert inputs
    assert "inputFile" in inputs
    assert inputs["inputFile"]["title"] == "PDB File"
    assert inputs["inputFile"]["mime-types"] == ["chemical/x-pdb"]
    assert inputs["inputFile"]["type"] == "file"
