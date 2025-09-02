# -----------------------------------------------------------------------------

import pytest  # noqa: F401
from conftest import run

from gitlabcis.benchmarks.dependencies_3 import third_party_packages_3_1

# -----------------------------------------------------------------------------


def test_verify_artifacts(glEntity, glObject):

    test = third_party_packages_3_1.verify_artifacts

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_third_party_sbom_required(glEntity, glObject):

    test = third_party_packages_3_1.third_party_sbom_required

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_verify_signed_metadata(glEntity, glObject):

    test = third_party_packages_3_1.verify_signed_metadata

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_monitor_dependencies(glEntity, glObject, gqlClient):
    from gql.transport.exceptions import TransportServerError

    test = third_party_packages_3_1.monitor_dependencies

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
                "enabled": ["DEPENDENCY_SCANNING"]
            }
        }
    }
    run(glEntity, glObject, test, False, **kwargs)

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
        "project": {
            "securityScanners": {}
        }
    }
    run(glEntity, glObject, test, False, **kwargs)

    gqlClient.return_value.execute.side_effect = \
        TransportServerError('GraphQL Error')
    run(glEntity, glObject, test, None, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_define_package_managers(glEntity, glObject):

    test = third_party_packages_3_1.define_package_managers

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_dependency_sbom(glEntity, glObject):

    test = third_party_packages_3_1.dependency_sbom

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_pin_dependency_version(glEntity, glObject):

    test = third_party_packages_3_1.pin_dependency_version

    run(glEntity, glObject, test, None)

# -----------------------------------------------------------------------------


def test_packages_over_60_days_old(glEntity, glObject):

    test = third_party_packages_3_1.packages_over_60_days_old

    run(glEntity, glObject, test, None)
