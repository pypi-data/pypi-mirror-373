# -------------------------------------------------------------------------


def limit_certifying_artifacts(glEntity, glObject, **kwargs):
    """
    id: 4.2.1
    title: Ensure the authority to certify artifacts is limited
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}


# -------------------------------------------------------------------------


def limit_artifact_uploaders(glEntity, glObject, **kwargs):
    """
    id: 4.2.2
    title: Ensure number of permitted users who may upload new
           artifacts is minimized
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            members = glEntity.members.list(all=True)
            maintainer_and_above = sum(
                1 for member in members if
                member.access_level >= 40)
            total_members = len(members)

            if maintainer_and_above and total_members == 0 \
                    or total_members == 0:
                return {None: 'No members found'}

            maintainer_and_above_percentage = (
                (maintainer_and_above / total_members) * 100
            )
            if maintainer_and_above_percentage < 20 \
                    or maintainer_and_above < 3:
                return {True: 'Number of permitted users who can upload new '
                        ' artifacts are limited'}
            else:
                return {False: 'Number of permitted users who can upload new '
                        ' artifacts are not limited'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def require_mfa_to_package_registry(glEntity, glObject, **kwargs):
    """
    id: 4.2.3
    title: Ensure user access to the package registry utilizes Multi-
           Factor Authentication (MFA)
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # applicable for all input types
    try:
        settings = glObject.settings.get()
        if settings.require_two_factor_authentication:
            return {True: 'Enforce two-factor authentication is enabled'}
        else:
            return {False: 'Enforce two-factor authentication is not enabled'}
    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def external_auth_server(glEntity, glObject, **kwargs):
    """
    id: 4.2.4
    title: Ensure user management of the package registry is not
           local
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def restrict_anonymous_access(glEntity, glObject, **kwargs):
    """
    id: 4.2.5
    title: Ensure anonymous access to artifacts is revoked
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # applicable for all input types
    try:
        settings = glObject.settings.get()
        project_visibility = settings.default_project_visibility

        if (project_visibility == 'public'):
            return {False: 'Default project visibility is: public'}
        else:
            return {True: 'Default project visibility is: '
                    f'{project_visibility}'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def minimum_package_registry_admins(glEntity, glObject, **kwargs):
    """
    id: 4.2.6
    title: Ensure minimum number of administrators are set for the
           package registry
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            members = glEntity.members.list(all=True)
            reporter_and_above = sum(
                1 for member in members if
                member.access_level >= 20)
            total_members = len(members)

            if reporter_and_above and total_members == 0 \
                    or total_members == 0:
                return {None: 'No members found'}

            reporter_and_above_percentage = (
                (reporter_and_above / total_members) * 100
            )
            if reporter_and_above_percentage < 40 or reporter_and_above < 3:
                return {True: 'Build access is limited, less than 40% '
                        'of the members have Reporter/Developer role or above'}
            else:
                return {False: 'Build access is not limited, over 40% '
                        'of the members have Reporter/Developer role or above'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}
