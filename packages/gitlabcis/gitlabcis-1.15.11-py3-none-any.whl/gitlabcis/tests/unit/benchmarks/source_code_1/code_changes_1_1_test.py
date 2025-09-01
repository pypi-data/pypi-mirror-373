# -----------------------------------------------------------------------------

from unittest.mock import Mock

from conftest import run

from gitlabcis.benchmarks.source_code_1 import code_changes_1_1

# -----------------------------------------------------------------------------


def test_version_control(glEntity, glObject):

    test = code_changes_1_1.version_control

    run(glEntity, glObject, test, True)

# -----------------------------------------------------------------------------


def test_code_tracing(glEntity, glObject):
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.code_tracing

    run(glEntity, glObject, test, False, **{})

    kwarg = [
        {'isProject': True}, {'isGroup': True}, {'isInstance': True}]

    for kwargs in kwarg:

        glEntity.mergerequests.list.return_value = []
        glObject.mergerequests.list.return_value = []
        print('trying:', kwargs)
        run(glEntity, glObject, test, False, **kwargs)

        mr = Mock()
        del mr.related_issues
        glEntity.mergerequests.list.return_value = [mr]
        glObject.mergerequests.list.return_value = [mr]
        run(glEntity, glObject, test, False, **kwargs)

        issue = Mock()
        mr = Mock()
        mr.related_issues.return_value = [issue]
        glEntity.mergerequests.list.return_value = [mr]
        glObject.mergerequests.list.return_value = [mr]
        run(glEntity, glObject, test, True, **kwargs)

    glEntity.mergerequests.list.side_effect = GitlabHttpError(
        response_code=401)
    glObject.mergerequests.list.side_effect = GitlabHttpError(
        response_code=403)
    run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_code_approvals(glEntity, glObject):
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.code_approvals

    kwarg = [{'isGroup': True}, {'isProject': True}]
    for kwargs in kwarg:

        approvalRule = Mock()
        approvalRule.approvals_required = 2
        if kwargs.get('isProject'):
            glEntity.approvalrules.list.return_value = [approvalRule]
        if kwargs.get('isGroup'):
            glEntity.approval_rules.list.return_value = [approvalRule]
        run(glEntity, glObject, test, True, **kwargs)

        approvalRule.approvals_required = 1
        if kwargs.get('isProject'):
            glEntity.approvalrules.list.return_value = [approvalRule]
        if kwargs.get('isGroup'):
            glEntity.approval_rules.list.return_value = [approvalRule]
        run(glEntity, glObject, test, False, **kwargs)

        if kwargs.get('isProject'):
            glEntity.approvalrules.list.side_effect = GitlabHttpError(
                response_code=401)
        if kwargs.get('isGroup'):
            glEntity.approval_rules.list.side_effect = GitlabHttpError(
                response_code=401)
        run(glEntity, glObject, test, None, **kwargs)

        if kwargs.get('isProject'):
            glEntity.approvalrules.list.side_effect = GitlabHttpError(
                'Error', response_code=418)
        if kwargs.get('isGroup'):
            glEntity.approval_rules.list.side_effect = GitlabHttpError(
                'Error', response_code=418)
        assert test(glEntity, glObject, **kwargs) is None

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_code_approval_dismissals(glEntity, glObject):
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.code_approval_dismissals

    kwargs = {'isProject': True}

    mrApprovalSettings = Mock()
    mrApprovalSettings.reset_approvals_on_push = True
    glEntity.approvals.get.return_value = mrApprovalSettings
    run(glEntity, glObject, test, True, **kwargs)

    mrApprovalSettings.reset_approvals_on_push = False
    glEntity.approvals.get.return_value = mrApprovalSettings
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.approvals.get.side_effect = GitlabHttpError(
        response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.approvals.get.side_effect = GitlabHttpError(
        'Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_code_dismissal_restrictions(glEntity, glObject):
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.code_dismissal_restrictions

    kwargs = {'isProject': True}
    protectedBranches = Mock()
    branch = Mock()
    protectedBranches.list.return_value = [branch]
    glEntity.protectedbranches = protectedBranches
    run(glEntity, glObject, test, True, **kwargs)

    protectedBranches.list.return_value = []
    glEntity.protectedbranches = protectedBranches
    run(glEntity, glObject, test, False, **kwargs)

    protectedBranches.list.return_value = []
    glEntity.protectedbranches.list.side_effect = GitlabHttpError(
        response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.protectedbranches.list.side_effect = GitlabHttpError(
        'Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_code_owners(glEntity, glObject):
    from gitlab.exceptions import GitlabGetError, GitlabHttpError

    test = code_changes_1_1.code_owners

    kwargs = {'isProject': True}
    _files = Mock()
    _files = [{
        'name': 'CODEOWNERS'
    }]
    glEntity.repository_tree.return_value = _files
    run(glEntity, glObject, test, True, **kwargs)

    _files = [{
        'name': 'notfound'
    }]
    glEntity.repository_tree.return_value = _files
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.repository_tree.side_effect = GitlabHttpError(
        response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.repository_tree.side_effect = GitlabGetError(
        response_code=404)
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.repository_tree.side_effect = GitlabGetError(
        response_code=418)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.repository_tree.side_effect = GitlabHttpError(
        'Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) == {None: 'Unknown error'}

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_code_changes_require_code_owners(glEntity, glObject):
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.code_changes_require_code_owners

    kwargs = {'isProject': True}
    defaultBranch = Mock()
    defaultBranch.code_owner_approval_required = True
    glEntity.default_branch = defaultBranch
    glEntity.protectedbranches.get.return_value = defaultBranch
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.protectedbranches.get.return_value = None
    run(glEntity, glObject, test, False, **kwargs)

    defaultBranch.code_owner_approval_required = False
    glEntity.default_branch = defaultBranch
    glEntity.protectedbranches.get.return_value = defaultBranch
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.protectedbranches.get.side_effect = GitlabHttpError(
        response_code=403, error_message='403 Forbidden')
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.protectedbranches.get.side_effect = GitlabHttpError(
        response_code=404)
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.protectedbranches.get.side_effect = GitlabHttpError(
        'Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_stale_branch_reviews(glEntity, glObject):
    from datetime import datetime, timezone

    from dateutil.relativedelta import relativedelta
    from gitlab.exceptions import GitlabHttpError

    test = code_changes_1_1.stale_branch_reviews

    kwargs = {'isProject': True}
    branch = Mock()
    now = datetime.now(timezone.utc)
    nowts = f"{now.strftime('%Y-%m-%dT%H:%M:%S.%f%z')}"
    branch.commit = {"committed_date": nowts}
    branch.name = 'not-stale'
    glEntity.branches.list.return_value = [branch]
    run(glEntity, glObject, test, True, **kwargs)

    thendt = now - relativedelta(months=5)
    branch.commit = {
        'committed_date': thendt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')}
    branch.name = 'stale'
    glEntity.branches.list.return_value = [branch]
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.branches.list.side_effect = GitlabHttpError(
        response_code=401)
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.branches.list.side_effect = GitlabHttpError(
        'Error', response_code=418)
    assert test(glEntity, glObject, **kwargs) is None

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_checks_pass_before_merging(glEntity, glObject):
    # from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.checks_pass_before_merging

    kwargs = {'isProject': True}
    glEntity.only_allow_merge_if_all_status_checks_passed = True
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.only_allow_merge_if_all_status_checks_passed = False
    run(glEntity, glObject, test, False, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

    glEntity = Mock()
    run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_branches_updated_before_merging(glEntity, glObject):
    # from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.branches_updated_before_merging

    # unauthorised.merge_method.side_effect = GitlabGetError(response_code=401)
    # run(unauthorised, glObject, test, None)

    kwargs = {'isProject': True}
    del glEntity.merge_method
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.merge_method = 'ff'
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.merge_method = 'no'
    run(glEntity, glObject, test, False, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_comments_resolved_before_merging(glEntity, glObject):

    test = code_changes_1_1.comments_resolved_before_merging

    kwargs = {'isProject': True}
    del glEntity.only_allow_merge_if_all_discussions_are_resolved
    run(glEntity, glObject, test, None, **kwargs)

    glEntity.only_allow_merge_if_all_discussions_are_resolved = True
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.only_allow_merge_if_all_discussions_are_resolved = False
    run(glEntity, glObject, test, False, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_commits_must_be_signed_before_merging(glEntity, glObject):

    test = code_changes_1_1.commits_must_be_signed_before_merging

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:
        push = Mock()
        push.reject_unsigned_commits = True
        glEntity.pushrules.get.return_value = push
        run(glEntity, glObject, test, True, **kwargs)

        push.reject_unsigned_commits = False
        glEntity.pushrules.get.return_value = push
        run(glEntity, glObject, test, False, **kwargs)

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_linear_history_required(glEntity, glObject):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.linear_history_required

    kwargs = {'isProject': True}
    glEntity.merge_method = 'dont-merge'
    run(glEntity, glObject, test, True, **kwargs)

    glEntity.merge_method = 'merge'
    run(glEntity, glObject, test, False, **kwargs)

    mergeFail = Mock()
    del mergeFail.merge_method
    mergeFail.side_effect = GitlabGetError(
        response_code=401)
    run(mergeFail, glObject, test, None, **kwargs)

    mergeNone = Mock()
    del mergeNone.merge_method
    mergeNone.side_effect = AttributeError()
    run(mergeNone, glObject, test, None, **kwargs)

    kwarg = [{'isGroup': True}, {'isInstance': True}]
    for kwargs in kwarg:
        run(glEntity, glObject, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_branch_protections_for_admins(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.branch_protections_for_admins

    kwargs = {'isProject': True}
    settings = Mock()
    settings.group_owners_can_manage_default_branch_protection = False
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    settings.group_owners_can_manage_default_branch_protection = True
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.group_owners_can_manage_default_branch_protection.side_effect\
        = GitlabGetError(response_code=401)
    unauthorised.settings.get.side_effect = GitlabGetError(response_code=401)
    run(glEntity, unauthorised, test, None, **kwargs)

    unauthorised.group_owners_can_manage_default_branch_protection.side_effect\
        = GitlabGetError(response_code=418)
    unauthorised.settings.get.side_effect = GitlabGetError(response_code=418)
    assert test(glEntity, unauthorised, **kwargs) is None

    del glObject.group_owners_can_manage_default_branch_protection
    glObject.settings.get.side_effect = AttributeError()
    assert test(glEntity, glObject, **kwargs) == {
        None: 'Feature is not enabled'}

# -----------------------------------------------------------------------------


def test_merging_restrictions(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.merging_restrictions

    kwargs = {'isProject': True}
    glEntity.protectedbranches.list.return_value = []
    run(glEntity, glObject, test, False, **kwargs)

    branch = Mock()
    branch.allow_force_push = True
    protectedBranches = [branch]
    glEntity.protectedbranches.list.return_value = protectedBranches
    run(glEntity, glObject, test, False, **kwargs)

    branch.allow_force_push = False
    protectedBranches = [branch]
    glEntity.protectedbranches.list.return_value = protectedBranches
    run(glEntity, glObject, test, True, **kwargs)

    unauthorised.protectedbranches.list.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection_defaults =\
        {'allow_force_push': False}
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection_defaults =\
        {'allow_force_push': True}
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.settings.get.side_effect = \
        GitlabGetError(response_code=401)
    run(unauthorised, unauthorised, test, None, **{'isInstance': True})

    run(glEntity, glObject, test, None, **{'isGroup': True})

# -----------------------------------------------------------------------------


def test_ensure_force_push_is_denied(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.ensure_force_push_is_denied

    kwargs = {'isProject': True}
    glEntity.protectedbranches.get.return_value = None
    run(glEntity, glObject, test, False, **kwargs)

    branch = Mock()
    branch.allow_force_push = False
    glEntity.protectedbranches.get.return_value = branch
    run(glEntity, glObject, test, True, **kwargs)

    branch.side_effect = GitlabGetError(response_code=401)
    glEntity.protectedbranches.get.return_value = branch
    unauthorised.protectedbranches.get.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection_defaults =\
        {'allow_force_push': False}
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection_defaults =\
        {'allow_force_push': True}
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.settings.get.side_effect = \
        GitlabGetError(response_code=401)
    run(unauthorised, unauthorised, test, None, **{'isInstance': True})

    run(glEntity, glObject, test, None, **{'isGroup': True})

# -----------------------------------------------------------------------------


def test_deny_branch_deletions(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.deny_branch_deletions

    kwargs = {'isProject': True}
    glEntity.protectedbranches.list.return_value = []
    run(glEntity, glObject, test, False, **kwargs)

    glEntity.protectedbranches.list.return_value = ['main']
    run(glEntity, glObject, test, True, **kwargs)

    unauthorised.protectedbranches.list.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection = 2
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection = 1
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.settings.get.side_effect = \
        GitlabGetError(response_code=401)
    run(unauthorised, unauthorised, test, None, **{'isInstance': True})

    run(glEntity, glObject, test, None, **{'isGroup': True})

# -----------------------------------------------------------------------------


def test_auto_risk_scan_merges(glEntity, glObject, gqlClient):

    from gql.transport.exceptions import TransportServerError

    kwarg = [{'isGroup': True}, {'isProject': True}]

    for kwargs in kwarg:

        if kwargs.get('isProject'):
            glEntity.path_with_namespace = 'test/project'

        if kwargs.get('isGroup'):
            glEntity.full_path = 'test/group'

        kwargs = {
            'graphQLEndpoint': 'https://gitlab.com/api/graphql',
            'graphQLHeaders': {'Authorization': 'Bearer token'},
            'isProject': True
        }

        test = code_changes_1_1.auto_risk_scan_merges

        entityType = 'project' if kwargs.get('isProject') else 'group'

        gqlClient.return_value.execute.return_value = {entityType: {}}
        run(glEntity, glObject, test, False, **kwargs)

        mock_result = {
            entityType: {
                'scanExecutionPolicies': {
                    'nodes': [
                        {
                            'enabled': True,
                            'yaml': '''
                                actions:
                                - scan: secret_detection
                                - scan: dast
                                - scan: cluster_image_scanning
                                - scan: container_scanning
                                - scan: sast
                                - scan: sast_iac
                                - scan: dependency_scanning
                                rules:
                                - type: pipeline
                                  branches: ['*']
                            '''
                        }
                    ]
                }
            }
        }

        gqlClient.return_value.execute.return_value = mock_result
        run(glEntity, glObject, test, True, **kwargs)

        mock_result = {
            entityType: {
                'scanExecutionPolicies': {
                    'nodes': [
                        {
                            'enabled': True,
                            'yaml': '''
                                actions:
                                - scan: secret_detection
                                - scan: dast
                                rules:
                                - type: pipeline
                                  branches: ['*']
                            '''
                        }
                    ]
                }
            }
        }

        gqlClient.return_value.execute.return_value = mock_result
        run(glEntity, glObject, test, True, **kwargs)

        mock_result = {
            entityType: {
                'scanExecutionPolicies': {
                    'nodes': [
                        {
                            'enabled': True,
                            'yaml': '''
                                actions:
                                - scan: dast
                                rules:
                                - type: pipeline
                                  branches: ['*']
                            '''
                        }
                    ]
                }
            }
        }
        gqlClient.return_value.execute.return_value = mock_result
        run(glEntity, glObject, test, False, **kwargs)

    gqlClient.return_value.execute.side_effect = \
        TransportServerError("Error")
    run(glEntity, glObject, test, None, **{'isProject': True})

    run(glEntity, glObject, test, None, **{'isInstance': True})

# -----------------------------------------------------------------------------


def test_audit_branch_protections(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabAuthenticationError, GitlabGetError

    test = code_changes_1_1.audit_branch_protections

    kwargs = {'isProject': True}

    glObject.get_license.return_value = {'plan': 'premium'}
    run(glEntity, glObject, test, True, **kwargs)

    glObject.get_license.return_value = {'plan': 'free'}
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.get_license.side_effect = GitlabGetError(
        response_code=403)
    run(glEntity, unauthorised, test, None, **kwargs)

    unauthorised.get_license.side_effect = GitlabAuthenticationError(
        response_code=403
    )
    run(glEntity, unauthorised, test, None, **kwargs)

# -----------------------------------------------------------------------------


def test_default_branch_protected(glEntity, glObject, unauthorised):
    from gitlab.exceptions import GitlabGetError

    test = code_changes_1_1.default_branch_protected

    kwargs = {'isProject': True}
    branch = Mock()
    branch.protected = False
    glEntity.branches.get.return_value = branch
    run(glEntity, glObject, test, False, **kwargs)

    branch.protected = True
    glEntity.branches.get.return_value = branch
    run(glEntity, glObject, test, True, **kwargs)

    unauthorised.branches.get.side_effect \
        = GitlabGetError(response_code=401)
    run(unauthorised, glObject, test, None, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection = 2
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, True, **kwargs)

    kwargs = {'isInstance': True}
    settings = Mock()
    settings.default_branch_protection = 1
    glObject.settings.get.return_value = settings
    run(glEntity, glObject, test, False, **kwargs)

    unauthorised.settings.get.side_effect = \
        GitlabGetError(response_code=401)
    run(unauthorised, unauthorised, test, None, **{'isInstance': True})

    run(glEntity, glObject, test, None, **{'isGroup': True})
