# Security Policy

## Reporting a Vulnerability

Use [the Vulnerability Disclosure issue template](/.gitlab/issue_templates/vuln.md) to report a new security vulnerability.

New security issue should follow these guidelines when being created on `GitLab.com`:

- Create new issues as `confidential` if unsure whether issue a potential
vulnerability or not. It is easier to make an issue that should have been
public open than to remediate an issue that should have been confidential.
Consider adding the `/confidential` quick action to a project issue template.

- Always label as ``~security`` at a minimum. If you're reporting a vulnerability (or something you suspect may possibly be one) please use the [Vulnerability Disclosure](./gitlab/issue_templates/vuln.md) template while creating the issue. Otherwise, follow the steps here (with a security label).

- Add any additional labels you know apply. Additional labels will be applied
by the security team and other engineering personnel, but it will help with
the triage process:

  - [`~"type::bug"`, `~"type::maintenance"`, or `~"type::feature"` if appropriate](https://handbook.gitlab.com/handbook/security/product-security/application-security/vulnerability-management/#vulnerability-vs-feature-vs-bug)
  - `~dependency update` if issue is related to updating to newer versions of the dependencies GitLab requires.

Occasionally, data that should remain confidential, such as the private
project contents of a user that reported an issue, may get included in an
issue. If necessary, a sanitized issue may need to be created with more
general discussion and examples appropriate for public disclosure prior to
release.
