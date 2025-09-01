# -----------------------------------------------------------------------------

from unittest.mock import MagicMock, Mock, patch

import pytest  # noqa: F401
from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError
from gitlab.v4.objects.files import ProjectFile

from gitlabcis.utils.ci import getConfig, searchConfig

# -----------------------------------------------------------------------------

mock_project_file = Mock(spec=ProjectFile)

# -----------------------------------------------------------------------------


def test_getConfig_remote_ci_file(glEntity, glObject):
    glEntity.ci_config_path = 'https://example.com/.gitlab-ci.yml'
    result = getConfig(glEntity, glObject)
    assert result == {
        None: 'Remote CI file: '
        'https://example.com/.gitlab-ci.yml not supported'}


def test_getConfig_default_path(glEntity, glObject):
    glEntity.ci_config_path = ''
    glEntity.default_branch = 'main'
    glEntity.files.get.return_value = mock_project_file
    result = getConfig(glEntity, glObject)
    assert isinstance(next(iter(result)), ProjectFile)


def test_getConfig_file_not_found(glEntity, glObject):
    glEntity.ci_config_path = '.gitlab-ci.yml'
    glEntity.default_branch = 'main'
    glEntity.files.get.side_effect = GitlabGetError(response_code=404)
    result = getConfig(glEntity, glObject)
    assert result == {
        False: f'Pipeline config file not found: {glEntity.ci_config_path}'}


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_string_found(mock_get_config, glEntity, glObject):
    mock_get_config.return_value = {mock_project_file: None}
    mock_project_file.content = 'SGVsbG8gV29ybGQ='
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result == {True: 'Hello was found in CI config file'}


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_string_not_found(mock_get_config, glEntity, glObject):
    mock_get_config.return_value = {mock_project_file: None}
    mock_project_file.content = 'SGVsbG8gV29ybGQ='
    result = searchConfig(glEntity, glObject, 'Python')
    assert result == {False: 'Python was not found in CI config file'}


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_skip_condition(mock_get_config, glEntity, glObject):
    mock_get_config.return_value = {None: 'Some skip reason'}
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result == {None: 'Some skip reason'}


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_file_not_found(mock_get_config, glEntity, glObject):
    mock_get_config.return_value = {
        False: 'Pipeline config file not found: .gitlab-ci.yml'}
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result == {False: 'Pipeline config file not found: .gitlab-ci.yml'}


def test_searchConfig_insufficient_permissions(glEntity, glObject):
    glEntity.ci_config_path = '.gitlab-ci.yml'
    glEntity.default_branch = 'main'
    glEntity.files.get.side_effect = GitlabAuthenticationError(
        response_code=401)
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result == {None: 'Insufficient permissions'}


def test_getConfig_insufficient_permissions(glEntity, glObject):
    glEntity.ci_config_path = '.gitlab-ci.yml'
    glEntity.default_branch = 'main'
    glEntity.files.get.side_effect = GitlabGetError(response_code=418)
    result = getConfig(glEntity, glObject)
    assert result == {
        False: f'Pipeline config file not found: {glEntity.ci_config_path}'}


@patch('re.match')
def test_nonetype_getConfig(reMatch, glEntity, glObject):
    mockRemote = MagicMock()
    mockRemote.group.side_effect = lambda name: {
        'refName': 'main',
        'namespace': 'stuff/things',
        'filePath': 'some/path'
    }[name]

    reMatch.return_value = mockRemote
    glEntity.ci_config_path = b'12345'
    glObject.projects.get.return_value = 'meh'
    glEntity.files.get.side_effect = GitlabGetError(response_code=404)
    result = getConfig(glEntity, glObject)
    assert result == {None: 'Insufficient permissions'}


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_handles_type_error(getConfig, glEntity, glObject):
    typeErrorMock = MagicMock()
    typeErrorMock.return_value = {None: 'lel'}
    getConfig.return_value = typeErrorMock
    getConfig.return_value.__iter__.side_effect = TypeError
    result = searchConfig(glEntity, glObject, 'search_string')
    assert next(iter(result)) is None


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_teapot(getConfig, glEntity, glObject):
    glEntity.ci_config_path = '.gitlab-ci.yml'
    glEntity.default_branch = 'main'
    getConfig.side_effect = GitlabAuthenticationError(response_code=418)
    glEntity.files.get.side_effect = GitlabAuthenticationError(
        response_code=418)
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result is None


@patch('gitlabcis.utils.ci.getConfig')
def test_searchConfig_unauth(getConfig, glEntity, glObject):
    glEntity.ci_config_path = '.gitlab-ci.yml'
    glEntity.default_branch = 'main'
    getConfig.side_effect = GitlabAuthenticationError(response_code=401)
    glEntity.files.get.side_effect = GitlabAuthenticationError(
        response_code=401)
    result = searchConfig(glEntity, glObject, 'Hello')
    assert result == {None: 'Insufficient permissions'}


@patch('re.match')
def test_nonetype_getConfig_teapot(reMatch, glEntity, glObject):
    mockRemote = MagicMock()
    mockRemote.group.side_effect = lambda name: {
        'refName': 'main',
        'namespace': 'stuff/things',
        'filePath': 'some/path'
    }[name]

    reMatch.return_value = mockRemote
    glEntity.ci_config_path = b'12345'
    glObject.projects.get.return_value = 'meh'
    glEntity.files.get.side_effect = GitlabAuthenticationError(
        response_code=418)
    result = getConfig(glEntity, glObject)
    assert result == {None: 'Insufficient permissions'}
