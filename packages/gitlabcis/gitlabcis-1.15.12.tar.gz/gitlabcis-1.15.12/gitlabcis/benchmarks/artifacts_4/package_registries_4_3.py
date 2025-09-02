# -------------------------------------------------------------------------


def validate_signed_artifacts_on_upload(glEntity, glObject, **kwargs):
    """
    id: 4.3.1
    title: Ensure all signed artifacts are validated upon uploading the
           package registry
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            commits = glEntity.commits.list(all=True)
            for commit in commits:
                commit_id = commit.id
                commit_info = glEntity.commits.get(commit_id)
                if commit_info.status is None:
                    return {False: 'Commits are not signed'}
                if commit_info.status != 'verified':
                    return {False: 'There are unverified commits'}
            return {True: 'All commits are verified'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def all_artifact_versions_signed(glEntity, glObject, **kwargs):
    """
    id: 4.3.2
    title: Ensure all versions of an existing artifact have their
           signatures validated
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            commits = glEntity.commits.list(all=True)
            for commit in commits:
                commit_id = commit.id
                commit_info = glEntity.commits.get(commit_id)
                if commit_info.status is None:
                    return {False: 'Commits are not signed'}
                if commit_info.status != 'verified':
                    return {False: 'There are unverified commits'}
            return {True: 'All commits are verified'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def audit_package_registry_config(glEntity, glObject, **kwargs):
    """
    id: 4.3.3
    title: Ensure changes in package registry configuration are
           audited
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def secure_repo_webhooks(glEntity, glObject, **kwargs):
    """
    id: 4.3.4
    title: Ensure webhooks of the repository are secured
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject'):
            webhooks = glEntity.hooks.list(get_all=True)

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

        elif kwargs.get('isInstance'):
            webhooks = glObject.hooks.list(get_all=True)

        if not webhooks:
            return {True: 'No hooks found'}

        for webhook in webhooks:

            if (webhook.url.startswith('https://') and
                    webhook.enable_ssl_verification):
                continue

            elif webhook.url.startswith('https://'):
                return {False: f'{webhook.url}' + ' uses '
                        'HTTPS but SSL verification is disabled'}

            else:
                return {False: f'{webhook.url}' + ' is '
                        'insecure (not using HTTPS)'}

        return {True: 'All hooks are secure'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
