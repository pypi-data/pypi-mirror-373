# Tests for the schema validator.
from typing import Any, Dict
from copy import deepcopy

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder

# A minimal Job Definition.
# Tests can use this and adjust accordingly.
_MINIMAL: Dict[str, Any] = {
    "kind": "DataManagerJobDefinition",
    "kind-version": "2021.1",
    "collection": "test",
    "jobs": {
        "demo": {
            "version": "1.0.0",
            "name": "test",
            "image": {
                "name": "blob",
                "tag": "1.0.0",
                "project-directory": "/data",
                "working-directory": "/data",
                "fix-permissions": True,
            },
            "command": "sys.exit(1)",
        }
    },
}


def test_validate_minimal():
    # Arrange

    # Act
    error = decoder.validate_job_schema(_MINIMAL)

    # Assert
    assert error is None


def test_validate_image_env_from_api_token():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["environment"] = [
        {"name": "ENV_VAR", "value-from": {"api-token": {"roles": ["abc"]}}}
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_env_from_constant():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["environment"] = [
        {"name": "ENV_VAR", "value-from": {"constant": {"value": "123"}}}
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_env_from_secret():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["environment"] = [
        {
            "name": "ENV_VAR",
            "value-from": {"secret": {"name": "secret-a", "key": "secret"}},
        }
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_env_from_account_server_asset():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["environment"] = [
        {
            "name": "ENV_VAR",
            "value-from": {"account-server-asset": {"name": "asset-a"}},
        }
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_file_from_account_server_asset():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["file"] = [
        {
            "name": "/usr/local/licence.txt",
            "content-from": {"account-server-asset": {"name": "asset-a"}},
        }
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_memory_32gi():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["memory"] = "32Gi"

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_memory_100mi():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["memory"] = "100Mi"

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_cores_1():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["cores"] = 1

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_cores_99():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["cores"] = 99

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_cores_10m():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["cores"] = "10m"

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_image_cores_1500m():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["image"]["cores"] = "1500m"

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_two_basic_tests():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["tests"] = {
        "basic-1": {"run-level": 1, "ignore": None},
        "basic-2": {
            "run-level": 100,
            "timeout-minutes": 30,
            "inputs": {"files": ["blob-1.txt", "blob-2.txt"]},
            "options": {"param-1": 32, "param-2": "a"},
            "environment": ["ENV_1", "ENV_2"],
            "checks": {
                "exitCode": 0,
                "outputs": [
                    {
                        "name": "blob.txt",
                        "checks": [{"exists": True}, {"lineCount": 100}],
                    }
                ],
            },
        },
    }

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_option_array():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["tests"] = {
        "option-array": {
            "options": {"param-array": ["a", "b"]},
        },
    }

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_groups():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    text["test-groups"] = [{"name": "demo-1"}, {"name": "demo-2"}]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_groups_with_environment():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    text["test-groups"] = [
        {
            "name": "demo-1",
            "environment": [{"ENV_A": "1"}, {"ENV_B": 2}, {"ENV_C": True}],
        }
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_groups_with_compose():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    text["test-groups"] = [
        {"name": "demo-1", "compose": {"file": "docker-compose-abc.yaml"}}
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_groups_with_compose_delay():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    text["test-groups"] = [
        {
            "name": "demo-1",
            "compose": {"file": "docker-compose-abc.yaml", "delay-seconds": 10},
        }
    ]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_run_groups():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["tests"] = {
        "basic-1": {
            "run-groups": [
                {"name": "demo-1", "ordinal": 1},
                {"name": "demo-2", "ordinal": 1},
            ],
        },
    }

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None


def test_validate_test_run_groups_without_ordinal():
    # Arrange
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["tests"] = {
        "basic-1": {
            "run-groups": [{"name": "demo-1"}, {"name": "demo-2"}],
        },
    }

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error == "'ordinal' is a required property"


def test_validate_replaces():
    text: Dict[str, Any] = deepcopy(_MINIMAL)
    demo_job: Dict[str, Any] = text["jobs"]["demo"]
    demo_job["replaces"] = [{"collection": "test-collection", "job": "test-job"}]

    # Act
    error = decoder.validate_job_schema(text)

    # Assert
    assert error is None
