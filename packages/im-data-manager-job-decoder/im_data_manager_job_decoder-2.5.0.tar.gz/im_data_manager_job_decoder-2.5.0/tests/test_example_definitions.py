import yaml
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_good_example_definitions():
    for example_definition in Path("example-definitions/good").glob("*.yaml"):
        with open(example_definition, "r", encoding="utf-8") as example_file:
            error = decoder.validate_job_schema(yaml.safe_load(example_file))
            assert error is None, example_definition


def test_bad_example_definitions():
    for example_definition in Path("example-definitions/bad").glob("*.yaml"):
        with open(example_definition, "r", encoding="utf-8") as example_file:
            error = decoder.validate_job_schema(yaml.safe_load(example_file))
            assert error is not None, example_definition
