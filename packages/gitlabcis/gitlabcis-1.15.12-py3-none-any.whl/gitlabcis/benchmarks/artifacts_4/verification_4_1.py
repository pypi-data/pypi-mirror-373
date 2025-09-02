# -------------------------------------------------------------------------


def sign_artifacts_in_build_pipeline(glEntity, glObject, **kwargs):
    """
    id: 4.1.1
    title: Ensure all artifacts are signed by the build pipeline itself
    """

    import io
    import os
    import zipfile

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            Build_stage_jobs = []
            build_stage = False
            pipelines = glEntity.pipelines.list(get_all=False)

            if not pipelines:
                return {False: 'No pipelines found'}

            latestPipeline = pipelines[0]
            jobs = latestPipeline.jobs.list(get_all=True)
            build_stage = []

            for job in jobs:
                if job.stage == 'build':
                    build_stage = True
                    Build_stage_jobs.append(job)

            if not build_stage:
                return {False: 'No build stages available'}

            for job in Build_stage_jobs:
                job_info = glEntity.jobs.get(job.id)
                artifact = job_info.artifacts()
                byte_stream = io.BytesIO(artifact)

            with zipfile.ZipFile(byte_stream) as z:
                file_list = z.namelist()

            for file_name in file_list:
                base_name, extension = os.path.splitext(file_name)
                sig_file = f"{base_name}.sig"

                if sig_file not in file_list:
                    return {False: 'Artifacts are not being signed'}

            return {True: 'Artifacts are signed'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

            if e.response_code == 404:
                return {False: 'Artifacts are not being signed'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def encrypt_artifacts_before_distribution(glEntity, glObject, **kwargs):
    """
    id: 4.1.2
    title: Ensure artifacts are encrypted before distribution
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def only_authorized_platforms_can_decrypt_artifacts(
        glEntity, glObject, **kwargs):
    """
    id: 4.1.3
    title: Ensure only authorized platforms have decryption
           capabilities of artifacts
    """

    # We cannot automatically answer this check, therefore we SKIP:
    return {None: 'This check requires validation'}
