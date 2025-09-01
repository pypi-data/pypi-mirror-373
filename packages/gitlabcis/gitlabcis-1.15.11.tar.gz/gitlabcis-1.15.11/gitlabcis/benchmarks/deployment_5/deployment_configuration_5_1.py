# -------------------------------------------------------------------------


def separate_deployment_config(glEntity, glObject, **kwargs):
    """
    id: 5.1.1
    title: Ensure deployment configuration files are separated from
           source code
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            # get the ci config file obj:
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}

            # check its existence:
            if ciFile.file_path is None:
                return {False: 'separate ci config file not set for project'}

            # check for sub dirs:
            if '/' not in ciFile.file_path:
                return {False: 'ci config file is available but not in '
                        'a separated path'}

            return {True: 'ci config yml file is available, '
                    'and stored separately from this project '
                    'source code'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def audit_deployment_config(glEntity, glObject, **kwargs):
    """
    id: 5.1.2
    title: Ensure changes in deployment configuration are audited
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabLicenseError,
                                   GitlabListError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:

            # get the ci config file obj:
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}

            for approval in glEntity.approvalrules.list(get_all=True):
                if approval.approvals_required < 1:
                    return {False: 'at least one approval is required '
                            'for code changes'}

            if glObject.get_license().get('plan') \
                    not in ['premium', 'ultimate']:
                return {False: 'License does not allow audit'}

            return {True: 'Changes are audited , reviewed and tracked'}

        except (GitlabHttpError, GitlabGetError, GitlabLicenseError,
                GitlabAuthenticationError, GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}
            if e.response_code == 404:
                return {None: 'Approval rules not available'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def secret_scan_deployment_config(glEntity, glObject, **kwargs):
    """
    id: 5.1.3
    title: Ensure scanners are in place to identify and prevent
           sensitive data in deployment configuration
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            return ci.searchConfig(
                glEntity, glObject, 'Secret-Detection')

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):

        settings = glObject.settings.get()

        if settings.get('pre_receive_secret_detection_enabled') is True:
            return {True: 'Secret Detection is enabled globally'}
        else:
            return {False: 'Secret Detection is not enabled globally'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def limit_deployment_config_access(glEntity, glObject, **kwargs):
    """
    id: 5.1.4
    title: Limit access to deployment configurations
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def scan_iac(glEntity, glObject, **kwargs):
    """
    id: 5.1.5
    title: Scan Infrastructure as Code (IaC)
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            return ci.searchConfig(
                glEntity, glObject, 'SAST-IaC')

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for instances or groups'}

# -------------------------------------------------------------------------


def verify_deployment_config(glEntity, glObject, **kwargs):
    """
    id: 5.1.6
    title: Ensure deployment configuration manifests are verified
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def pin_deployment_config_manifests(glEntity, glObject, **kwargs):
    """
    id: 5.1.7
    title: Ensure deployment configuration manifests are pinned to a
           specific, verified version
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
