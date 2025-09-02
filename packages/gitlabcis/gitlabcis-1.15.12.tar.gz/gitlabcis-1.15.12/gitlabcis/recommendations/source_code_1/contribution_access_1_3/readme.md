# 1.3 Contribution Access

This section consists of security recommendations for managing access to the application code. This includes managing both internal and external access, administrator accounts, permissions, identification methods, etc. Securing these items is important for software safety because every security constraint on access is an obstacle in the way of attacks.

This section differentiates between the common user account and an admin account. It is important to understand that due to the high permissions of the admin account, it should be used only for administrative work and not for everyday tasks.

## Recommendations

* [1.3.1 - review_and_remove_inactive_users.yml](./review_and_remove_inactive_users.yml)
* [1.3.2 - limit_top_level_group_creation.yml](./limit_top_level_group_creation.yml)
* [1.3.3 - minimum_number_of_admins.yml](./minimum_number_of_admins.yml)
* [1.3.4 - require_mfa_for_contributors.yml](./require_mfa_for_contributors.yml)
* [1.3.5 - require_mfa_at_org_level.yml](./require_mfa_at_org_level.yml)
* [1.3.6 - limit_user_registration_domain.yml](./limit_user_registration_domain.yml)
* [1.3.7 - ensure_2_admins_per_repo.yml](./ensure_2_admins_per_repo.yml)
* [1.3.8 - strict_permissions_for_repo.yml](./strict_permissions_for_repo.yml)
* [1.3.9 - domain_verification.yml](./domain_verification.yml)
* [1.3.10 - scm_notification_restriction.yml](./scm_notification_restriction.yml)
* [1.3.11 - org_provided_ssh_certs.yml](./org_provided_ssh_certs.yml)
* [1.3.12 - restrict_ip_addresses.yml](./restrict_ip_addresses.yml)
* [1.3.13 - track_code_anomalies.yml](./track_code_anomalies.yml)
