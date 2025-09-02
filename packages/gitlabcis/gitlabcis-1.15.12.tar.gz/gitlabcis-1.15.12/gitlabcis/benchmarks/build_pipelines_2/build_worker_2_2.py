# -------------------------------------------------------------------------


def single_use_workers(glEntity, glObject, **kwargs):
    """
    id: 2.2.1
    title: Ensure build workers are single-used
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def pass_worker_envs_and_commands(glEntity, glObject, **kwargs):
    """
    id: 2.2.2
    title: Ensure build worker environments and commands are
           passed and not pulled
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def segregate_worker_duties(glEntity, glObject, **kwargs):
    """
    id: 2.2.3
    title: Ensure the duties of each build worker are segregated
    """
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        # ---------------------------------------------------------------------

        if kwargs.get('isProject'):

            if any([runner for runner in
                    glEntity.runners.list(get_all=True)
                    if not runner.is_shared]):
                return {True: 'project_assigned_runners are available'}

            return {False: 'No project_assigned_runners are available'}

        # ---------------------------------------------------------------------

        elif kwargs.get('isInstance'):

            if any([runner for runner in
                    glObject.runners.list(get_all=True)
                    if not runner.is_shared]):

                return {True: 'Instance runners are available'}

            return {False: 'No instance runners are available'}

        # ---------------------------------------------------------------------

        elif kwargs.get('isGroup'):
            if any([runner for runner in
                    glEntity.runners.list(get_all=True)
                    if not runner.is_shared]):
                return {True: 'Group runners are available'}

            return {False: 'No group runners are available'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def restrict_worker_connectivity(glEntity, glObject, **kwargs):
    """
    id: 2.2.4
    title: Ensure build workers have minimal network connectivity
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def worker_runtime_security(glEntity, glObject, **kwargs):
    """
    id: 2.2.5
    title: Ensure run-time security is enforced for build workers
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def build_worker_vuln_scanning(glEntity, glObject, **kwargs):
    """
    id: 2.2.6
    title: Ensure build workers are automatically scanned for
           vulnerabilities
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def store_worker_config(glEntity, glObject, **kwargs):
    """
    id: 2.2.7
    title: Ensure build workers' deployment configuration is stored in
           a version control platform
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
                return {True: 'Build workers deployment configuration '
                        'is stored in a version control platform'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def monitor_worker_resource_consumption(glEntity, glObject, **kwargs):
    """
    id: 2.2.8
    title: Ensure resource consumption of build workers is monitored
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
