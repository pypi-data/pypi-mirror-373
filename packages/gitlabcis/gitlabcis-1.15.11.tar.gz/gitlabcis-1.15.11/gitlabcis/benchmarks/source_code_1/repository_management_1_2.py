# -------------------------------------------------------------------------


def public_repos_have_security_file(glEntity, glObject, **kwargs):
    """
    id: 1.2.1
    title: Ensure all public repositories contain a SECURITY.md file
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        if kwargs.get('isProject'):
            # SKIP private repos:
            try:
                if glEntity.visibility == 'private':
                    return {None: 'Project is private'}
            except AttributeError:
                return {None: 'Insufficient permissions'}

            # PASS if the SECURITY.md file exists in the root dir of default
            # branch
            _rootFiles = glEntity.repository_tree(path='', get_all=True)

            for _file in _rootFiles:
                if _file.get('name').upper() == 'SECURITY.MD':
                    return {True: 'SECURITY.md file found'}

            return {False: 'No SECURITY.md file found'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for instances or groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def limit_repo_creations(glEntity, glObject, **kwargs):
    """
    id: 1.2.2
    title: Ensure repository creation is limited to specific members
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        if kwargs.get('isProject') or kwargs.get('isInstance'):

            settings = glObject.settings.get()

            if settings.signup_enabled is False:
                return {True: 'Public signup is disabled'}

            if settings.signup_enabled is True and \
                settings.require_admin_approval_after_user_signup is True and \
                    settings.email_confirmation_setting == 'hard':
                return {True: 'Requires approval after signup and email '
                        'confirmation setting is "hard"'}

            return {False: 'Either public signup enabled, admin approval '
                    'after signup not set or email confirmation is set '
                    'to "hard"'}

        if kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def limit_repo_deletions(glEntity, glObject, **kwargs):
    """
    id: 1.2.3
    title: Ensure repository deletion is limited to specific users
    """

    # attempting to paginate over 1,000 users in a project which
    # received their membership due to nested-group permissions...
    # results in a large wait-time for this function to run.
    # roughly it take 1.5 minutes for it to complete all of /gitlab-com.

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def limit_issue_deletions(glEntity, glObject, **kwargs):
    """
    id: 1.2.4
    title: Ensure issue deletion is limited to specific users
    """

    # attempting to paginate over 1,000 users in a project which
    # received their membership due to nested-group permissions...
    # results in a large wait-time for this function to run.
    # roughly it take 1.5 minutes for it to complete all of /gitlab-com.

    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def track_forks(glEntity, glObject, **kwargs):
    """
    id: 1.2.5
    title: Ensure all copies (forks) of code are tracked and accounted for
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject'):

            _forksFound = glEntity.forks.list(get_all=False)

            if not _forksFound:
                return {True: 'No forks found'}

            # we can't track and account for forks, so SKIP if forks found
            return {None: 'Cannot track and account for forks'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for instances or groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def track_project_visibility_status(glEntity, glObject, **kwargs):
    """
    id: 1.2.6
    title: Ensure all code projects are tracked for changes in visibility
           status
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def review_and_archive_stale_repos(glEntity, glObject, **kwargs):
    """
    id: 1.2.7
    title: Ensure inactive repositories are reviewed and archived
           periodically
    """

    from datetime import datetime, timezone

    from dateutil.parser import isoparse
    from dateutil.relativedelta import relativedelta
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        sixMonthsAgo = datetime.now(timezone.utc) - relativedelta(months=6)

        if kwargs.get('isProject'):

            lastActivity = isoparse(
                glEntity.last_activity_at).replace(tzinfo=timezone.utc)

            if lastActivity > sixMonthsAgo:
                return {True: 'Repository is active'}

            return {False: 'Repository is inactive'}

        elif kwargs.get('isInstance'):

            for project in glObject.projects.list(iterator=True):
                lastActivity = isoparse(
                    project.last_activity_at).replace(tzinfo=timezone.utc)

                # fail first as there may be many projects to iterate through
                if lastActivity < sixMonthsAgo:
                    return {
                        False: f'Repository: {project.path_with_namespace} is inactive'}  # noqa: E501

            return {True: 'All repositories are active'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
