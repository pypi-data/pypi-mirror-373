# -------------------------------------------------------------------------


def version_control(glEntity, glObject, **kwargs):
    """
    id: 1.1.1
    title: Ensure any changes to code are tracked in a version control
           platform
    """

    # previously we authenticated, so this defaults to PASS
    return {True: 'Using GitLab as version control'}

# -------------------------------------------------------------------------


def code_tracing(glEntity, glObject, **kwargs):
    """
    id: 1.1.2
    title: Ensure any change to code can be traced back to its associated
           task
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:

        # -----------------------------------------------------------------

        def _checkCrosslinks(entity):
            """
            Check related_issues in MR's for either project, group or
            instances
            """

            # this will only check the last 20 MR's:
            for mr in entity.mergerequests.list(get_all=False):

                try:
                    if mr.related_issues():
                        return {True: 'Recent merge requests are crosslinked '
                                'to issues'}

                # some MR's do not have this attr..
                except AttributeError:
                    continue

            return {False: 'Merge requests are not crosslinked to '
                    'issues'}

        # -----------------------------------------------------------------

        if kwargs.get('isGroup') or kwargs.get('isProject'):
            return _checkCrosslinks(glEntity)

        if kwargs.get('isInstance'):
            return _checkCrosslinks(glObject)

        return {False: 'Merge requests are not crosslinked to issues'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def code_approvals(glEntity, glObject, **kwargs):
    """
    id: 1.1.3
    title: Ensure any change to code receives approval of two strongly
           authenticated users
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject') or kwargs.get('isGroup'):

            if kwargs.get('isGroup'):
                _approvals = glEntity.approval_rules.list(get_all=True)

            elif kwargs.get('isProject'):
                _approvals = glEntity.approvalrules.list(get_all=True)

            for approval in _approvals:
                if approval.approvals_required >= 2:
                    return {True: '2 approvals are required for code changes'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        return {False: '2 approvals are required for code changes'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
        # approval_group_rules feature flag not enabled:
        if e.response_code == 404:
            return {None: 'Approvals not available'}

# -------------------------------------------------------------------------


def code_approval_dismissals(glEntity, glObject, **kwargs):
    """
    id: 1.1.4
    title: Ensure previous approvals are dismissed when updates are
           introduced to a code change proposal
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    try:
        if kwargs.get('isProject'):
            mrApprovalSettings = glEntity.approvals.get()

            if mrApprovalSettings.reset_approvals_on_push is True:
                return {True: 'Approvals reset on push'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

        return {False: 'Approvals not reset on push'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
        if e.response_code == 404:
            return {None: 'Approvals not available'}

# -------------------------------------------------------------------------


def code_dismissal_restrictions(glEntity, glObject, **kwargs):
    """
    id: 1.1.5
    title: Ensure there are restrictions on who can dismiss code change
           reviews
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    try:
        if kwargs.get('isProject'):

            if glEntity.protectedbranches.list(get_all=False):
                return {
                    True: 'Protected branches found, restrictions set on '
                    'who can dismiss code changes'}

            return {False: 'No restrictions on who can dismiss code '
                    'changes'}

        elif kwargs.get('isInstance'):
            return {None: 'Not applicable at instance level'}

        elif kwargs.get('isGroup'):
            return {None: 'Not yet implemented for groups'}

    except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
            GitlabListError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def code_owners(glEntity, glObject, **kwargs):
    """
    id: 1.1.6
    title: Ensure code owners are set for extra sensitive code or
           configuration
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # as per the docs, the CODEOWNERS file can live in multiple places:
    # https://docs.gitlab.com/ee/user/project/codeowners/

    if kwargs.get('isProject'):
        _dirPaths = ['', '.gitlab', 'docs']

        # if the CODEOWNERS file is present, pass the check:
        for dirPath in _dirPaths:

            # some repos may not have these paths, so exclude them:
            try:
                _files = glEntity.repository_tree(path=dirPath, get_all=True)

            except (GitlabHttpError, GitlabGetError,
                    GitlabAuthenticationError) as e:

                if e.response_code == 404:
                    continue

                if e.response_code in [401, 403]:
                    return {None: 'Insufficient permissions'}

                return {None: 'Unknown error'}

            for _file in _files:

                if _file.get('name') == 'CODEOWNERS':
                    return {True: 'CODEOWNERS file present'}

        return {False: 'CODEOWNERS file not present'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

# -------------------------------------------------------------------------


def code_changes_require_code_owners(glEntity, glObject, **kwargs):
    """
    id: 1.1.7
    title: Ensure code owner's review is required when a change affects
           owned code
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            defaultBranch = glEntity.protectedbranches.get(
                glEntity.default_branch)

            if defaultBranch is None:
                return {False: 'Default branch is not protected'}

            if defaultBranch.code_owner_approval_required is True:
                return {True: 'CODEOWNERS approval is required'}

            return {False: 'CODEOWNERS approval is not configured'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code == 403 and e.error_message == '403 Forbidden':
                return {None: 'Insufficient permissions'}

            if e.response_code == 404:
                return {False: 'Default branch is not protected'}
        except AttributeError:
            return {None: 'CODEOWNERS approval not available'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def stale_branch_reviews(glEntity, glObject, **kwargs):
    """
    id: 1.1.8
    title: Ensure inactive branches are periodically reviewed and removed
    """

    from datetime import datetime

    from dateutil.relativedelta import relativedelta
    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            _staleBranches = []

            for branch in glEntity.branches.list(get_all=True):
                _commitDate = datetime.strptime(
                            branch.commit.get('committed_date'),
                            '%Y-%m-%dT%H:%M:%S.%f%z'
                        ).replace(tzinfo=None)

                if relativedelta(datetime.now(), _commitDate).months > 3:
                    _staleBranches.append(branch.name)

            if len(_staleBranches) == 0:
                return {True: 'No stale branches found'}

            return {False: 'Found stale branches'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}

# -------------------------------------------------------------------------


def checks_pass_before_merging(glEntity, glObject, **kwargs):
    """
    id: 1.1.9
    title: Ensure all checks have passed before merging new code
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        # bool value if box is checked in Settings -> Merge Requests:
        try:
            _allowMerging = \
                glEntity.only_allow_merge_if_all_status_checks_passed

            if _allowMerging is True:
                return {True: 'All checks must pass before merging'}
            else:
                return {False: 'All checks do not need to pass before merging'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        # if a user is on a free tier plan, this attribute will not exist:
        except AttributeError:
            return {None: 'The project is not on an eligible plan'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}

# -------------------------------------------------------------------------


def branches_updated_before_merging(glEntity, glObject, **kwargs):
    """
    id: 1.1.10
    title: Ensure open Git branches are up to date before they can be
           merged into code base
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            if glEntity.merge_method in ['rebase_merge', 'ff']:
                return {True: 'Merge methods set'}

            return {False: 'Merge methods not set'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        # this throws an attr error if accessed anonymously (pytest no auth)
        except AttributeError:
            return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}

# -------------------------------------------------------------------------


def comments_resolved_before_merging(glEntity, glObject, **kwargs):
    """
    id: 1.1.11
    title: Ensure all open comments are resolved before allowing code
           change merging
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            # bool value if box is checked in Settings -> Merge Requests:
            try:
                _dR = glEntity.only_allow_merge_if_all_discussions_are_resolved
            # this throws an attr error if accessed anonymously
            # (pytest no auth)
            except AttributeError:
                return {None: 'Insufficient permissions'}

            if _dR is True:
                return {True: 'All comments must be resolved before merging'}

            elif _dR is False:
                return {
                    False: 'All comments do not need to be resolved before '
                    'merging'
                }

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def commits_must_be_signed_before_merging(glEntity, glObject, **kwargs):
    """
    id: 1.1.12
    title: Ensure verification of signed commits for new changes before
           merging
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject') or kwargs.get('isGroup'):
        try:
            pushRules = glEntity.pushrules.get()

            if pushRules.reject_unsigned_commits is True:
                return {True: 'Rejecting unsigned commits'}

            return {False: 'Unsigned commits are not rejected'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

            if e.response_code == 404:
                return {None: 'No push rules found, or feature not enabled'}

    elif kwargs.get('isInstance'):
        return {None: 'This check requires validation'}

# -------------------------------------------------------------------------


def linear_history_required(glEntity, glObject, **kwargs):
    """
    id: 1.1.13
    title: Ensure linear history is required
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            if glEntity.merge_method not in ['rebase_merge', 'merge']:
                return {True: 'Merge method set'}

            return {False: 'Merge method not set'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        # this throws an attr error if accessed anonymously (pytest no auth)
        except AttributeError:
            return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}

# -------------------------------------------------------------------------


def branch_protections_for_admins(glEntity, glObject, **kwargs):
    """
    id: 1.1.14
    title: Ensure branch protection rules are enforced for administrators
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    # supports all input types:
    try:
        settings = glObject.settings.get()

        if settings.group_owners_can_manage_default_branch_protection \
                is False:
            return {
                True: 'Group owners cannot manage default branch '
                'protection'}

        return {False: 'Group owners can manage default branch protection'}

    except (GitlabHttpError, GitlabGetError,
            GitlabAuthenticationError) as e:
        if e.response_code in [401, 403]:
            return {None: 'Insufficient permissions'}
    except AttributeError:
        return {None: 'Feature is not enabled'}

# -------------------------------------------------------------------------


def merging_restrictions(glEntity, glObject, **kwargs):
    """
    id: 1.1.15
    title: Ensure pushing or merging of new code is restricted to specific
           individuals or teams
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            protectedBranches = glEntity.protectedbranches.list(get_all=True)

            if len(protectedBranches) == 0:
                return {False: 'No protected branches found'}

            for branch in protectedBranches:

                if branch.allow_force_push is True:
                    return {False: 'Protected branches allow force push'}

            return {True: 'Protected branches do not allow force push'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        try:
            settings = glObject.settings.get()

            if settings.default_branch_protection_defaults.get(
                    'allow_force_push') is False:
                return {True: 'Force push is disabled at instance level'}
            else:
                return {False: 'Force push is not disabled at instance level'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def ensure_force_push_is_denied(glEntity, glObject, **kwargs):
    """
    id: 1.1.16
    title: Ensure force push code to branches is denied
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            defaultBranch = glEntity.protectedbranches.get(
                glEntity.default_branch)

            if defaultBranch is not None \
                    and defaultBranch.allow_force_push is False:
                return {
                    True: 'Default branch is protected and does not allow '
                    'force push'
                }

            return {False: 'Default branch is not protected or allows '
                    'force push'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            # if we don't have access, or the default branch is not protected:
            if e.response_code in [401, 403, 404]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        try:
            settings = glObject.settings.get()

            if settings.default_branch_protection_defaults.get(
                    'allow_force_push') is False:
                return {True: 'Force push is disabled at instance level'}
            else:
                return {False: 'Force push is not disabled at instance level'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def deny_branch_deletions(glEntity, glObject, **kwargs):
    """
    id: 1.1.17
    title: Ensure branch deletions are denied
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabListError)

    if kwargs.get('isProject'):
        try:
            protectedBranches = glEntity.protectedbranches.list(get_all=False)

            if len(protectedBranches) == 0:
                return {False: 'No protected branches found'}

            return {True: 'Protected branches found'}

        except (GitlabHttpError, GitlabGetError, GitlabAuthenticationError,
                GitlabListError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        try:
            settings = glObject.settings.get()

            # 2 = once a repo is created, the default branch is protected
            if settings.default_branch_protection == 2:
                return {
                    True: 'New repositories have a default protected branch'}
            else:
                return {False: 'New repositories do not have a default '
                        'protected branch'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isGroup'):
        return {None: 'Not yet implemented for groups'}

# -------------------------------------------------------------------------


def auto_risk_scan_merges(glEntity, glObject, **kwargs):
    """
    id: 1.1.18
    title: Ensure any merging of code is automatically scanned for risks
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)
    from gql import Client, gql
    from gql.transport.exceptions import (TransportAlreadyConnected,
                                          TransportServerError)
    from gql.transport.requests import RequestsHTTPTransport
    from graphql import GraphQLError

    from gitlabcis.utils import ci

    if kwargs.get('isProject') or kwargs.get('isGroup'):
        try:

            variables = {
                'fullPath': glEntity.path_with_namespace
                if kwargs.get('isProject') else glEntity.full_path
            }

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

        client = Client(
            transport=RequestsHTTPTransport(
                url=kwargs.get('graphQLEndpoint'),
                headers=kwargs.get('graphQLHeaders'),
                use_json=True,
                verify=kwargs.get('sslVerify')
            ),
            fetch_schema_from_transport=True
        )

        query = gql('''
query GetSecurityScanners($fullPath: ID!) {
  project(fullPath: $fullPath) {
    scanExecutionPolicies {
      nodes {
        name
        enabled
        yaml
      }
    }
  }
  group(fullPath: $fullPath) {
    scanExecutionPolicies {
      nodes {
        name
        enabled
        yaml
      }
    }
  }
}
''')

        try:

            results = client.execute(query, variable_values=variables)

        except (GraphQLError, TransportServerError, TransportAlreadyConnected):
            return {None: 'Error: Issue with GraphQL Query'}

        # pytest no auth:
        except AttributeError:
            return {None: 'Insufficient permissions'}

        try:
            required_scans = [
                'dast', 'secret_detection', 'cluster_image_scanning',
                'container_scanning', 'sast', 'sast_iac', 'dependency_scanning'
            ]

            scans_found = set()
            secret_detection_policy_found = False

            if kwargs.get('isProject'):
                policies = results['project']['scanExecutionPolicies']['nodes']

            elif kwargs.get('isGroup'):
                policies = results['group']['scanExecutionPolicies']['nodes']

            for policy in policies:
                if policy.get('enabled') is True:
                    policy_yaml = ci.safeLoad(policy.get('yaml', ''))
                    actions = policy_yaml.get('actions', [])
                    rules = policy_yaml.get('rules', [])
                    for action in actions:
                        scans_found.add(action.get('scan'))
                        if action.get('scan') == 'secret_detection':
                            for rule in rules:
                                if (
                                    rule.get('type') == 'pipeline'
                                    and '*' in rule.get('branches', [])
                                ):
                                    secret_detection_policy_found = True
            missing_scans = [
                scan for scan in required_scans
                if scan not in scans_found
                ]
            if secret_detection_policy_found:
                if missing_scans:
                    return {
                        True: (
                            'Scan Execution Policy for secret_detection is '
                            'enabled and triggers for all pipelines and '
                            'branches. Other missing scans for manual review:'
                            f'{", ".join(missing_scans)}'
                        )
                    }
                else:
                    return {
                        True: (
                            'Scan Execution Policy for secret_detection is '
                            'enabled and triggers for all pipelines and '
                            'branches. All required scans are covered.'
                        )
                    }
            else:
                return {
                    False: (
                        'Scan Execution Policy for secret_detection '
                        'is not enabled to trigger for all pipelines '
                        'and branches. Other missing scans for manual '
                        f'review: {", ".join(missing_scans)}'
                    )
                }

        except KeyError:
            return {False: 'Scan Execution Policy was not found'}

    elif kwargs.get('isInstance'):
        return {None: 'Not applicable at instance level'}

# -------------------------------------------------------------------------


def audit_branch_protections(glEntity, glObject, **kwargs):
    """
    id: 1.1.19
    title: Ensure any changes to branch protection rules are audited
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError, GitlabLicenseError)

    # acceptable for all input types:
    try:
        if glObject.get_license().get('plan') in ['premium', 'ultimate']:
            return {True: 'License allows audit on branch protections'}

        return {False: 'License does not allow audit on branch '
                'protections'}

    except (GitlabHttpError, GitlabGetError, GitlabLicenseError,
            GitlabAuthenticationError) as e:
        if e.response_code in [401, 403, 404]:
            return {None: 'Insufficient permissions'}

# -------------------------------------------------------------------------


def default_branch_protected(glEntity, glObject, **kwargs):
    """
    id: 1.1.20
    title: Ensure branch protection is enforced on the default branch
    """

    from gitlab.exceptions import (GitlabAuthenticationError, GitlabGetError,
                                   GitlabHttpError)

    if kwargs.get('isProject'):
        try:
            defaultBranch = glEntity.branches.get(glEntity.default_branch)

            if defaultBranch.protected is True:
                return {True: 'Default branch is protected'}

            return {False: 'Default branch is not protected'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isInstance'):
        try:
            settings = glObject.settings.get()

            # 2 = once a repo is created, the default branch is protected
            if settings.default_branch_protection == 2:
                return {
                    True: 'New repositories have a default protected branch'}
            else:
                return {False: 'New repositories do not have a default '
                        'protected branch'}

        except (GitlabHttpError, GitlabGetError,
                GitlabAuthenticationError) as e:
            if e.response_code in [401, 403]:
                return {None: 'Insufficient permissions'}

    elif kwargs.get('isGroup'):
        return {None: 'Not applicable at group level'}
