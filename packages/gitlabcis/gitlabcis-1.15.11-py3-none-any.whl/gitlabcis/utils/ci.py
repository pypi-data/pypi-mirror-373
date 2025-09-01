# -------------------------------------------------------------------------


def getConfig(glEntity, glObject, **kwargs):
    """
    This function attempts to obtain the .gitlab-ci.yml file.

    The filepath can be:
        - Remote: e.g. https://example.com/.gitlab-ci.yml
        - External: e.g. rel/path/.gitlab-ci.yml@my/project:refName
        - Local: e.g. custom/local/repo/path/.gitlab-ci.yml

    Ref: https://docs.gitlab.com/ee/ci/pipelines/settings.html#specify-a-custom-cicd-configuration-file  # noqa: E501

    Because remote links can potentially include any type of file, they are
    not supported.

    The function returns a dict in the similar manner as the benchmarks:

    Examples:
        - SKIP: {None: 'reason'}
        - FAIL: {False: 'reason'}
        - PASS: {ProjectFile, None}
    """

    import logging
    import re

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        # set the default path if one is not set:
        gitlabCiYamlPath = (
            str(glEntity.ci_config_path)
            if glEntity.ci_config_path != ''
            else '.gitlab-ci.yml'
        )

        # SKIP remote CI files:
        if '://' in gitlabCiYamlPath:
            return {None: f'Remote CI file: {gitlabCiYamlPath} not supported'}

        # handle different project locations:
        remote = re.match(
            r'(?P<filePath>.*)@(?P<namespace>.*):?(?P<refName>.*)',
            gitlabCiYamlPath)

        # define the location:
        if remote is not None:
            _tempEntity = glObject.projects.get(
                remote.group('namespace')
            )
            _tempRef = remote.group('refName')
            _tempPath = remote.group('filePath')
        else:
            _tempEntity = glEntity
            _tempRef = glEntity.default_branch
            _tempPath = gitlabCiYamlPath

        # obtain the CI config file:
        gitlabCiYaml = None
        try:
            gitlabCiYaml = _tempEntity.files.get(
                file_path=_tempPath,
                ref=_tempRef
            )
        except (GitlabHttpError, GitlabGetError) as e:
            if e.response_code == 404:
                logging.debug(f'No CI config file found at: {_tempPath}')
                return {False: f'Pipeline config file not found: {_tempPath}'}

        # return a dict with a ProjectFile class var as the key
        # to differentiate results or not:
        if gitlabCiYaml is not None:
            return {gitlabCiYaml: None}

        return {False: f'Pipeline config file not found: {_tempPath}'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError):
        return {None: 'Insufficient permissions'}

    # this is for pytest to run unauthed tests:
    except AttributeError:
        return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def searchConfig(glEntity, glObject, searchString, **kwargs):
    """
    This function allows to search for a string inside the .gitlab-ci.yml file

    It uses the above getConfig() function to obtain it, then checks the str
    based on its lowercase value.
    """

    import base64

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gitlab.v4.objects.files import ProjectFile

    try:
        # obtain the ci config file:
        gitlabCiYaml = getConfig(
            glEntity, glObject, **kwargs)

        # obtain the result:
        try:
            _result = next(iter(gitlabCiYaml))

        # a SKIP was identified:
        except TypeError:
            # ensure the reason is returned:
            return {None: gitlabCiYaml[None]}

        # ensure we actually found the file:
        if not isinstance(_result, ProjectFile):
            return {_result: gitlabCiYaml[_result]}

        yamlContents = base64.b64decode(
            _result.content).decode('utf-8')

        if searchString.lower() in yamlContents.lower():
            return {True: f'{searchString} was found in CI config file'}
        else:
            return {False: f'{searchString} was not found in CI config file'}  # noqa: E713, E501

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def safeLoad(ciConfigObject):
    """
    GitLab CI Config can contain !reference which PyYAML cannot parse using
    safe_load. This function allows to execute: yaml.safe_load(obj) whilst
    loading !reference tags
    """

    import logging

    import yaml

    class GitLabYamlLoader(yaml.SafeLoader):
        pass

    def _yaml_constructor(loader, node):
        return loader.construct_sequence(node)

    yaml.add_constructor('!reference', _yaml_constructor,
                         GitLabYamlLoader)

    try:
        # We exclude Bandit's yaml load, as we _are_ using the SafeLoader
        # but we're monkey patching it to allow !reference tags.
        # (nosec B506)
        return yaml.load(ciConfigObject, Loader=GitLabYamlLoader)  # nosec B506

    except yaml.constructor.ConstructorError:
        logging.error('Failed to load the CI config file')
        return {None: 'Could not load CI config file'}
