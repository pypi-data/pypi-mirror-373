# -----------------------------------------------------------------------------

from unittest.mock import Mock, patch

import pytest  # noqa: F401
from conftest import run
from gitlab.exceptions import GitlabHttpError

from gitlabcis.benchmarks.build_pipelines_2 import build_environment_2_1

# -----------------------------------------------------------------------------


def test_single_responsibility_pipeline(glEntity, glObject):

    test = build_environment_2_1.single_responsibility_pipeline

    kwargs = {'isProject': True}

    def setup_pipeline_jobs(*job_stages):
        mock_pipeline = Mock()
        mock_pipeline.jobs.list.return_value = [
            Mock(stage=stage) for stage in job_stages]
        glEntity.pipelines.list.return_value = [mock_pipeline]

    glEntity.pipelines.list.return_value = []
    run(glEntity, glObject, test, True, **kwargs)

    setup_pipeline_jobs('test')
    run(glEntity, glObject, test, None, **kwargs)

    setup_pipeline_jobs('build')
    run(glEntity, glObject, test, True, **kwargs)

    setup_pipeline_jobs('build', 'build')
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.pipelines.list.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.pipelines.list.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_immutable_pipeline_infrastructure(glEntity, glObject):

    test = build_environment_2_1.immutable_pipeline_infrastructure

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_build_logging(glEntity, glObject):

    test = build_environment_2_1.build_logging

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.getConfig')
def test_build_automation(mockGetConfig, glEntity, glObject):

    test = build_environment_2_1.build_automation

    kwargs = {'isProject': True}
    mockGetConfig.return_value = {'gitlab-ci.yml': 'content'}
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.return_value = {None: 'No CI file found'}
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.return_value = {False: 'Invalid CI file'}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_limit_build_access(glEntity, glObject):

    test = build_environment_2_1.limit_build_access

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:

        glEntity.members.list.return_value = [
            Mock(access_level=40),
            Mock(access_level=20),
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
            Mock(access_level=30),
            Mock(access_level=20)
        ]
        run(glEntity, glObject, test, False, **kwargs)

    for kwargs in kwarg:
        glEntity.members.list.side_effect = GitlabHttpError(response_code=403)
        run(glEntity, glObject, test, None, **kwargs)

        glEntity.members.list.side_effect = GitlabHttpError(response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_authenticate_build_access(glEntity, glObject):

    test = build_environment_2_1.authenticate_build_access

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:

        glEntity.members.list.return_value = [
            Mock(access_level=40),
            Mock(access_level=20),
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
            Mock(access_level=30),
            Mock(access_level=20)
        ]
        run(glEntity, glObject, test, False, **kwargs)

    for kwargs in kwarg:
        glEntity.members.list.side_effect = GitlabHttpError(response_code=403)
        run(glEntity, glObject, test, None, **kwargs)

        glEntity.members.list.side_effect = GitlabHttpError(response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_limit_build_secrets_scope(glEntity, glObject):

    test = build_environment_2_1.limit_build_secrets_scope

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_vuln_scanning(glEntity, glObject):

    test = build_environment_2_1.vuln_scanning

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_disable_build_tools_default_passwords(glEntity, glObject):

    test = build_environment_2_1.disable_build_tools_default_passwords

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_secure_build_env_webhooks(glEntity, glObject):

    test = build_environment_2_1.secure_build_env_webhooks

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:

        secHookSSLVerify = Mock(
            url='https://example.com',
            enable_ssl_verification=True)

        secHookNoSSLVerify = Mock(
            url='https://example.com',
            enable_ssl_verification=False)

        unsecureHook = Mock(
            url='http://example.com',
            enable_ssl_verification=False)

        glEntity.hooks.list.return_value = []
        run(glEntity, glObject, test, True, **kwargs)

        glEntity.hooks.list.return_value = [
            secHookSSLVerify]
        run(glEntity, glObject, test, True, **kwargs)

        glEntity.hooks.list.return_value = [
            secHookNoSSLVerify]
        run(glEntity, glObject, test, False, **kwargs)

        glEntity.hooks.list.return_value = [
            unsecureHook]
        run(glEntity, glObject, test, False, **kwargs)

    for kwargs in kwarg:

        glEntity.hooks.list.side_effect = GitlabHttpError(response_code=403)
        run(glEntity, glObject, test, None, **kwargs)

        glEntity.hooks.list.side_effect = GitlabHttpError(response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_build_env_admins(glEntity, glObject):

    test = build_environment_2_1.build_env_admins

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:

        glEntity.members.list.return_value = [
            Mock(access_level=40),
            Mock(access_level=20),
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
            Mock(access_level=30),
            Mock(access_level=20)
        ]
        run(glEntity, glObject, test, False, **kwargs)

    for kwargs in kwarg:

        glEntity.members.list.side_effect = GitlabHttpError(response_code=403)
        run(glEntity, glObject, test, None, **kwargs)

        glEntity.members.list.side_effect = GitlabHttpError(response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isInstance': True})
