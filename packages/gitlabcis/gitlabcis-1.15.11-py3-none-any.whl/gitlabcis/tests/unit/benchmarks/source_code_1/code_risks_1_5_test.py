# -----------------------------------------------------------------------------

from conftest import run

from gitlabcis.benchmarks.source_code_1 import code_risks_1_5

# -------------------------------------------------------------------------


def test_enable_secret_detection(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.enable_secret_detection

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
                "enabled": ["SECRET_DETECTION", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING"]
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

# -------------------------------------------------------------------------


def test_secure_pipeline_instructions(glEntity, glObject, unauthorised):

    test = code_risks_1_5.secure_pipeline_instructions
    run(glEntity, glObject, test, None)

# -------------------------------------------------------------------------


def test_secure_iac_instructions(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.secure_iac_instructions

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
                "enabled": ["SAST", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING"]
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

# -------------------------------------------------------------------------


def test_vulnerability_scanning(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.vulnerability_scanning

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
                "enabled": ["SAST", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING"]
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

# -------------------------------------------------------------------------


def test_dependency_scanning(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.dependency_scanning

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

# -------------------------------------------------------------------------


def test_license_scanning(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.license_scanning

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

# -------------------------------------------------------------------------


def test_dast_web_scanning(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.dast_web_scanning

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
                "enabled": ["DAST", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING"]
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

# -------------------------------------------------------------------------


def test_dast_api_scanning(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = code_risks_1_5.dast_api_scanning

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
                "enabled": ["DAST", "CONTAINER_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.path_with_namespace = 'test/project'
    gqlClient.return_value.execute.return_value = {
        "project": {
            "securityScanners": {
                "enabled": ["DEPENDENCY_SCANNING"]
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
