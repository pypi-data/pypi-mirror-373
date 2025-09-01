# -------------------------------------------------------------------------

def review_and_remove_inactive_users(glEntity, glObject, **kwargs):
    """
    id: 1.3.1
    title: Ensure inactive users are reviewed and removed periodically
    """

    from datetime import datetime, timezone

    from dateutil.relativedelta import relativedelta
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject') or kwargs.get('isInstance'):
            ninetyDaysAgo = datetime.now(timezone.utc) - relativedelta(days=90)

            users = glObject.users.list(per_page=100, iterator=True)

            for user in users:

                # a regular PAT is not going to return this value:
                try:
                    if user.last_activity_on is None:
                        continue
                except AttributeError:
                    return {None: 'Insufficient permissions'}

                if datetime.strptime(
                    user.last_activity_on,
                    '%Y-%m-%d'
                        ).replace(tzinfo=timezone.utc) > ninetyDaysAgo:
                    return {
                        False: f'User: {user.username} found with last '
                        'activity longer than 90 days'}

            return {True: 'No users found with activity longer than 90 days'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def limit_top_level_group_creation(glEntity, glObject, **kwargs):
    """
    id: 1.3.2
    title: Ensure top-level group creation is limited to specific members
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # available for all input types
    try:
        if glObject.settings.get().can_create_group is False:
            return {True: 'Top-level group creation is limited'}

        return {False: 'Top-level group creation is not limited'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def minimum_number_of_admins(glEntity, glObject, **kwargs):
    """
    id: 1.3.3
    title: Ensure minimum number of administrators are set for the
           organization
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        if kwargs.get('isProject'):
            members = glEntity.members_all.list(get_all=True)

            totalMembers = len(members)

            if totalMembers == 1:
                return {None: 'Only 1 member found'}

            # Access levels:
            #   No access      0
            #   Minimal access 5
            #   Guest          10
            #   Reporter       20
            #   Developer      30
            #   Maintainer     40
            #   Owner          50

            ownersOrMaintainers = []
            for member in members:
                if member.access_level >= 40:
                    ownersOrMaintainers.append(member)

            if len(ownersOrMaintainers) < totalMembers:
                return {True: 'Less owners/maintainers than members set'}

            return {False: 'Access levels not restrictive for members'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def require_mfa_for_contributors(glEntity, glObject, **kwargs):
    """
    id: 1.3.4
    title: Ensure Multi-Factor Authentication (MFA) is required for
           contributors of new code
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # available for all input types
    try:
        _settings = glObject.settings.get()

        if _settings.require_two_factor_authentication is True:
            return {True: 'Two Factor Authentication is required'}

        return {False: 'Two Factor Authentication is not required'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def require_mfa_at_org_level(glEntity, glObject, **kwargs):
    """
    id: 1.3.5
    title: Ensure the organization is requiring members to use
           Multi-Factor Authentication (MFA)
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # available for all input types
    try:
        _settings = glObject.settings.get()

        if _settings.require_two_factor_authentication is True:
            return {True: 'Two Factor Authentication is required'}

        if _settings.two_factor_grace_period != 0:
            return {True: 'Grace period is set for Two Factor Authentication'}

        return {False: 'Two Factor Authentication is not required'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def limit_user_registration_domain(glEntity, glObject, **kwargs):
    """
    id: 1.3.6
    title: Ensure new members are required to be invited using
           company-approved email
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def ensure_2_admins_per_repo(glEntity, glObject, **kwargs):
    """
    id: 1.3.7
    title: Ensure two administrators are set for each repository
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        if kwargs.get('isProject'):
            owners = 0
            members = glEntity.members_all.list(get_all=True)

            for member in members:

                if member.access_level == 50:
                    owners += 1

                    if owners == 2:
                        return {True: 'Two repository owners found'}

            return {
                True: 'No repository owners found'
                if owners == 0
                else f'Only found: {owners} owners'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for instances or groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

    # this throws an attr error if accessed anonymously (pytest no auth)
    except AttributeError:
        return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def strict_permissions_for_repo(glEntity, glObject, **kwargs):
    """
    id: 1.3.8
    title: Ensure strict base permissions are set for repositories
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject'):
            members = glEntity.members_all.list(get_all=True)

            totalMembers = len(members)

            if totalMembers == 1:
                return {None: 'Only 1 member found'}

            # Access levels:
            #   No access      0
            #   Minimal access 5
            #   Guest          10
            #   Reporter       20
            #   Developer      30
            #   Maintainer     40
            #   Owner          50

            ownersOrMaintainers = []
            for member in members:
                if member.access_level >= 40:
                    ownersOrMaintainers.append(member)

            if len(ownersOrMaintainers) < totalMembers:
                return {True: 'Less owners/maintainers than members set'}

            return {False: 'Access levels not restrictive for members'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def domain_verification(glEntity, glObject, **kwargs):
    """
    id: 1.3.9
    title: Ensure an organization's identity is confirmed with a “Verified”
           badge
    """

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def scm_notification_restriction(glEntity, glObject, **kwargs):
    """
    id: 1.3.10
    title: Ensure Source Code Management (SCM) email notifications are
           restricted to verified domains
    """

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def org_provided_ssh_certs(glEntity, glObject, **kwargs):
    """
    id: 1.3.11
    title: Ensure an organization provides SSH certificates
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # available for all input types
    try:
        keyRestrictions = [
            'ed25519_key_restriction', 'ecdsa_key_restriction',
            'dsa_key_restriction', 'rsa_key_restriction',
            'ecdsa_sk_key_restriction', 'ed25519_sk_key_restriction'
        ]

        settings = glObject.settings.get()

        for restriction in keyRestrictions:

            if getattr(settings, restriction) != 0:
                return {True: f'{restriction} is enforced'}

        return {False: 'No key restrictions set'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def restrict_ip_addresses(glEntity, glObject, **kwargs):
    """
    id: 1.3.12
    title: Ensure Git access is limited based on IP addresses
    """

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def track_code_anomalies(glEntity, glObject, **kwargs):
    """
    id: 1.3.13
    title: Ensure anomalous code behavior is tracked
    """

    return {None: 'This check requires validation'}
