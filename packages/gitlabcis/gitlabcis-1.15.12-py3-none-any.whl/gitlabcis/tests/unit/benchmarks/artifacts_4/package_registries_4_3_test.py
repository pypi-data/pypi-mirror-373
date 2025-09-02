# -----------------------------------------------------------------------------

from unittest.mock import Mock

import pytest  # noqa: F401
from conftest import run
from gitlab.exceptions import GitlabHttpError

from gitlabcis.benchmarks.artifacts_4 import package_registries_4_3

# -----------------------------------------------------------------------------


def test_validate_signed_artifacts_on_upload(glEntity, glObject):

    test = package_registries_4_3.validate_signed_artifacts_on_upload

    kwargs = {'isProject': True}
    glEntity.commits.list.return_value = [Mock(id='1'), Mock(id='2')]

    glEntity.commits.get.return_value = Mock(status='verified')
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.commits.get.return_value = Mock(status=None)
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.commits.get.side_effect = [
        Mock(status='verified'), Mock(status='unverified')]
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.commits.list.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.commits.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_all_artifact_versions_signed(glEntity, glObject):

    test = package_registries_4_3.all_artifact_versions_signed

    kwargs = {'isProject': True}
    glEntity.commits.list.return_value = [Mock(id='1'), Mock(id='2')]

    glEntity.commits.get.return_value = Mock(status=None)
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.commits.get.return_value = Mock(status='verified')
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.commits.get.return_value = Mock(status='unverified')
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.commits.list.side_effect = GitlabHttpError(response_code=403)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.commits.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_audit_package_registry_config(glEntity, glObject):

    test = package_registries_4_3.audit_package_registry_config

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_secure_repo_webhooks(glEntity, glObject):

    test = package_registries_4_3.secure_repo_webhooks

    kwarg = [{'isProject': True}, {'isInstance': True}]

    for kwargs in kwarg:

        secHookSSLVerify = Mock(
            url='https://example.com', enable_ssl_verification=True)

        secHookNoSSLVerify = Mock(
            url='https://example.com', enable_ssl_verification=False)

        unsecureHook = Mock(
            url='http://example.com', enable_ssl_verification=False)

        print(kwargs)
        glEntity.hooks.list.return_value = []
        glObject.hooks.list.return_value = []
        run(glEntity, glObject, test, True, **kwargs)

        glEntity.hooks.list.return_value = [
            secHookSSLVerify]
        glObject.hooks.list.return_value = [
                secHookSSLVerify]
        run(glEntity, glObject, test, True, **kwargs)

        glEntity.hooks.list.return_value = [
            secHookNoSSLVerify]
        glObject.hooks.list.return_value = [
            secHookNoSSLVerify]
        run(glEntity, glObject, test, False, **kwargs)

        glEntity.hooks.list.return_value = [
            unsecureHook]
        glObject.hooks.list.return_value = [
            unsecureHook]
        run(glEntity, glObject, test, False, **kwargs)

    kwarg = [{'isProject': True}, {'isInstance': True}]

    for kwargs in kwarg:
        glEntity.hooks.list.side_effect = GitlabHttpError(response_code=403)
        glObject.hooks.list.side_effect = GitlabHttpError(response_code=403)
        run(glEntity, glObject, test, None, **kwargs)

        glEntity.hooks.list.side_effect = GitlabHttpError(response_code=418)
        glObject.hooks.list.side_effect = GitlabHttpError(response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isGroup': True})
