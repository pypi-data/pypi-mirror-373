# Tests for the decoder package.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_job_key():
    # Arrange
    j_collection: str = "c-1"
    j_job: str = "j-1"

    # Act
    key = decoder.get_job_key(collection=j_collection, job=j_job)

    # Assert
    assert key == "c-1|j-1"


def test_get_job_from_key():
    # Arrange
    j_key: str = "c-1|j-1"

    # Act
    j_collection, j_job = decoder.get_job_from_key(key=j_key)

    # Assert
    assert j_collection == "c-1"
    assert j_job == "j-1"


def test_jinja2_3_0_decode():
    # Arrange
    text: str = "foo={{ foo }}, bar={{ bar }}, baz={{ baz }}"
    field_map: Dict = {"foo": 1, "bar": 2, "baz": 3}
    expected_text: str = "foo=1, bar=2, baz=3"

    # Act
    rendered, success = decoder.decode(
        text, field_map, "text", decoder.TextEncoding.JINJA2_3_0
    )

    # Assert
    assert success
    assert rendered == expected_text


def test_jinja2_3_0_decode_with_missing_variables():
    # Arrange
    text: str = "foo={{ foo }}, bar={{ bar }}, baz={{ baz }}"
    field_map: Dict = {"foo": 1, "bar": 2}

    # Act
    rendered, success = decoder.decode(
        text, field_map, "text", decoder.TextEncoding.JINJA2_3_0
    )

    # Assert
    assert not success
    assert rendered == "Undefined template variables for text: baz"


def test_jinja2_3_0_decode_without_variables():
    # Arrange
    text: str = "foo=1, bar=2, baz=3"
    expected_text: str = "foo=1, bar=2, baz=3"

    # Act
    rendered, success = decoder.decode(
        text, None, "text", decoder.TextEncoding.JINJA2_3_0
    )

    # Assert
    assert success
    assert rendered == expected_text


def test_is_valid_collection_name_when_not_valid():
    # Arrange

    # Act
    success = decoder.is_valid_collection_name("blob.yaml")

    # Assert
    assert not success


def test_is_valid_collection_name_when_valid():
    # Arrange

    # Act
    success = decoder.is_valid_collection_name("collection-1")

    # Assert
    assert success


def test_is_valid_job_name_when_not_valid():
    # Arrange

    # Act
    success = decoder.is_valid_job_name("blob.yaml")

    # Assert
    assert not success


def test_is_valid_job_name_when_valid():
    # Arrange

    # Act
    success = decoder.is_valid_job_name("job-1")

    # Assert
    assert success
