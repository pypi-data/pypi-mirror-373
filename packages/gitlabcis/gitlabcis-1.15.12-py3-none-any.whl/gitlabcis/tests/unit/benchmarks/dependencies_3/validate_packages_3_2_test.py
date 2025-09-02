# -----------------------------------------------------------------------------

from unittest.mock import Mock

from conftest import run

from gitlabcis.benchmarks.dependencies_3 import validate_packages_3_2

# -----------------------------------------------------------------------------


def test_org_wide_dependency_policy(glEntity, glObject, gqlClient):

    from gql.transport.exceptions import TransportServerError

    test = validate_packages_3_2.org_wide_dependency_policy

    glEntity.path_with_namespace = 'test/project'

    kwargs = {
        'graphQLEndpoint': 'https://gitlab.com/api/graphql',
        'graphQLHeaders': {'Authorization': 'Bearer token'},
        'isProject': True
    }

    gqlClient.return_value.execute.return_value = {'project': {}}
    run(glEntity, glObject, test, False, **kwargs)

    mock_result = {
        'project': {
            'scanExecutionPolicies': {
                'nodes': [
                    {
                        'enabled': True,
                        'yaml': '''
                            actions:
                              - scan: secret_detection
                              - scan: dast
                              - scan: cluster_image_scanning
                              - scan: container_scanning
                              - scan: sast
                              - scan: sast_iac
                              - scan: dependency_scanning
                            rules:
                              - type: pipeline
                                branches: ['*']
                        '''
                    }
                ]
            }
        }
    }
    gqlClient.return_value.execute.return_value = mock_result
    run(glEntity, glObject, test, True, **kwargs)

    mock_result = {
        'project': {
            'scanExecutionPolicies': {
                'nodes': [
                    {
                        'enabled': True,
                        'yaml': '''
                            actions:
                              - scan: dast
                            rules:
                              - type: pipeline
                                branches: ['*']
                        '''
                    }
                ]
            }
        }
    }
    gqlClient.return_value.execute.return_value = mock_result
    run(glEntity, glObject, test, False, **kwargs)

    gqlClient.return_value.execute.side_effect = \
        TransportServerError('GraphQL Error')
    run(glEntity, glObject, test, None, **kwargs)

    gqlClient.return_value.execute.side_effect = \
        AttributeError()
    run(glEntity, glObject, test, None, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_package_vuln_scanning(glEntity, glObject, unauthorised):

    from gitlab.exceptions import GitlabGetError
    from gitlab.v4.objects.files import ProjectFile

    test = validate_packages_3_2.package_vuln_scanning

    kwargs = {'isProject': True}
    # throw an exception
    unauthorised.settings.get.side_effect = Mock(side_effect=GitlabGetError(
        response_code=401))
    run(unauthorised, unauthorised, test, None, **kwargs)

    # test success
    settings = Mock(auto_devops_enabled=True)
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    # test success
    settings = Mock(auto_devops_enabled=False)
    glObject.settings.get.return_value = settings

    glEntity.ci_config_path = ''
    _projectFile = Mock(spec=ProjectFile)

    # We need to fake "file contents" as base64 encoded str
    # its value is: dependency_scanning
    # this is passed to the ci.searchConfig() function

    _projectFile.content = 'ZGVwZW5kZW5jeV9zY2FubmluZw=='
    glEntity.files.get.return_value = _projectFile
    run(glEntity, glObject, test, True, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_package_license_scanning(glEntity, glObject, unauthorised):

    from gitlab.exceptions import GitlabGetError
    from gitlab.v4.objects.files import ProjectFile

    test = validate_packages_3_2.package_license_scanning

    kwargs = {'isProject': True}
    # throw an exception
    unauthorised.settings.get.side_effect = Mock(side_effect=GitlabGetError(
        response_code=401))
    run(unauthorised, unauthorised, test, None, **kwargs)

    # test success
    settings = Mock(auto_devops_enabled=True)
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)
    run(glEntity, glObject, test, True, **{'isInstance': True})

    # test fail
    # we need to bypass the run function and call the test directly
    settings = Mock(auto_devops_enabled=False)
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **{'isInstance': True})

    glEntity.ci_config_path = 'https://gitlab.com/.gitlab-ci.yml'
    assert next(iter(validate_packages_3_2.package_license_scanning(
            glEntity, glObject, **kwargs))) is None

    # test success
    settings = Mock(auto_devops_enabled=False)
    glObject.settings.get.return_value = settings

    glEntity.ci_config_path = ''
    _projectFile = Mock(spec=ProjectFile)

    # We need to fake "file contents" as base64 encoded str
    # its value is: dependency_scanning
    # this is passed to the ci.searchConfig() function

    _projectFile.content = 'ZGVwZW5kZW5jeV9zY2FubmluZw=='
    glEntity.files.get.return_value = _projectFile
    run(glEntity, glObject, test, True, **kwargs)

    run(glEntity, glObject, test, None, **{'isGroup': True})

# -----------------------------------------------------------------------------


def test_package_ownership_change(glEntity, glObject):

    test = validate_packages_3_2.package_ownership_change

    run(glEntity, glObject, test, None)
