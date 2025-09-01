# -------------------------------------------------------------------------

def single_responsibility_pipeline(glEntity, glObject, **kwargs):
    """
    id: 2.1.1
    title: Ensure each pipeline has a single responsibility
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            pipelines = glEntity.pipelines.list(get_all=False)

            if not pipelines:
                return {True: 'No pipelines found'}

            latestPipeline = pipelines[0]
            jobs = latestPipeline.jobs.list(get_all=True)

            buildStages = set()
            multiBuildJobs = False

            for job in jobs:

                _stage = job.stage.lower()

                if 'build' in _stage:
                    if _stage in buildStages:
                        multiBuildJobs = True
                        break
                    buildStages.add(_stage)

            if len(buildStages) == 0:
                return {None: 'No build stage found'}

            # either there are multiple pipeline stages with "build" in
            # the name or there are multiple jobs in those stages
            if multiBuildJobs is True:
                return {False: 'Multi build stages or build jobs found'}

            # there's a single build stage, which has a single job:
            return {True: 'Build phase has a single responsibility'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [403, 401]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def immutable_pipeline_infrastructure(glEntity, glObject, **kwargs):
    """
    id: 2.1.2
    title: Ensure all aspects of the pipeline infrastructure and
           configuration are immutable
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def build_logging(glEntity, glObject, **kwargs):
    """
    id: 2.1.3
    title: Ensure the build environment is logged
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def build_automation(glEntity, glObject, **kwargs):
    """
    id: 2.1.4
    title: Ensure the creation of the build environment is automated
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
                return {True: 'The build environment creation is automated'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def limit_build_access(glEntity, glObject, **kwargs):
    """
    id: 2.1.5
    title: Ensure access to build environments is limited
    """
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject') or kwargs.get('isGroup'):
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

# -------------------------------------------------------------------------


def authenticate_build_access(glEntity, glObject, **kwargs):
    """
    id: 2.1.6
    title: Ensure users must authenticate to access the build
           environment
    """
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject') or kwargs.get('isGroup'):
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

# -------------------------------------------------------------------------


def limit_build_secrets_scope(glEntity, glObject, **kwargs):
    """
    id: 2.1.7
    title: Ensure build secrets are limited to the minimal necessary
           scope
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def vuln_scanning(glEntity, glObject, **kwargs):
    """
    id: 2.1.8
    title: Ensure the build infrastructure is automatically scanned for
           vulnerabilities
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation.'}

# -------------------------------------------------------------------------


def disable_build_tools_default_passwords(glEntity, glObject, **kwargs):
    """
    id: 2.1.9
    title: Ensure default passwords are not used
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation.'}

# -------------------------------------------------------------------------


def secure_build_env_webhooks(glEntity, glObject, **kwargs):
    """
    id: 2.1.10
    title: Ensure webhooks of the build environment are secured
    """
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject') or kwargs.get('isGroup'):
        try:
            webhooks = glEntity.hooks.list(get_all=True)
            if not webhooks:
                return {True: 'No webhooks found'}
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

            return {True: 'All webhooks are secure'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

# -------------------------------------------------------------------------


def build_env_admins(glEntity, glObject, **kwargs):
    """
    id: 2.1.11
    title: Ensure minimum number of administrators are set for the
           build environment
    """
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject') or kwargs.get('isGroup'):
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
                return {True: 'Build access is limited, less than 20% '
                        'of the members have Owner/Maintainer role'}
            else:
                return {False: 'Build access is not limited, over than 20% of '
                        'the members have Owner/Maintainer role'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}
