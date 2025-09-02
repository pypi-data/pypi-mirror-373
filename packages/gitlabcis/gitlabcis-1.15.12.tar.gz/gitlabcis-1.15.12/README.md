# CIS GitLab Benchmark Scanner - gitlabcis

## Background

On April 17th 2024, [GitLab™](https://about.gitlab.com/) published [a blog post](https://about.gitlab.com/blog/2024/04/17/gitlab-introduces-new-cis-benchmark-for-improved-security/) introducing its Center for Internet Security® (CIS) GitLab Benchmark. With the goal to improve the security of the product and offer hardening recommendations to GitLab's customers. You can download a copy of the benchmarks which are published on the [Center for Internet Security® website](https://workbench.cisecurity.org/benchmarks/17538).

> _"The CIS GitLab Benchmark stemmed from a collaboration between CIS and GitLab's Field Security and Product Management teams. After numerous conversations with customers, we understood the need for a specific benchmark that would guide their hardening efforts. We conducted an in-depth review of GitLab’s product and documentation to understand how our offering mapped to CIS's Software Supply Chain Security Benchmark. After the initial draft was ready, it entered into the CIS consensus process, where the broader CIS Benchmark Community was able to review it and suggest edits prior to publication."_
>
> _Ref: [Creating the CIS GitLab Benchmark](https://about.gitlab.com/blog/2024/04/17/gitlab-introduces-new-cis-benchmark-for-improved-security/#creating-the-cis-gitlab-benchmark)_

## Overview

`gitlabcis` is a [Python®](https://www.python.org/downloads/) package which audits a GitLab project against the [Center for Internet Security® (CIS) GitLab Benchmark](https://workbench.cisecurity.org/benchmarks/17538). It includes [recommendations-as-code](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/gitlabcis/recommendations?ref_type=heads#recommendations) formatted in [YAML™](https://yaml.org/).

## GitLab Product Enhancement

### Compliance Adherence Report

There is a larger effort to [add the CIS Benchmark](https://gitlab.com/groups/gitlab-org/-/epics/13823) as a compliance standard to the [Compliance Adherence Report](https://gitlab.com/groups/gitlab-org/-/epics/7854).

- Once implemented, this will enable customers to automatically have visibility into whether there are additional measures they need to take in order to comply with the measures recommended in the CIS Benchmark.

### Contributing back to GitLab

Through the course of developing this tool, the authors contributed 2 features to the GitLab product (#39):

- [Show Crosslinked/related issues in merge requests via the API](https://gitlab.com/gitlab-org/gitlab/-/issues/461536)
- [Groups API: Add Restrict group access by Domain](https://gitlab.com/gitlab-org/gitlab/-/issues/351494)

## Table of Contents

[[_TOC_]]

### Disclaimers

| Disclaimer | Comment |
| -----------| ------- |
| This tool assumes that one is using GitLab for [everything](https://about.gitlab.com/blog/2016/03/08/gitlab-tutorial-its-all-connected/) | <ul><li>For example, the first recommendation ([1.1.1 - version_control](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/gitlabcis/recommendations/source_code_1/code_changes_1_1/version_control.yml#L4)):</li><ul><li>_"Ensure any changes to code are tracked in a version control platform."_</ul><li>Using GitLab automatically passes this control.</li></ul> |
| This tool cannot audit every recommendation | <ul><li>We have kept a record of every recommendation that we cannot automate. Review our limitations doc ([docs/limitations.md](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/docs/limitations.md?ref_type=heads)), which highlights automation gaps in which a condition cannot confidently be automated.</li></ul> |
| This tool **does not execute any write operations** on your GitLab instance, group or project. No write actions are performed. | <ul><li>This tool is expressly designed to refrain from performing any write operations that may:</li><ul><li>modify, alter, change, or otherwise impact the configuration, data, or integrity of your GitLab project</li></ul> <li>ensuring that no alterations or unauthorized adjustments are made to its state or contents.</li></ul> |
| This is not an official GitLab product | <ul><li>This repository was created by GitLab engineers and is not officially supported by GitLab.</li></ul> |

### Getting started

- **Required:**
  - You need to have [python®](https://www.python.org/downloads/) & [pip](https://pip.pypa.io/en/stable/installation/) installed
  - **One of:**
    - GitLab [Personal Access Token (PAT)](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
    - GitLab [OAuth Token](https://docs.gitlab.com/ee/security/tokens/#oauth-20-tokens)

#### Tokens

`gitlabcis` **requires** one of the following tokens:

##### Personal Access Token (PAT)

- Create a [Personal Access Token (PAT)](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#create-a-personal-access-token).

You can either pass the token as an option or store it as an environment variable:

- `GITLAB_TOKEN` - (_optional_) Environment Variable
- `--token` / `-t` - (_optional_) gitlabcis token option

##### OAuth Token

- Create an [OAuth Token](https://docs.gitlab.com/ee/api/oauth2.html).

You can either pass the token as an option or store it as an environment variable:

- `GITLAB_OAUTH_TOKEN` - (_optional_) Environment Variable
- `--oauth-token` / `-ot` - (_optional_) gitlabcis token option

##### Token Scope

- **Required:** Your token needs to have _at least_ the `read_api` scope.
- (_optional_) Providing your token more scope will unlock more controls that require higher levels of permission.

#### Install

There's a number of ways to download the scanner. Please see them below:

##### Pypi

Install `gitlabcis` from pypi.org:

```sh
pip install gitlabcis
```

##### GitLab

Install `gitlabcis` from the [package registry](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/packages/):

```sh
pip install gitlabcis --index-url https://gitlab.com/api/v4/projects/57279821/packages/pypi/simple
```

If you haven't already done so, you will need to add the below to your `.pypirc` file.

```ini
[gitlab]
repository = https://gitlab.com/api/v4/projects/57279821/packages/pypi
username = __token__
password = <your personal access token>
```

Install `gitlabcis` from source via clone, or our [releases page](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/releases)

```sh
# make a clone (or create a local fork) of the repo
git clone git@gitlab.com:gitlab-security-oss/cis/gitlabcis.git
cd gitlabcis
make install
```

#### Usage

The following syntax is expected:

```sh
gitlabcis URL OPTIONS
```

#### Screenshot

![results](docs/img/results.png)

#### Generate a report

To generate a report from the shell:

```sh
gitlabcis https://gitlab.example.com/path/to/project --token $TOKEN
```

Generate a json report: (_Using the `$GITLAB_TOKEN` variable, you do not need to specify `--token` option_)

```sh
gitlabcis \
    https://gitlab.example.com/path/to/project \
    -o results.json \
    -f json
```

To execute a single control:

```sh
gitlabcis \
    https://gitlab.example.com/path/to/project \
    -ids 1.2.3 # or multiple: 2.3.4 3.4.5 etc
```

## Documentation

Review the `gitlabcis` [documentation (./docs)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/tree/main/docs?ref_type=heads) directory - _Something missing?_ Feel free to create contribute with a [new issue](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/issues/new).

## License

`gitlabcis` was published using the [MIT license](https://opensource.org/license/mit), it can be reviewed in the [./LICENSE](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/LICENSE?ref_type=heads) file.

## Changelog

See the [./CHANGELOG.md](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CHANGELOG.md?ref_type=heads) for more information.

## Developers

### Code of Conduct

Review the heading section of [contributing doc (CONTRIBUTING.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CONTRIBUTING.md?ref_type=heads) for the code of conduct.

### Security

Review our [security policy (docs/SECURITY.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/docs/SECURITY.md?ref_type=heads) document which outlines how to disclose a vulnerability.

### Contributing

Do you want to contribute? - Fantastic! Check out the [contributing doc (CONTRIBUTING.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CONTRIBUTING.md?ref_type=heads) for more information.
