# -------------------------------------------------------------------------


def sign_artifacts(glEntity, glObject, **kwargs):
    """
    id: 2.4.1
    title: Ensure all artifacts on all releases are signed
    """

    # We cannot automatically answer this check, thereforewe  SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def lock_dependencies(glEntity, glObject, **kwargs):
    """
    id: 2.4.2
    title: Ensure all external dependencies used in the build
           process are locked
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def validate_dependencies(glEntity, glObject, **kwargs):
    """
    id: 2.4.3
    title: Ensure dependencies are validated before being used
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            return ci.searchConfig(
                glEntity, glObject, 'dependency-scanning')

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def create_reproducible_artifacts(glEntity, glObject, **kwargs):
    """
    id: 2.4.4
    title: Ensure the build pipeline creates reproducible artifacts
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
            if gitlab_ci_yml_dict is None:
                return {False: 'gitlab_ci_yml file not found'}
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
                        return {True: 'No built stage detected'
                                ' in gitlab_ci_yml'}
                    for job_name in build_jobs:
                        job = gitlab_ci_yml_dict[job_name]
                        if 'artifacts' in job:
                            continue
                        else:
                            return {False: 'No artifacts found for a '
                                    'job in the build stage'}
                else:
                    return {True: 'No stages detected in gitlab_ci_yml'}
                return {True: 'Build pipeline creates reproducible artifacts'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def pipeline_produces_sbom(glEntity, glObject, **kwargs):
    """
    id: 2.4.5
    title: Ensure pipeline steps produce a Software Bill of Materials
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    from gitlabcis.utils import ci

    if kwargs.get('isProject'):
        try:
            _result = ci.searchConfig(
                glEntity, glObject, 'dependency-scanning')

            result, reason = _result.popitem()

            if result is True:
                return {True: 'dependency-scanning is enabled,'
                        ' review CycloneDX SBOMs which named '
                        'gl-sbom--.cdx.json, available as job '
                        'artifacts of the dependency scanning job.'}
            else:
                return {result: reason}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance') or kwargs.get('isGroup'):
        return {None: 'Not applicable at instance or group level'}

# -------------------------------------------------------------------------


def pipeline_sign_sbom(glEntity, glObject, **kwargs):
    """
    id: 2.4.6
    title: Ensure pipeline steps sign the Software Bill of
           Materials -(SBOM) produced
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
