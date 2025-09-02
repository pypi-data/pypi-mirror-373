# -----------------------------------------------------------------------------

import base64
from unittest.mock import Mock, patch

import pytest  # noqa: F401
import yaml
from conftest import run
from gitlab.exceptions import GitlabHttpError

from gitlabcis.benchmarks.build_pipelines_2 import pipeline_integrity_2_4

# -----------------------------------------------------------------------------


def test_sign_artifacts(glEntity, glObject):

    test = pipeline_integrity_2_4.sign_artifacts

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_lock_dependencies(glEntity, glObject):

    test = pipeline_integrity_2_4.lock_dependencies

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.searchConfig')
def test_validate_dependencies(mockSearchConfig, glEntity, glObject):

    test = pipeline_integrity_2_4.validate_dependencies

    kwargs = {'isProject': True}
    mockSearchConfig.return_value = {True: 'Dependency Scanning found'}
    run(glEntity, glObject, test, True, **kwargs)

    mockSearchConfig.return_value = {False: 'Dependency Scanning not found'}
    run(glEntity, glObject, test, False, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.getConfig')
def test_create_reproducible_artifacts(mockGetConfig, glEntity, glObject):

    test = pipeline_integrity_2_4.create_reproducible_artifacts

    kwargs = {'isProject': True}

    def setup_ci_yaml(yaml_content):
        mock_file = Mock()
        mock_file.content = base64.b64encode(
            yaml.dump(
                yaml_content
            ).encode()).decode('utf-8')
        return {mock_file: 'reason'}

    mockGetConfig.return_value = {None: 'File not found'}
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.return_value = setup_ci_yaml({})
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.return_value = setup_ci_yaml({'stages': ['test']})
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.return_value = setup_ci_yaml({
        'stages': ['build', 'test'],
        'build_job': {'stage': 'build', 'artifacts': {'paths': ['**/*']}}
    })
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.searchConfig')
def test_pipeline_produces_sbom(mockSearchConfig, glEntity, glObject):

    test = pipeline_integrity_2_4.pipeline_produces_sbom

    kwargs = {'isProject': True}
    mockSearchConfig.return_value = {True: 'Dependency Scanning found'}
    run(glEntity, glObject, test, True, **kwargs)

    mockSearchConfig.return_value = {False: 'Dependency Scanning not found'}
    run(glEntity, glObject, test, False, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_pipeline_sign_sbom(glEntity, glObject):

    test = pipeline_integrity_2_4.pipeline_sign_sbom

    run(glEntity, glObject, test, None)
