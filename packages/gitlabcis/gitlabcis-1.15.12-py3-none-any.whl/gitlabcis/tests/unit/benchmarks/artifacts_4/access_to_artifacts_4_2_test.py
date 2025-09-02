# -----------------------------------------------------------------------------

from unittest.mock import Mock

import pytest  # noqa: F401
from conftest import run
from gitlab.exceptions import GitlabHttpError

from gitlabcis.benchmarks.artifacts_4 import access_to_artifacts_4_2

# -----------------------------------------------------------------------------


def test_limit_certifying_artifacts(glEntity, glObject):

    test = access_to_artifacts_4_2.limit_certifying_artifacts

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_limit_artifact_uploaders(glEntity, glObject):

    test = access_to_artifacts_4_2.limit_artifact_uploaders

    kwargs = {'isProject': True}
    glEntity.members.list.return_value = [
        Mock(access_level=40),
        Mock(access_level=30),
        Mock(access_level=20),
        Mock(access_level=10),
        Mock(access_level=10)
    ]
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.members.list.return_value = [
        Mock(access_level=40),
        Mock(access_level=40),
        Mock(access_level=40),
        Mock(access_level=30),
        Mock(access_level=20)
    ]
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.members.list.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.members.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_require_mfa_to_package_registry(glEntity, glObject):

    test = access_to_artifacts_4_2.require_mfa_to_package_registry

    glObject.settings.get.return_value = Mock(
        require_two_factor_authentication=True)
    run(glEntity, glObject, test, True)

    glObject.settings.get.return_value = Mock(
        require_two_factor_authentication=False)
    run(glEntity, glObject, test, False)

    glObject.settings.get.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None)

    glObject.settings.get.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject) is None

# -----------------------------------------------------------------------------


def test_external_auth_server(glEntity, glObject):

    test = access_to_artifacts_4_2.external_auth_server

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_restrict_anonymous_access(glEntity, glObject):

    test = access_to_artifacts_4_2.restrict_anonymous_access

    glObject.settings.get.return_value = Mock(
        default_project_visibility='public')
    run(glEntity, glObject, test, False)

    glObject.settings.get.return_value = Mock(
        default_project_visibility='not-public')
    run(glEntity, glObject, test, True)

    glObject.settings.get.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None)

    glObject.settings.get.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject) is None

# -----------------------------------------------------------------------------


def test_minimum_package_registry_admins(glEntity, glObject):

    test = access_to_artifacts_4_2.minimum_package_registry_admins

    kwargs = {'isProject': True}
    glEntity.members.list.return_value = [
        Mock(access_level=40),
        Mock(access_level=10),
        Mock(access_level=10),
        Mock(access_level=10),
        Mock(access_level=10)
    ]
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.members.list.return_value = [
        Mock(access_level=40),
        Mock(access_level=40),
        Mock(access_level=40),
        Mock(access_level=40),
        Mock(access_level=20)
    ]
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.members.list.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.members.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)
