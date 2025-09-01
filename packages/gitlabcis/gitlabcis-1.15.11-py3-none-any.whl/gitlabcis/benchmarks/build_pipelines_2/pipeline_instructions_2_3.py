# -------------------------------------------------------------------------


def build_steps_as_code(glEntity, glObject, **kwargs):
    """
    id: 2.3.1
    title: Ensure all build steps are defined as code
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}
            else:
                return {True: 'Build steps are defined as code'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def build_stage_io(glEntity, glObject, **kwargs):
    """
    id: 2.3.2
    title: Ensure steps have clearly defined build stage input and
           output
    """

    import base64

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}

            gl_ci_yml_content = ciFile.content
            gl_ci_yml_decode = base64.b64decode(
                gl_ci_yml_content).decode('utf-8')
            gitlab_ci_yml_dict = ci.safeLoad(gl_ci_yml_decode)
            if not gitlab_ci_yml_dict:
                return {False: 'gitlab_ci_yml file is empty'}
            else:
                if ('stages' in gitlab_ci_yml_dict
                        and 'build' in gitlab_ci_yml_dict['stages']):
                    build_jobs = [
                        job_name
                        for job_name, job in gitlab_ci_yml_dict.items()
                        if isinstance(job, dict) and
                        job.get('stage') == 'build'
                    ]
                    if not build_jobs:
                        return {True: 'No build stage detected'
                                ' in gitlab_ci_yml'}
                    for job_name in build_jobs:
                        job = gitlab_ci_yml_dict[job_name]
                        if 'script' in job:
                            if 'artifacts' in job:
                                continue
                            else:
                                return {False: 'No output found for a '
                                        'job in the build stage'}
                        else:
                            return {False: 'No script found for '
                                    'a job in the build stage'}
                else:
                    return {False: 'No build stages detected in gitlab_ci_yml'}
                return {True: 'input and output has defined '
                        'for each build stage.'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def secure_pipeline_output(glEntity, glObject, **kwargs):
    """
    id: 2.3.3
    title: Ensure output is written to a separate, secured storage
           repository
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def track_pipeline_files(glEntity, glObject, **kwargs):
    """
    id: 2.3.4
    title: Ensure changes to pipeline files are tracked and reviewed
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}
            else:
                return {True: 'changes to pipeline files are '
                        'being tracked and reviewed'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def limit_pipeline_triggers(glEntity, glObject, **kwargs):
    """
    id: 2.3.5
    title: Ensure access to build process triggering is minimized
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            protected_environments = glEntity.protected_environments.list(
                get_all=False)

            if not protected_environments:
                return {False: 'No protected environment detected'}
            return {None: 'This check requires validation'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}
            if e.response_code == 404:
                return {None: 'Protected Environments not available'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def pipeline_misconfiguration_scanning(glEntity, glObject, **kwargs):
    """
    id: 2.3.6
    title: Ensure pipelines are automatically scanned for
           misconfigurations
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gql import Client, gql
    from gql.transport.exceptions import (TransportAlreadyConnected,
                                          TransportServerError)
    from gql.transport.requests import RequestsHTTPTransport
    from graphql import GraphQLError

    from gitlabcis.utils import ci

    if kwargs.get('isProject') or kwargs.get('isGroup'):
        try:

            variables = {
                'fullPath': glEntity.path_with_namespace
                if kwargs.get('isProject')
                else glEntity.full_path
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
  group(fullPath: $fullPath) {
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

        # when pytest runs without auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:
            required_scans = [
                'dast', 'secret_detection', 'cluster_image_scanning',
                'container_scanning', 'sast', 'sast_iac', 'dependency_scanning'
            ]

            scans_found = set()
            dast_policy_found = False
            sast_policy_found = False

            if kwargs.get('isProject'):
                _policies \
                    = results['project']['scanExecutionPolicies']['nodes']

            elif kwargs.get('isGroup'):
                _policies = results['group']['scanExecutionPolicies']['nodes']

            for policy in _policies:
                if policy.get('enabled') is True:
                    policy_yaml = ci.safeLoad(policy.get('yaml', ''))
                    actions = policy_yaml.get('actions', [])
                    rules = policy_yaml.get('rules', [])
                    for action in actions:
                        scans_found.add(action.get('scan'))
                        if action.get('scan') == 'sast':
                            for rule in rules:
                                if (
                                    rule.get('type') == 'pipeline'
                                    and '*' in rule.get('branches', [])
                                ):
                                    sast_policy_found = True
                        elif action.get('scan') == 'dast':
                            for rule in rules:
                                if (
                                    rule.get('type') == 'pipeline'
                                    and '*' in rule.get('branches', [])
                                ):
                                    dast_policy_found = True
            missing_scans = [
                scan for scan in required_scans
                if scan not in scans_found
                ]
            if (dast_policy_found and sast_policy_found):
                if missing_scans:
                    return {
                        True: (
                            'Scan Execution Policy for sast and dast is '
                            'enabled and triggers for all pipelines and '
                            'branches. Other missing scans for manual review:'
                            f'{", ".join(missing_scans)}'
                        )
                    }
                else:
                    return {
                        True: (
                            'Scan Execution Policy for sast and dast is '
                            'enabled and triggers for all pipelines and '
                            'branches. All required scans are covered.'
                        )
                    }
            else:
                return {
                    False: (
                        'Required Scan Execution Policy '
                        'is not enabled to trigger for all pipelines '
                        'and branches. Missing scans to '
                        f'review: {", ".join(missing_scans)}'
                    )
                }
        except KeyError:
            return {False: 'Scan Execution Policy was not found'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

# -------------------------------------------------------------------------


def pipeline_vuln_scanning(glEntity, glObject, **kwargs):
    """
    id: 2.3.7
    title: Ensure pipelines are automatically scanned for
           vulnerabilities
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gql import Client, gql
    from gql.transport.exceptions import (TransportAlreadyConnected,
                                          TransportServerError)
    from gql.transport.requests import RequestsHTTPTransport
    from graphql import GraphQLError

    from gitlabcis.utils import ci

    if kwargs.get('isProject') or kwargs.get('isGroup'):
        try:

            variables = {
                'fullPath': glEntity.path_with_namespace
                if kwargs.get('isProject')
                else glEntity.full_path
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
  group(fullPath: $fullPath) {
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
            required_scans = [
                'dast', 'secret_detection', 'cluster_image_scanning',
                'container_scanning', 'sast', 'sast_iac', 'dependency_scanning'
            ]

            scans_found = set()
            dast_policy_found = False
            sast_policy_found = False

            if kwargs.get('isProject'):
                _policies \
                    = results['project']['scanExecutionPolicies']['nodes']

            elif kwargs.get('isGroup'):
                _policies = results['group']['scanExecutionPolicies']['nodes']

            for policy in _policies:
                if policy.get('enabled') is True:
                    policy_yaml = ci.safeLoad(policy.get('yaml', ''))
                    actions = policy_yaml.get('actions', [])
                    rules = policy_yaml.get('rules', [])
                    for action in actions:
                        scans_found.add(action.get('scan'))
                        if action.get('scan') == 'sast':
                            for rule in rules:
                                if (
                                    rule.get('type') == 'pipeline'
                                    and '*' in rule.get('branches', [])
                                ):
                                    sast_policy_found = True
                        elif action.get('scan') == 'dast':
                            for rule in rules:
                                if (
                                    rule.get('type') == 'pipeline'
                                    and '*' in rule.get('branches', [])
                                ):
                                    dast_policy_found = True
            missing_scans = [
                scan for scan in required_scans
                if scan not in scans_found
                ]
            if (dast_policy_found and sast_policy_found):
                if missing_scans:
                    return {
                        True: (
                            'Scan Execution Policy for sast and dast is '
                            'enabled and triggers for all pipelines and '
                            'branches. Other missing scans for manual review:'
                            f'{", ".join(missing_scans)}'
                        )
                    }
                else:
                    return {
                        True: (
                            'Scan Execution Policy for sast and dast is '
                            'enabled and triggers for all pipelines and '
                            'branches. All required scans are covered.'
                        )
                    }
            else:
                return {
                    False: (
                        'Required Scan Execution Policy '
                        'is not enabled to trigger for all pipelines '
                        'and branches. Missing scans to '
                        f'review: {", ".join(missing_scans)}'
                    )
                }
        except KeyError:
            return {False: 'Scan Execution Policy was not found'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

# -------------------------------------------------------------------------


def pipeline_secret_scanning(glEntity, glObject, **kwargs):
    """
    id: 2.3.8
    title: Ensure scanners are in place to identify and prevent
           sensitive data in pipeline files
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:

            _result = ci.searchConfig(
                glEntity, glObject, 'secret-detection')

            result, reason = _result.popitem()

            if result is True:
                return {True: 'Secret-Detection is enabled'}
            else:
                return {False: 'Secret-Detection is not enabled'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}
