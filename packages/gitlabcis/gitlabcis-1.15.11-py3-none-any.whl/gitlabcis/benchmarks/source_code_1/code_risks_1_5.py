# -------------------------------------------------------------------------

def enable_secret_detection(glEntity, glObject, **kwargs):
    """
    id: 1.5.1
    title: Ensure scanners are in place to identify and prevent sensitive
           data in code
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'SECRET_DETECTION' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'Secret Detection is enabled'}

            else:
                return {False: 'Secret Detection is not enabled'}

        except KeyError:
            return {False: 'Secret Detection is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'This check requires validation'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def secure_pipeline_instructions(glEntity, glObject, **kwargs):
    """
    id: 1.5.2
    title: Detect and prevent misconfigurations and insecure instructions
           in CI pipelines
    """

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def secure_iac_instructions(glEntity, glObject, **kwargs):
    """
    id: 1.5.3
    title: Ensure scanners are in place to secure Infrastructure as Code
           (IaC) instructions
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'SAST' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'SAST Scanning is enabled'}

            else:
                return {False: 'SAST Scanning is not enabled'}

        except KeyError:
            return {False: 'SAST Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def vulnerability_scanning(glEntity, glObject, **kwargs):
    """
    id: 1.5.4
    title: Ensure scanners are in place for code vulnerabilities
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'SAST' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'Vulnerability Scanning is enabled'}

            else:
                return {False: 'Vulnerability Scanning is not enabled'}

        except KeyError:
            return {False: 'Vulnerability Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def dependency_scanning(glEntity, glObject, **kwargs):
    """
    id: 1.5.5
    title: Ensure scanners are in place for open-source vulnerabilities in
           used packages
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'DEPENDENCY_SCANNING' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'Dependency Scanning is enabled'}

            else:
                return {False: 'Dependency Scanning is not enabled'}

        except KeyError:
            return {False: 'Dependency Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def license_scanning(glEntity, glObject, **kwargs):
    """
    id: 1.5.6
    title: Ensure scanners are in place for open-source license issues in
           used packages
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            # License scanning is covered under dependency scanning:
            if 'DEPENDENCY_SCANNING' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'License Scanning is enabled'}

            else:
                return {False: 'License Scanning is not enabled'}

        except KeyError:
            return {False: 'License Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def dast_web_scanning(glEntity, glObject, **kwargs):
    """
    id: 1.5.7
    title: Ensure scanners are in place for web application runtime
           security weaknesses
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'DAST' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'DAST Scanning is enabled'}

            else:
                return {False: 'DAST Scanning is not enabled'}

        except KeyError:
            return {False: 'DAST Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def dast_api_scanning(glEntity, glObject, **kwargs):
    """
    id: 1.5.8
    title: Ensure scanners are in place for API runtime security weaknesses
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

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:

            if 'DAST' in \
                    results['project']['securityScanners']['enabled']:
                return {True: 'DAST Scanning is enabled'}

            else:
                return {False: 'DAST Scanning is not enabled'}

        except KeyError:
            return {False: 'DAST Scanning is not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}
