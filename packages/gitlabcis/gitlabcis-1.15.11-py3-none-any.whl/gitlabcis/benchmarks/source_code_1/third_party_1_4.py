# -------------------------------------------------------------------------


def admin_approval_for_app_installs(glEntity, glObject, **kwargs):
    """
    id: 1.4.1
    title: Ensure administrator approval is required for every installed
           application
    """

    return {True: 'You are compliant by default. Only maintainers and '
                  'owners can integrate with external applications'}

# -------------------------------------------------------------------------


def stale_app_reviews(glEntity, glObject, **kwargs):
    """
    id: 1.4.2
    title: Ensure stale applications are reviewed and inactive ones are
           removed
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
            # dependency scanning alerts when there are stale applications
            # present:
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


def least_privilge_app_permissions(glEntity, glObject, **kwargs):
    """
    id: 1.4.3
    title: Ensure the access granted to each installed application is
           limited to the least privilege needed
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject'):
            integrations = glEntity.integrations.list(get_all=False)

            if len(integrations) == 0:
                return {True: 'No integrations found'}

            return {None: 'This check requires validation'}

        elif kwargs.get('isInstance'):
            return {None: 'This check requires validation'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for instances or groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def secure_webhooks(glEntity, glObject, **kwargs):
    """
    id: 1.4.4
    title: Ensure only secured webhooks are used
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:

        # -----------------------------------------------------------------

        def verify_hooks(hooks):

            if len(hooks) == 0:
                return {None: 'No hooks found'}

            for hook in hooks:

                if hook.enable_ssl_verification is False or \
                        hook.url.startswith('http://'):
                    return {False: f'Insecure hook: {hook.name} found'}

            return {True: 'All hooks use HTTPS and verify SSL'}

        # -----------------------------------------------------------------

        if kwargs.get('isProject'):

            return verify_hooks(glEntity.hooks.list(get_all=True))

        elif kwargs.get('isInstance'):

            return verify_hooks(glObject.hooks.list(get_all=True))

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for instances or groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
