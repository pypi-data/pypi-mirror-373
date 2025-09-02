# Tests for the decoder package.
import pytest

pytestmark = pytest.mark.unit

from typing import Dict

from decoder import decode_jinja2_3_0


def test_basic_decode():
    # Arrange
    text: str = "foo={{ foo }}, bar={{ bar }}, baz={{ baz }}"
    field_map: Dict = {"foo": 1, "bar": 2, "baz": 3}
    expected_text: str = "foo=1, bar=2, baz=3"

    # Act
    rendered, success = decode_jinja2_3_0.decode(text, field_map, "text")

    # Assert
    assert success
    assert rendered == expected_text


def test_decode_with_missing_variables():
    # Arrange
    text: str = "foo={{ foo }}, bar={{ bar }}, baz={{ baz }}"
    field_map: Dict = {"foo": 1}
    expected_text_prefix: str = "Undefined template variables for text:"

    # Act
    rendered, success = decode_jinja2_3_0.decode(text, field_map, "text")

    # Assert
    assert not success
    # The order of missing variables is not deterministic.
    # They change - so we just need to make suer they're there.
    assert rendered.startswith(expected_text_prefix)
    assert "bar" in rendered
    assert "baz" in rendered


def test_decode_with_template_error():
    # Arrange
    text: str = "foo={{ foo doo }}, bar={{ bar }}, baz={{ baz }}"
    field_map: Dict = {"foo": 1}
    expected_text: str = (
        "TemplateSyntaxError with text:"
        " expected token 'end of print statement', got 'doo'"
    )

    # Act
    rendered, success = decode_jinja2_3_0.decode(text, field_map, "text")

    # Assert
    assert not success
    assert rendered == expected_text
