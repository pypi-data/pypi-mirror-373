# Tests for the decoder's get_outputs() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_split_variables_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    splits = decoder.get_split_variables(job_definition)

    # Assert
    assert splits == set()


def test_get_split_variables():
    # Arrange
    job_definition: Dict = {
        "variables": {
            "outputs": {
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
    splits = decoder.get_split_variables(job_definition)

    # Assert
    assert splits
    assert "pdbFile" in splits
