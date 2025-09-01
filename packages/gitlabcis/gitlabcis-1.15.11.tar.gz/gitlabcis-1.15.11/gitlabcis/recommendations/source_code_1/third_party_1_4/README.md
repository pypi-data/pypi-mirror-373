# 1.4 Third Party

This section consists of security recommendations for using third-party applications in the code repositories.

Applications are typically automated integrations that improve the workflow of an organization, for example, OAuth applications. Those applications are written by third-party developers and therefore should be reviewed carefully before use. It is important to monitor their use and permissions because unused applications or unnecessary high permissions can enlarge the attack surface.

## Recommendations

* [1.4.1 - admin_approval_for_app_installs.yml](./admin_approval_for_app_installs.yml)
* [1.4.2 - stale_app_reviews.yml](./stale_app_reviews.yml)
* [1.4.3 - least_privilge_app_permissions.yml](./least_privilge_app_permissions.yml)
* [1.4.4 - secure_webhooks.yml](./secure_webhooks.yml)
