# -------------------------------------------------------------------------


def automate_deployment(glEntity, glObject, **kwargs):
    """
    id: 5.2.1
    title: Ensure deployments are automated
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    try:
        if kwargs.get('isProject'):
            gitlab_ci_yml = ci.getConfig(glEntity, glObject, **kwargs)

            ciFile, reason = gitlab_ci_yml.popitem()

            if ciFile in [None, False]:
                return {ciFile: reason}
            else:
                return {None: 'Ci config file is available, '
                        'however this check requires manual '
                        'validation'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}


# -------------------------------------------------------------------------


def reproducible_deployment(glEntity, glObject, **kwargs):
    """
    id: 5.2.2
    title: Ensure the deployment environment is reproducible
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def limit_prod_access(glEntity, glObject, **kwargs):
    """
    id: 5.2.3
    title: Ensure access to production environment is limited
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def disable_default_passwords(glEntity, glObject, **kwargs):
    """
    id: 5.2.4
    title: Ensure default passwords are not used
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
