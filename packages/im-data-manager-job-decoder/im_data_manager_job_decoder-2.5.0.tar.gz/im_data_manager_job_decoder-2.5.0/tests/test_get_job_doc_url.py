# Tests for the decoder's get_job_doc_url() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_get_github_job_doc_url_with_fq_doc_url():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {
        "doc-url": "https://example.com/docs/doc.md",
    }
    manifest_url: str = (
        "https://raw.githubusercontent.com/"
        "InformaticsMatters/virtual-screening/main/data-manager/"
        "manifest-virtual-screening.yaml"
    )
    expected_doc_url: str = "https://example.com/docs/doc.md"

    # Act
    doc_url = decoder.get_job_doc_url(
        decoder.REPO_TYPE_GITHUB, collection, job, job_definition, manifest_url
    )

    # Assert
    assert doc_url
    assert doc_url == expected_doc_url


def test_get_github_job_doc_url_with_partial_doc_url():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {"doc-url": "special/doc.md"}
    manifest_url: str = (
        "https://raw.githubusercontent.com/"
        "InformaticsMatters/virtual-screening/main/data-manager/"
        "manifest-virtual-screening.yaml"
    )
    expected_doc_url: str = (
        "https://github.com/"
        "InformaticsMatters/virtual-screening/blob/main/data-manager/docs/"
        "special/doc.md"
    )

    # Act
    doc_url = decoder.get_job_doc_url(
        decoder.REPO_TYPE_GITHUB, collection, job, job_definition, manifest_url
    )

    # Assert
    assert doc_url
    assert doc_url == expected_doc_url


def test_get_github_job_doc_url_with_no_doc_url():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {}
    manifest_url: str = (
        "https://raw.githubusercontent.com/"
        "InformaticsMatters/virtual-screening/1.0.1/data-manager/"
        "manifest-virtual-screening.yaml"
    )
    expected_doc_url: str = (
        "https://github.com/"
        "InformaticsMatters/virtual-screening/blob/1.0.1/data-manager/docs/"
        "collection-x/job-x.md"
    )

    # Act
    doc_url = decoder.get_job_doc_url(
        decoder.REPO_TYPE_GITHUB, collection, job, job_definition, manifest_url
    )

    # Assert
    assert doc_url
    assert doc_url == expected_doc_url


def test_get_gitlab_job_doc_url_with_partial_doc_url():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {"doc-url": "special/doc.md"}
    manifest_url: str = (
        "https://gitlab.com/api/v4/projects/00000000/repository/files/"
        "data-manager%2fmanifest.yaml/raw"
    )
    expected_doc_url: str = (
        "https://gitlab.com/api/v4/projects/00000000/repository/files/"
        "data-manager%2fdocs%2fspecial%2fdoc.md/raw"
    )

    # Act
    doc_url = decoder.get_job_doc_url(
        decoder.REPO_TYPE_GITLAB, collection, job, job_definition, manifest_url
    )

    # Assert
    assert doc_url
    assert doc_url == expected_doc_url


def test_get_gitlab_job_doc_url_with_no_doc_url():
    # Arrange
    collection: str = "collection-x"
    job: str = "job-x"
    job_definition: Dict = {}
    manifest_url: str = (
        "https://gitlab.com/api/v4/projects/00000000/repository/files/"
        "data-manager%2fmanifest.yaml/raw"
    )
    expected_doc_url: str = (
        "https://gitlab.com/api/v4/projects/00000000/repository/files/"
        "data-manager%2fdocs%2fcollection-x%2fjob-x.md/raw"
    )

    # Act
    doc_url = decoder.get_job_doc_url(
        decoder.REPO_TYPE_GITLAB, collection, job, job_definition, manifest_url
    )

    # Assert
    assert doc_url
    assert doc_url == expected_doc_url
