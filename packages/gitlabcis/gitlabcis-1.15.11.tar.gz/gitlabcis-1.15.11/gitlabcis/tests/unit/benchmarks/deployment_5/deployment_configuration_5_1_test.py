# -----------------------------------------------------------------------------

from unittest.mock import Mock, patch

import pytest  # noqa: F401
from conftest import run
from gitlab.exceptions import GitlabHttpError

from gitlabcis.benchmarks.deployment_5 import deployment_configuration_5_1

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.getConfig')
def test_separate_deployment_config(mockGetConfig, glEntity, glObject):

    test = deployment_configuration_5_1.separate_deployment_config

    kwargs = {'isProject': True}
    mockGetConfig.return_value = {None: 'No CI file found'}
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.return_value = {False: 'Invalid CI file'}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {Mock(file_path=None): None}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {Mock(file_path='.gitlab-ci.yml'): None}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {
        Mock(file_path='.gitlab/.gitlab-ci.yml'): None}
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.getConfig')
def test_audit_deployment_config(mockGetConfig, glEntity, glObject):

    test = deployment_configuration_5_1.audit_deployment_config

    kwargs = {'isProject': True}
    mockGetConfig.return_value = {None: 'No CI file found'}
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.return_value = {False: 'Invalid CI file'}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {'gitlab-ci.yml': None}
    glEntity.approvalrules.list.return_value = [Mock(approvals_required=0)]
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {'gitlab-ci.yml': None}
    glEntity.approvalrules.list.return_value = [Mock(approvals_required=2)]
    glObject.get_license.return_value = {'plan': 'GOLD PLATED PLATNUM'}
    run(glEntity, glObject, test, False, **kwargs)

    mockGetConfig.return_value = {'gitlab-ci.yml': None}
    glEntity.approvalrules.list.return_value = [Mock(approvals_required=2)]
    glObject.get_license.return_value = {'plan': 'ultimate'}
    run(glEntity, glObject, test, True, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockGetConfig.side_effect = GitlabHttpError('Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.searchConfig')
def test_secret_scan_deployment_config(mockSearchConfig, glEntity, glObject):

    test = deployment_configuration_5_1.secret_scan_deployment_config

    kwargs = {'isProject': True}
    mockSearchConfig.return_value = {True: 'Secret-Detection found'}
    run(glEntity, glObject, test, True, **kwargs)

    mockSearchConfig.return_value = {False: 'Secret-Detection not found'}
    run(glEntity, glObject, test, False, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwargs = {'isInstance': True}
    settings = Mock()
    for bool in [True, False]:
        settings.get.return_value = \
            {'pre_receive_secret_detection_enabled': bool}
        settings.get.side_effect = lambda key: \
            bool if key == 'pre_receive_secret_detection_enabled' else None
        glObject.settings.get.return_value = settings
        run(glEntity, glObject, test, bool, **kwargs)

    run(glEntity, glObject, test, None, **{'isGroup': True})

# -----------------------------------------------------------------------------


def test_limit_deployment_config_access(glEntity, glObject):

    test = deployment_configuration_5_1.limit_deployment_config_access

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


@patch('gitlabcis.utils.ci.searchConfig')
def test_scan_iac(mockSearchConfig, glEntity, glObject):

    test = deployment_configuration_5_1.scan_iac

    kwargs = {'isProject': True}
    mockSearchConfig.return_value = {True: 'SAST-IaC found'}
    run(glEntity, glObject, test, True, **kwargs)

    mockSearchConfig.return_value = {False: 'SAST-IaC not found'}
    run(glEntity, glObject, test, False, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    mockSearchConfig.side_effect = GitlabHttpError(response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_verify_deployment_config(glEntity, glObject):

    test = deployment_configuration_5_1.verify_deployment_config

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_pin_deployment_config_manifests(glEntity, glObject):

    test = deployment_configuration_5_1.pin_deployment_config_manifests

    run(glEntity, glObject, test, None)
