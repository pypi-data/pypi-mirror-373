# -------------------------------------------------------------------------


def org_wide_dependency_policy(glEntity, glObject, **kwargs):
    """
    id: 3.2.1
    title: Ensure an organization-wide dependency usage policy
    is enforced
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gql import Client, gql
    from gql.transport.exceptions import (TransportAlreadyConnected,
                                          TransportServerError)
    from gql.transport.requests import RequestsHTTPTransport
    from graphql import GraphQLError

    from gitlabcis.utils import ci

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
                scanExecutionPolicies {
                nodes {
                    name
                    enabled
                    yaml
                }
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
            secret_detection_policy_found = False
            for policy in results['project']['scanExecutionPolicies']['nodes']:
                if policy.get('enabled') is True:
                    policy_yaml = ci.safeLoad(policy.get('yaml', ''))
                    actions = policy_yaml.get('actions', [])
                    for action in actions:
                        if action.get('scan') == 'dependency_scanning':
                            secret_detection_policy_found = True

            if secret_detection_policy_found:
                return {
                    True: (
                        'Scan Execution Policy for dependency_scanning is '
                        'enabled'
                        )
                    }
            else:
                return {
                    False: (
                        'Scan Execution Policy for dependency_scanning '
                        'is not enabled'
                    )
                }

        except KeyError:
            return {False: 'Scan Execution Policy was not found'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def package_vuln_scanning(glEntity, glObject, **kwargs):
    """
    id: 3.2.2
    title: Ensure packages are automatically scanned for known
           vulnerabilities
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            settings = glObject.settings.get()

            if settings.auto_devops_enabled is True:
                return {True: 'Dependency Scanning is '
                        'enabled via Auto DevOps'}

            return ci.searchConfig(
                glEntity, glObject, 'dependency_scanning')

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def package_license_scanning(glEntity, glObject, **kwargs):
    """
    id: 3.2.3
    title: Ensure packages are automatically scanned
           for license implications
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject') or kwargs.get('isInstance'):
        try:
            settings = glObject.settings.get()

            _successAddon = ('On GitLab self-managed, you also can choose '
                             'package registry metadata to synchronize '
                             'in the Admin Area for the GitLab instance. '
                             'You also must allow outbound network traffic '
                             'from your GitLab instance to the domain '
                             'storage.googleapis.com.')

            if settings.auto_devops_enabled is True:
                return {True: 'Dependency Scanning which is required so '
                        'packages be automatically scanned is '
                        f'enabled via Auto DevOps. {_successAddon}'}
            else:
                if kwargs.get('isInstance'):
                    return {False: 'Auto DevOps is not enabled at the '
                            'instance level'}

            _result = ci.searchConfig(
                glEntity, glObject, 'dependency_scanning')

            result, reason = _result.popitem()

            if result is True:
                return {True: 'Dependency Scanning which is required for '
                        'packages to be automatically scanned is '
                        f'configured in .gitlab-ci.yml. {_successAddon}'}
            else:
                return {result: reason}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def package_ownership_change(glEntity, glObject, **kwargs):
    """
    id: 3.2.4
    title: Ensure packages are automatically scanned for
           ownership change
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
