# 2.1 Build Environment

This section consists of security recommendations for the build pipelines environment.

Build environment is everything related to the infrastructure of the organization's artifacts build - the orchestrator, the pipeline executer, where the build workers are running, while pipeline is a set of commands that runs in the build environment. Most of the build environment recommendations are relevant for self-hosted build platforms only. For example, instance of CircleCi that is self-hosted.

## Recommendations

* [2.1.1 - single_responsibility_pipeline.yml](./single_responsibility_pipeline.yml)
* [2.1.2 - immutable_pipeline_infrastructure.yml](./immutable_pipeline_infrastructure.yml)
* [2.1.3 - build_logging.yml](./build_logging.yml)
* [2.1.4 - build_automation.yml](./build_automation.yml)
* [2.1.5 - limit_build_access.yml](./limit_build_access.yml)
* [2.1.6 - authenticate_build_access.yml](./authenticate_build_access.yml)
* [2.1.7 - limit_build_secrets_scope.yml](./limit_build_secrets_scope.yml)
* [2.1.8 - vuln_scanning.yml](./vuln_scanning.yml)
* [2.1.9 - disable_build_tools_default_passwords.yml](./disable_build_tools_default_passwords.yml)
* [2.1.10 - secure_build_env_webhooks.yml](./secure_build_env_webhooks.yml)
* [2.1.11 - build_env_admins.yml](./build_env_admins.yml)
