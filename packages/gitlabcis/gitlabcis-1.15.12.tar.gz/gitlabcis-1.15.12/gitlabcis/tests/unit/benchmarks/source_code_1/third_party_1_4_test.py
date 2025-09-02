# -----------------------------------------------------------------------------

from unittest.mock import Mock

from conftest import run

from gitlabcis.benchmarks.source_code_1 import third_party_1_4

# -----------------------------------------------------------------------------


def test_admin_approval_for_app_installs(glEntity, glObject):

    test = third_party_1_4.admin_approval_for_app_installs

    run(glEntity, glObject, test, True)

# -----------------------------------------------------------------------------


def test_stale_app_reviews(glEntity, glObject, gqlClient):

    from gql.transport.exceptions import TransportServerError

    test = third_party_1_4.stale_app_reviews

    kwargs = {
        'graphQLEndpoint': 'https://example.com/graphql',
        'graphQLHeaders': {'Authorization': 'Bearer token'},
        'isProject': True
    }
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": []
            }
        }
    }
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {}
    }
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


def test_least_privilge_app_permissions(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = third_party_1_4.least_privilge_app_permissions

    kwargs = {'isProject': True}
    unauthorised.integrations.list.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **kwargs)

    glEntity.integrations.list.return_value = ['one']
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.integrations.list.return_value = []
    run(glEntity, glObject, test, True, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_secure_webhooks(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = third_party_1_4.secure_webhooks

    kwarg = [{'isProject': True}, {'isInstance': True}]

    unauthorised.hooks.list.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **{'isProject': True})

    for kwargs in kwarg:

        hook = Mock()
        hook.name = 'http test'
        hook.enable_ssl_verification = False
        hook.url = 'http://example.com'
        glEntity.hooks.list.return_value = [hook]
        glObject.hooks.list.return_value = [hook]
        run(glEntity, glObject, test, False, **kwargs)

        hook.enable_ssl_verification = True
        hook.name = 'pass result'
        hook.url = 'https://example.com'
        glEntity.hooks.list.return_value = [hook]
        glObject.hooks.list.return_value = [hook]
        run(glEntity, glObject, test, True, **kwargs)

        glEntity.hooks.list.return_value = []
        glObject.hooks.list.return_value = []
        run(glEntity, glObject, test, None, **kwargs)

    run(glEntity, glObject, test, None, **{'isGroup': True})
