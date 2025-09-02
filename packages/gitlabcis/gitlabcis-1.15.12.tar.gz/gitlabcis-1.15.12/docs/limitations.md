# Limitations

We cannot fully automate the audit of a control, as it's either not fully confident or simply unfeasible. Below is a list of all limitations within `gitlabcis`.

We are actively attempting to enhance GitLab by either developing features or providing ideas for features, see: #39+ for tracking.

## General

- The `gitlabcis` tool does support instances & groups but does not support all controls currently. This is on-going and can be tracked in: &2+
- When the `gitlabcis` tool audits a `project` it only look at the `project` level, not take into hierarchical settings or permissions.
  - i.e. If you selected "Require approval from CODEOWNERS" at a group level and _not_ at the project level, you would `FAIL` the [1.1.7 - code_changes_require_code_owners](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/gitlabcis/recommendations/source_code/code_changes/code_changes_require_code_owners.yml) control.
- For any controls that require _admin_ level permissions a `SKIP` will be returned if the token does not have sufficient permission.
  - This also includes any control that requires non-admin elevated permissions which the token used, does not have.

## Benchmark Controls

| id     | name | Limitation |
|--------|------|------------|
| 1.1.4 | code_approval_dismissals | For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [MR approval settings Group Level #3165](https://github.com/python-gitlab/python-gitlab/issues/3165)). |
| 1.1.5 | code_dismissal_restrictions | Trusted users cannot be automatically checked. The control will `PASS` for projects that have protected branches, and `FAIL` if none are set. For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Branches Group Level #3164](https://github.com/python-gitlab/python-gitlab/issues/3164)).|
| 1.1.7  | code_changes_require_code_owners | The recommendation is only set for the `default` branch. This function does not iterate over all protected branches. Additionally, if a user removes the protected status of their default branch, then creates a new protected branch. Only the protected branch is checked, skipping the default. For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Branches Group Level #3164](https://github.com/python-gitlab/python-gitlab/issues/3164)). |
| 1.1.11 | comments_resolved_before_merging | For `Group` input types, the following [feature request](https://gitlab.com/gitlab-org/gitlab/-/issues/534608) needs to be created, then an upstream change created in `python-gitlab` in order for us to assess this.|
| 1.1.12 | commits_must_be_signed_before_merging | This control will return a `SKIP` if the [push rules](https://docs.gitlab.com/api/group_push_rules/) feature is not enabled. |
| 1.1.14  | branch_protections_for_admins | Requires admin permissions to get a `PASS`/`FAIL` - additionally, gitlab.com `FAIL`'s this, because we allow group owners to manage default branch protections (by design). |
| 1.1.15  | merging_restrictions | This requires to iterate over every protected branch, which for large projects takes quite some time. We cannot distinguish between trusted & untrusted users, as the recommendation states these must be trusted users, this function does not `FAIL` based on this. For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Branches Group Level #3164](https://github.com/python-gitlab/python-gitlab/issues/3164)). |
| 1.1.16 | ensure_force_push_is_denied | For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Branches Group Level #3164](https://github.com/python-gitlab/python-gitlab/issues/3164)). |
| 1.1.17 | deny_branch_deletions | For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Branches Group Level #3164](https://github.com/python-gitlab/python-gitlab/issues/3164)). |
| 1.1.19 | audit_branch_protections | Ensuring that any changes to branch protections are audited requires reviewing logs generated on the instance. Enabling/disabling audit_events isn't toggle-able and if the automation could query the `protected_branch_updated` events, it still would not concretely answer if the events were audited. |
| 1.2.1 | public_repos_have_security_file | The control will `SKIP` if the repository is not public. If the `SECURITY.md` file does not exist in the root directory of the default branch in the repository, it will `FAIL`. |
| 1.2.3 | limit_repo_deletions | If a project that contains 1,000+ members as a result of nested-group permissions, this control will take a long time to finish. As such, it will return `SKIP` until a solution is found. |
| 1.2.4 | limit_issue_deletions | If a project that contains 1,000+ members as a result of nested-group permissions, this control will take a long time to finish. As such, it will return `SKIP` until a solution is found.|
| 1.2.5 | trace_forks | We can't account and trace forks programatically. This control will `SKIP` if forks are found, otherwise `PASS`. |
| 1.2.6 | track_project_visibility_status | `SKIP` by default as we cannot ascertain the relevant information programatically. |
| 1.3.1 | review_and_remove_inactive_users | Running this benchmark as a gitlab.com admin will take a considerable amount of time. |
| 1.3.3 | minimum_number_of_admins | Running this benchmark as a gitlab.com admin will take a considerable amount of time. |
| 1.3.6 | limit_user_registration_domain | `SKIP` by default as we cannot ascertain the relevant information programatically. |
| 1.3.8 | strict_permissions_for_repo | Running this benchmark as a gitlab.com admin will take a considerable amount of time. |
| 1.3.9 | domain_verification | `SKIP` by default as we cannot ascertain the relevant information programatically. |
| 1.3.10 | scm_notification_restriction | `SKIP` by default as we cannot ascertain the relevant information programatically. |
| 1.3.12 | restrict_ip_addresses | `SKIP` by default as the information is not returned by the API |
| 1.3.13 | track_code_anomalies | `SKIP` by default as it's not feasible to ascertain |
| 1.4.1 | admin_approval_for_app_installs | This control will _not_ review scopes on authorized applications, as this requires manual verification |
| 1.4.2 | stale_app_reviews | This control will look at the previous `20` pipeline jobs, and check for `dependency_scanning` in the name. This occurs when Dependency Scanning is enabled for a project, if found it will `PASS` else returns a `FAIL` |
| 1.4.3 | least_privilege_app_permissions | <ul><li>For `Instance` types, a `SKIP` will be presented.</li><li>For `Project` types, If a project has `integrations` then this check will `SKIP` to require manual verification, otherwise if none were found return a `PASS`</li></ul>|
| 1.5.1 | enable_secret_detection | `SKIP` by default for `Instance` types. |
| 1.5.2 | secure_pipeline_instructions | `SKIP` by default as we cannot automate this |
| 1.5.3 | secure_iac_instructions | `PASS` if SAST is enabled but does not specifically look for IaC SAST. |
| 1.5.7 | dast_web_scanning | `PASS` if DAST is enabled, but we cannot differentiate between API & WEB scanning. |
| 1.5.8 | dast_api_scanning | `PASS` if DAST is enabled, but we cannot differentiate between API & WEB scanning. |
| 2.1.1 | single_responsibility_pipeline | `FAIL` if there are multiple jobs under the "build" stages, also assumes that the build "phase" is under a stage with "build" in its name.|
| 2.1.2 | immutable_pipeline_infrastructure | `SKIP` by default as we cannot automate this |
| 2.1.3 | build_logging | `SKIP` by default as we cannot automate this |
| 2.1.4 | build_automation | `PASS` only if CI config file be available  |
| 2.1.5 | limit_build_access | `PASS` if the number of members with reporter role or higher is below 40% or fewer than three. |
| 2.1.6 | authenticate_build_access | `PASS` if the number of members with reporter role or higher is below 40% or fewer than three.|
| 2.1.7 | limit_build_secrets_scope | `SKIP` by default as we cannot automate this |
| 2.1.8 | vuln_scanning | `SKIP` by default as we cannot automate this |
| 2.1.9 | disable_build_tools_default_passwords | `SKIP` by default as we cannot automate this |
| 2.1.11| build_env_admins | `PASS` if the number of members with maintainer role or higher is below 20% or fewer than three. |
| 2.2.1 | single_use_workers | `SKIP` by default as we cannot automate this |
| 2.2.2 | pass_worker_envs_and_commands | `SKIP` by default as we cannot automate this |
| 2.2.4 | restrict_worker_connectivity | `SKIP` by default as we cannot automate this |
| 2.2.5 | worker_runtime_security | `SKIP` by default as we cannot automate this |
| 2.2.6 | build_worker_vuln_scanning | `SKIP` by default as we cannot automate this |
| 2.2.8 | monitor_worker_resource_consumption | `SKIP` by default as we cannot automate this |
| 2.3.3 | secure_pipeline_output | `SKIP` by default as we cannot automate this |
| 2.3.5 | limit_pipeline_triggers | `FAIL` if there is no protected branch otherwise `SKIP` as we cannot automate this. For `Group` input types, we require a change upstream on the `python-gitlab` dependency (ref: [Protected Environments Group Level #3168](https://github.com/python-gitlab/python-gitlab/issues/3168)). |
| 2.3.6 | pipeline_misconfiguration_scanning | `PASS` if SAST and DAST both are enabled|
| 2.3.7 | pipeline_vuln_scanning | `PASS` if SAST and DAST both are enabled|
| 2.4.1 | sign_artifacts | `SKIP` by default as we cannot automate this |
| 2.4.2 | lock_dependencies | `SKIP` by default as we cannot automate this |
| 2.4.5 | pipeline_produces_sbom | `PASS` if dependency-scanning is enabled however file name needs to be reviewed manually|
| 2.4.6 | pipeline_sign_sbom | `SKIP` by default as we cannot automate this |
| 3.1.1 | verify_artifacts | `SKIP` by default as we cannot automate this |
| 3.1.2 | third_party_sbom_required | `SKIP` by default as we cannot automate this |
| 3.1.3 | verify_signed_metadata | `SKIP` by default as we cannot automate this |
| 3.1.5 | define_package_managers | `SKIP` by default as we cannot automate this |
| 3.1.6 | dependency_sbom | `SKIP` by default as we cannot automate this |
| 3.1.7 | pin_dependency_version | `SKIP` by default as we cannot automate this |
| 3.1.8 | packages_over_60_days_old | `SKIP` by default as we cannot automate this |
| 3.2.4 | package_ownership_change | `SKIP` by default as we cannot ascertain the relevant information programatically. |
| 4.1.1 | sign_artifacts_in_build_pipeline | `PASS` if every file in artifacts.zip has a corresponding .sig file, indicating that the artifacts are signed |
| 4.1.2 | encrypt_artifacts_before_distribution | `SKIP` by default as we cannot automate this |
| 4.1.3 | only_authorized_platforms_can_decrypt_artifacts | `SKIP` by default as we cannot automate this |
| 4.2.1 | limit_certifying_artifacts | `SKIP` by default as we cannot automate this |
| 4.2.2 | limit_artifact_uploaders | `PASS` if the number of members with maintainer role or higher is below 20% or fewer than three.|
| 4.2.4 | external_auth_server | `SKIP` by default as we cannot automate this |
| 4.2.6 | minimum_package_registry_admins | `PASS` if the number of members with reporter role or higher is below 40% or fewer than three. |
| 4.3.3 | audit_package_registry_config | `SKIP` by default as we cannot automate this |
| 4.4.1 | artifact_origin_info | `SKIP` by default as we cannot automate this |
| 5.1.1 | separate_deployment_config | `PASS` if ci config yml file is available and not in the root directory of this project |
| 5.1.2 | audit_deployment_config | `PASS` if ci config yml file is available and changes need at least one approval and licence allow audit |
| 5.1.3 | secret_scan_deployment_config | `PASS` if secret_detection is enabled|
| 5.1.4 | limit_deployment_config_access | `SKIP` by default as we cannot automate this |
| 5.1.5 |  scan_iac| `PASS` if SAST_IAC is enabled|
| 5.1.6 | verify_deployment_config | `SKIP` by default as we cannot automate this |
| 5.1.7 | pin_deployment_config_manifests | `SKIP` by default as we cannot automate this |
| 5.2.1 | automate_deployment | `FAIL` if ci config file is not available otherwise `SKIP` for manual review |
| 5.2.2 | reproducible_deployment | `SKIP` by default as we cannot automate this |
| 5.2.3 | limit_prod_access | `SKIP` by default as we cannot automate this |
| 5.2.4 | disable_default_passwords | `SKIP` by default as we cannot automate this |
