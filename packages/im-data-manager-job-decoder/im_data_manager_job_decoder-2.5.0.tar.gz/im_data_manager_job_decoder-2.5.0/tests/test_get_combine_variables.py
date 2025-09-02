# Tests for the decoder's get_outputs() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_combine_variables_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    combines = decoder.get_combine_variables(job_definition)

    # Assert
    assert combines == set()


def test_get_combine_variables():
    # Arrange
    job_definition: Dict = {
        "variables": {
            "inputs": {
                "properties": {
                    "pdbFile": {
                        "title": "PDB File",
                        "mime-types": ["chemical/x-pdb"],
                        "type": "files",
                    }
                }
            }
        }
    }

    # Act
    combines = decoder.get_combine_variables(job_definition)

    # Assert
    assert combines
    assert "pdbFile" in combines
