# 4.2 Access to Artifacts

This section consists of security recommendations for access management of artifacts.

Artifacts are often stored in registries, some external and some internal. Those registries have user entities that control access and permissions. Artifacts are considered sensitive, because they are being delivered to the costumer, and are prune to many attacks: data theft, dependency confusion, malicious packages and more. That's why their access management should be restrictive and careful.

## Recommendations

* [4.2.1 - limit_certifying_artifacts.yml](./limit_certifying_artifacts.yml)
* [4.2.2 - limit_artifact_uploaders.yml](./limit_artifact_uploaders.yml)
* [4.2.3 - require_mfa_to_package_registry.yml](./require_mfa_to_package_registry.yml)
* [4.2.4 - external_auth_server.yml](./external_auth_server.yml)
* [4.2.5 - restrict_anonymous_access.yml](./restrict_anonymous_access.yml)
* [4.2.6 - minimum_package_registry_admins.yml](./minimum_package_registry_admins.yml)
