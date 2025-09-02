# -----------------------------------------------------------------------------

import logging
from sys import exit
from urllib.parse import urlparse

import gitlab

# -----------------------------------------------------------------------------


class GitlabCIS():

    # -------------------------------------------------------------------------

    def __init__(self, url, token, oauth=False, ssl_verify=True):
        """
        This class authenticates to GitLab and determines if the user provided
        a group, project or simply an instance. This is important as the
        control functions will need to know what they should be checking
        against.

        Inputs:
            - url: The URL to the GitLab instance, project or group
            - token: The GitLab token to authenticate with
            - oauth: True if the token is an OAuth token

        Outputs:
            - isGroup: True if the URL path is a group
            - isInstance: True if the URL path is an instance
            - isProject: True if the URL path is a project
            - isAdmin: True if the PAT has administrator privilege
            - isDotCom: True if the domain is gitlab.com
            - glObject: The main authenticated glObject
            - glEntity: Either the group / project object
            - graphQLEndpoint: The GraphQL API Endpoint
            - graphQLHeaders: The GraphQL HTTP Headers to connect with
            - pathStrs: List of path strings of a glEntity
            - pathObjs: List of path gitlab objects of a glEntity
        """

        # ---------------------------------------------------------------------

        self.url = url
        self.token = token
        self.oauth = oauth
        self.ssl_verify = ssl_verify

        self.isGroup = False
        self.isInstance = False
        self.isProject = False
        self.isAdmin = False
        self.isDotCom = False
        self.pathObjs = []
        self.paths = []

        self.glObject = None
        self.glEntity = None

        self.graphQLEndpoint = ''
        self.graphQLHeaders = ''

        # ---------------------------------------------------------------------

        # parse out the URL:
        urlParsedInput = urlparse(self.url)
        self.userInputPath = urlParsedInput.path.strip('/')
        self.userInputHost = \
            f'{urlParsedInput.scheme}://{urlParsedInput.netloc}'  # noqa: E231

        if urlParsedInput.netloc == 'gitlab.com':
            self.isDotCom = True
        logging.debug(f'{self.isDotCom=}')

        # setup graphQL:
        self.graphQLEndpoint = f'{self.userInputHost}/api/graphql'
        self.graphQLHeaders = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # attempt an authentication & decide on what we need to scan:
        self.authenticate()
        self.determineEntity()

        # determine what groups if any exist in hierarchy:
        self.cascade()

        # ---------------------------------------------------------------------
        # Set DotCom & Admin:
        # add a warning for gitlab.com admins:
        # ---------------------------------------------------------------------

        try:
            self.isAdmin = self.glObject.user.is_admin
            if self.isDotCom and self.isAdmin:

                user_input = input(
                    '\nWARNING: You are authenticated as a GitLab.com admin. '
                    'Running a "full scan" may create significant load.\n\n'
                    '  Do you wish to continue? (y/n): '
                ).lower()

                if user_input != 'y':
                    exit(0)

        # if gl.user.is_admin does not return a bool:
        except AttributeError:
            self.isAdmin = False
            pass

    # ---------------------------------------------------------------------
    # attempt a dry-run auth to make sure the token works:
    # ---------------------------------------------------------------------

    def authenticate(self):
        try:
            # instantiate the gl obj:
            self.glObject = gitlab.Gitlab(
                self.userInputHost,
                private_token=self.token if self.oauth is False else None,
                oauth_token=self.token if self.oauth is True else None,
                keep_base_url=True,
                ssl_verify=self.ssl_verify
            )
            self.glObject.auth()

        except gitlab.exceptions.GitlabAuthenticationError as e:
            print(
                'Error: The token provided '
                f'failed to authenticate to: {self.url}')
            logging.debug(f'Auth Error: {e}')
            exit(1)

        except (
            gitlab.exceptions.GitlabHttpError,
            gitlab.exceptions.GitlabGetError
                ) as e:

            logging.debug(f'Exception: {e}')

            if e.response_code == 403 \
                    and e.error_message == 'insufficient_scope':
                print('Error: The provided token has an insufficient scope.')
                exit(1)

            print(
                f'Error: The host: {self.userInputHost} does not appear '
                'to be a GitLab instance. If this is erroneous, please raise '
                'an issue.'
            )
            exit(1)

        except Exception as e:
            print(f'Error: Unable to connect to GitLab instance: {self.url}')
            logging.debug(f'Connection Error: {e}')
            exit(1)

        logging.debug(f'Successfully authenticated to: "{self.url}"')

    # ---------------------------------------------------------------------
    # Check if we are dealing with an instance, group or project:
    # ---------------------------------------------------------------------

    def determineEntity(self):

        # either the user provided a url to:
        # a group, an instance or a project

        if self.userInputPath != '':

            for getter, flag in [
                (self.glObject.projects.get, 'isProject'),
                    (self.glObject.groups.get, 'isGroup')]:

                try:
                    self.glEntity = getter(self.userInputPath)
                    setattr(self, flag, True)
                    logging.debug(f'{flag} - {self.url} found')
                    break
                except (gitlab.exceptions.GitlabGetError,
                        gitlab.exceptions.GitlabHttpError) as e:
                    if e.response_code == 404:
                        continue

            if self.glEntity is None:
                print(f'Error: "{self.userInputPath}" was not found.')
                exit(1)

        if self.isProject:
            self.paths = self.glEntity.namespace.get('full_path').split(
                '/')

        if self.isGroup:
            self.paths = self.glEntity.full_path.split('/')

        if self.isProject is False and self.isGroup is False:
            self.url = self.userInputHost
            logging.debug(f'Scanning instance: {self.url}')
            self.glEntity = self.url
            self.isInstance = True

    # ---------------------------------------------------------------------

    def cascade(self):
        """
        Determine the pathObjs of the glEntity path strings.
        Find the namespace, sub-groups, top-level group.
        """

        for _path in self.paths:

            for getter, _flag in [
                (self.glObject.namespaces.get, 'isNamespace'),
                    (self.glObject.groups.get, 'isGroup')]:

                try:
                    _namespaceObj = getter(_path)
                except (gitlab.exceptions.GitlabGetError,
                        gitlab.exceptions.GitlabHttpError) as e:
                    if e.response_code == 404:
                        continue

                self.pathObjs.append({
                    'objectType': _flag,
                    'object': _namespaceObj,
                    'path': _path
                })

    # ---------------------------------------------------------------------
    # Return an object of args to use inside the control functions:
    # ---------------------------------------------------------------------

    @property
    def kwargs(self):
        return {
            'isGroup': self.isGroup,
            'isInstance': self.isInstance,
            'isProject': self.isProject,
            'isAdmin': self.isAdmin,
            'isDotCom': self.isDotCom,
            'graphQLEndpoint': self.graphQLEndpoint,
            'graphQLHeaders': self.graphQLHeaders,
            'pathStrs': self.paths,
            'pathObjs': self.pathObjs,
            'sslVerify': self.ssl_verify
        }
