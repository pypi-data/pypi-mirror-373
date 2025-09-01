# -----------------------------------------------------------------------------

import builtins
from unittest.mock import Mock, patch

import gitlab
import pytest

from gitlabcis.cli.auth import GitlabCIS

# -----------------------------------------------------------------------------


# skip admin warning
@pytest.fixture(autouse=True)
def mock_input(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda _: 'y')


# mock auth
@pytest.fixture
def mock_gitlab():
    with patch('gitlabcis.cli.auth.gitlab') as mock:
        yield mock

# -----------------------------------------------------------------------------


def test_authenticate(mock_gitlab):
    gitlab_cis = GitlabCIS('https://gitlab.com', 'fake-token')
    assert gitlab_cis.glObject is not None

# -----------------------------------------------------------------------------


def test_determine_entity_project(mock_gitlab):
    mock_project = Mock()
    mock_project.namespace = {'full_path': 'user/project'}
    mock_gitlab.Gitlab.return_value.projects.get.return_value = mock_project

    gitlab_cis = GitlabCIS('https://gitlab.com/user/project', 'fake-token')

    assert gitlab_cis.isProject
    assert not gitlab_cis.isGroup
    assert not gitlab_cis.isInstance

# -----------------------------------------------------------------------------


def test_determine_entity_group(mock_gitlab):
    # Mock project.get to raise GitlabGetError with 404 response code
    mock_projects_get = Mock(
        side_effect=gitlab.exceptions.GitlabGetError('', response_code=404))
    mock_gitlab.Gitlab.return_value.projects.get = mock_projects_get

    # Set up the group mock correctly
    mock_group = Mock()
    mock_group.full_path = 'group'
    mock_groups_get = Mock(return_value=mock_group)
    mock_gitlab.Gitlab.return_value.groups.get = mock_groups_get

    # Ensure GitlabGetError and GitlabHttpError are available
    mock_gitlab.exceptions.GitlabGetError = gitlab.exceptions.GitlabGetError
    mock_gitlab.exceptions.GitlabHttpError = gitlab.exceptions.GitlabHttpError

    gitlab_cis = GitlabCIS('https://gitlab.com/group', 'fake-token')

    assert mock_projects_get.called, "projects.get was not called"
    assert mock_groups_get.called, "groups.get was not called"
    assert not gitlab_cis.isProject, "isProject should be False for a group"
    assert gitlab_cis.isGroup, "isGroup should be True"
    assert not gitlab_cis.isInstance, "isInstance should be False"
    assert gitlab_cis.paths == ['group'], "paths should be ['group']"

# -----------------------------------------------------------------------------


def test_determine_entity_instance(mock_gitlab):
    mock_gitlab.Gitlab.return_value.projects.get.side_effect = \
        mock_gitlab.exceptions.GitlabGetError()
    mock_gitlab.Gitlab.return_value.groups.get.side_effect = \
        mock_gitlab.exceptions.GitlabGetError()
    gitlab_cis = GitlabCIS('https://gitlab.com', 'fake-token')
    assert not gitlab_cis.isProject
    assert not gitlab_cis.isGroup
    assert gitlab_cis.isInstance

# -----------------------------------------------------------------------------


def test_cascade(mock_gitlab):
    mock_group = Mock()
    mock_group.full_path = 'group/subgroup'
    mock_gitlab.Gitlab.return_value.groups.get.return_value = mock_group
    gitlab_cis = GitlabCIS('https://gitlab.com/group/subgroup', 'fake-token')
    gitlab_cis.cascade()
    assert gitlab_cis.paths is not None

# -----------------------------------------------------------------------------


def test_kwargs(mock_gitlab):
    gitlab_cis = GitlabCIS('https://gitlab.com', 'fake-token')
    kwargs = gitlab_cis.kwargs
    assert 'isGroup' in kwargs
    assert 'isInstance' in kwargs
    assert 'isProject' in kwargs
    assert 'isAdmin' in kwargs
    assert 'isDotCom' in kwargs
    assert 'graphQLEndpoint' in kwargs
    assert 'graphQLHeaders' in kwargs
    assert 'pathStrs' in kwargs
    assert 'pathObjs' in kwargs
