# -------------------------------------------------------------------------


def verify_artifacts(glEntity, glObject, **kwargs):
    """
    id: 3.1.1
    title: Ensure third-party artifacts and open-source
           libraries are verified
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def third_party_sbom_required(glEntity, glObject, **kwargs):
    """
    id: 3.1.2
    title: Ensure Software Bill of Materials (SBOM) is required from
           all third-party suppliers
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def verify_signed_metadata(glEntity, glObject, **kwargs):
    """
    id: 3.1.3
    title: Ensure signed metadata of the build process is required and
           verified
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def monitor_dependencies(glEntity, glObject, **kwargs):
    """
    id: 3.1.4
    title: Ensure dependencies are monitored between open-source
           components
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gql import Client, gql
    from gql.transport.exceptions import (TransportAlreadyConnected,
                                          TransportServerError)
    from gql.transport.requests import RequestsHTTPTransport
    from graphql import GraphQLError

    if kwargs.get('isProject'):
        try:

            variables = {
                'fullPath': glEntity.path_with_namespace
            }

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        client = Client(
            transport=RequestsHTTPTransport(
                url=kwargs.get('graphQLEndpoint'),
                headers=kwargs.get('graphQLHeaders'),
                use_json=True,
                verify=kwargs.get('sslVerify')
            ),
            fetch_schema_from_transport=True
        )

        query = gql('''
        query GetSecurityScanners($fullPath: ID!) {
            project(fullPath: $fullPath) {
                securityScanners {
                    enabled
                }
            }
        }
        ''')

        try:

            results = client.execute(query, variable_values=variables)

        except (GraphQLError, TransportServerError, TransportAlreadyConnected):
            return {None: 'Error: Issue with GraphQL Query'}

        # pytest no auth
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:
            enabledScanners = results["project"]["securityScanners"]["enabled"]
            dependencyScanningEnabled = \
                "DEPENDENCY_SCANNING" in enabledScanners
            containerScanningEnabled = \
                "CONTAINER_SCANNING" in enabledScanners
            if (dependencyScanningEnabled and containerScanningEnabled):
                return {True: 'DEPENDENCY SCANNING and '
                        'CONTAINER SCANNING are enabled'}
            elif (dependencyScanningEnabled and not containerScanningEnabled):
                return {False: 'DEPENDENCY SCANNING is enabled but '
                        'CONTAINER SCANNING is not enabled'}
            elif (containerScanningEnabled and not dependencyScanningEnabled):
                return {False: 'CONTAINER SCANNING is enabled '
                        'but DEPENDENCY SCANNING is not enabled'}
            return {False: 'CONTAINER SCANNING and DEPENDENCY SCANNING '
                    'are not enabled'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        except KeyError:
            return {False: 'No scanners enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def define_package_managers(glEntity, glObject, **kwargs):
    """
    id: 3.1.5
    title: Ensure trusted package managers and repositories are
           defined and prioritized
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def dependency_sbom(glEntity, glObject, **kwargs):
    """
    id: 3.1.6
    title: Ensure a signed Software Bill of Materials (SBOM) of the
           code is supplied
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def pin_dependency_version(glEntity, glObject, **kwargs):
    """
    id: 3.1.7
    title: Ensure dependencies are pinned to a specific, verified
           version
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# ------------------------------------------------------------------------


def packages_over_60_days_old(glEntity, glObject, **kwargs):
    """
    id: 3.1.8
    title: Ensure all packages used are more than 60 days old
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
