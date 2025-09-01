# Docs

[[_TOC_]]

## Download

To download the `gitlabcis` tool, you can either clone the repository or download the source via our releases page:

### Clone

```sh
git clone git@gitlab.com:gitlab-security-oss/cis/gitlabcis.git
```

### Releases

You can download a release from our [releases](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/releases) page.

### Install

There's a number of ways to download the scanner. Please see them below:

#### Pypi

Install `gitlabcis` from pypi.org:

```sh
pip install gitlabcis
```

#### GitLab

Install `gitlabcis` from the [package registry](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/packages):

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

Install `gitlabcis` from source via clone/fork, or our [releases page](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/releases)

```sh
git clone git@gitlab.com:gitlab-security-oss/cis/gitlabcis.git
cd gitlabcis
pip install .
```

### For Developers install

You need to have `python3`, `pip` & `GNU make` available.

```sh
# download gitlabcis via clone/fork
cd gitlabcis
make install
```

Or without `GNU make`:

```sh
# inside the gitlabcis dir run:
python3 -m pip install -q .
python3 -m pip install -q .\[test,build\]
```

### Verify installation

You should now be able to run the following:

```sh
gitlabcis --help
```

## CIS GitLab Benchmark Explained

The follow section was taken from the published benchmark.

### Overview

All CIS Benchmarks focus on technical configuration settings used to maintain and/or increase the security of the addressed technology, and they should be used in conjunction with other essential cyber hygiene tasks like:

* Monitoring the base operating system for vulnerabilities and quickly updating with the latest security patches
* Monitoring applications and libraries for vulnerabilities and quickly updating with the latest security patches

In the end, the CIS Benchmarks are designed as a key component of a comprehensive cybersecurity program.

This document provides prescriptive guidance for establishing a secure configuration posture for securing the Software Supply Chain. To obtain the latest version of this guide, please visit [www.cisecurity.org](www.cisecurity.org). If you have questions, comments, or have identified ways to improve this guide, please write to us at [support@cisecurity.org](mailto:support@cisecurity.org).

**Special Note**: The set of configuration files mentioned anywhere throughout this benchmark document may vary according to the deployment tool and the platform. Any reference to a configuration file should be modified according to the actual configuration files used on the specific deployment.

### Intended Audience

This document is intended for DevOps and application security administrators, security specialists, auditors, help desk, and platform deployment personnel who plan to develop, deploy, assess, or secure solutions to build and deploy software updates through automated means of DevOps pipelines.

### Consensus Guidance

This CIS Benchmark was created using a consensus review process comprised of a global community of subject matter experts. The process combines real world experience with data-based information to create technology specific guidance to assist users to secure their environments. Consensus participants provide perspective from a diverse set of backgrounds including consulting, software development, audit and compliance, security research, operations, government, and legal. Each CIS Benchmark undergoes two phases of consensus review. The first phase occurs during initial Benchmark development. During this phase, subject matter experts convene to discuss, create, and test working drafts of the Benchmark. This discussion occurs until consensus has been reached on Benchmark recommendations. The second phase begins after the Benchmark has been published. During this phase, all feedback provided by the Internet community is reviewed by the consensus team for incorporation in the Benchmark. If you are interested in participating in the consensus process, please visit the [CIS Workbench](https://workbench.cisecurity.org/).

### Recommendation Definitions

The following defines the various components included in a CIS recommendation as applicable. If any of the components are not applicable it will be noted or the component will not be included in the recommendation.

#### Title

Concise description for the recommendation's intended configuration.

#### Assessment Status

An assessment status is included for every recommendation. The assessment status indicates whether the given recommendation can be automated or requires manual steps to implement. Both statuses are equally important and are determined and supported as defined below:

#### Automated

Represents recommendations for which assessment of a technical control can be fully automated and validated to a `pass`/`fail` state. Recommendations will include the necessary information to implement automation.

#### Manual

Represents recommendations for which assessment of a technical control cannot be fully automated and requires all or some manual steps to validate that the configured state is set as expected. The expected state can vary depending on the environment.

#### Profile

A collection of recommendations for securing a technology or a supporting platform. Most benchmarks include at least a Level 1 and Level 2 Profile. Level 2 extends Level 1 recommendations and is not a standalone profile. The Profile Definitions section in the benchmark provides the definitions as they pertain to the recommendations included for the technology.

#### Description

Detailed information pertaining to the setting with which the recommendation is concerned. In some cases, the description will include the recommended value. Rationale Statement Detailed reasoning for the recommendation to provide the user a clear and concise understanding on the importance of the recommendation.

#### Impact Statement

Any security, functionality, or operational consequences that can result from following the recommendation.

#### Audit Procedure

Systematic instructions for determining if the target system complies with the recommendation.

#### Remediation Procedure

Systematic instructions for applying recommendations to the target system to bring it into compliance according to the recommendation.

#### Default Value

Default value for the given setting in this recommendation, if known. If not known, either not configured or not defined will be applied.

#### References

Additional documentation relative to the recommendation.

#### CIS Critical Security Controls® (CIS Controls®)

The mapping between a recommendation and the CIS Controls is organized by CIS Controls version, Safeguard, and Implementation Group (IG). The Benchmark in its entirety addresses the CIS Controls safeguards of (v7) “5.1 - Establish Secure Configurations” and (v8) '4.1 - Establish and Maintain a Secure Configuration Process” so individual recommendations will not be mapped to these safeguards.

#### Additional Information

Supplementary information that does not correspond to any other field but may be useful to the user.

### Profile Definitions

The following configuration profiles are defined by this Benchmark:

#### Level 1

Items in this profile intend to:

* be practical and prudent;
* provide a clear security benefit; and
* not inhibit the utility of the technology beyond acceptable means.

#### Level 2

This profile extends the "Level 1 - Domain Controller" profile. Items in this profile exhibit one or more of the following characteristics:

* are intended for environments or use cases where security is paramount
* acts as defense in depth measure
* may negatively inhibit the utility or performance of the technology

### Acknowledgements

This Benchmark exemplifies the great things a community of users, vendors, and
subject matter experts can accomplish through consensus collaboration. The CIS
community thanks the entire consensus team with special recognition to the following
individuals who contributed greatly to the creation of this guide:
This benchmark exemplifies the great things a community of users, vendors, and
subject matter experts can accomplish through consensus collaboration. The CIS
community thanks to the entire consensus team with special recognition to the following
individuals who contributed greatly to the creation of this guide:

#### Authors

* Randall Mowen – Center for Internet Security
* Resheet Kosef – Aqua Security
* Eylam Milner – Aqua Security

#### Editors

* Sara Meadzinger – GitLab
* Ayoub Fandi – GitLab

#### Contributors

* Stuart Taylor
* Nikhil Verma
* James Scott
* Tony Wilwerding
* Matthew Reagan – Center for Internet Security
* Phil White – Center for Internet Security

#### Special Thanks to

* Greg Myers – GitLab
* Nick Malcolm – GitLab

And the entire GitLab team that contributed their knowledge and inputs to make the benchmark a reality.

## gitlabcis Usage

The following section covers how to use `gitlabcis` on the command line.

The format is as follows:

```sh
gitlabcis URL OPTIONS
```

### Arguments

This section covers all of the relevant command line arguments for `gitlabcis`

#### help

```sh
gitlabcis -h
gitlabcis --help
```

```sh
usage: gitlabcis [-h] [-t TOKEN] [-ot OAUTH_TOKEN] [-ci [CIS_CONTROL_IDS ...]] [-ids [RECOMMENDATION_IDS ...]] [-s [RECOMMENDATION_IDS_TO_SKIP ...]] [--no-ssl-verify] [-p PROFILE] [-r] [-o OUTPUT_FILE]
                 [-g [IMPLEMENTATION_GROUPS ...]] [-os] [-f {terminal,yaml,json,csv,xml,txt}] [-mw MAX_WORKERS] [-d] [-l [LOG]] [-v]
                 [URL ...]

GitLab CIS Benchmark Scanner Version: 1.11.2

positional arguments:
  URL                   The URL to the GitLab instance, group or project to audit

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        GitLab Personal Access Token
  -ot OAUTH_TOKEN, --oauth-token OAUTH_TOKEN
                        GitLab OAUTH Token
  -ci [CIS_CONTROL_IDS ...], --cis-controls [CIS_CONTROL_IDS ...]
                        The IDs of the CIS Controls to check against (e.g. 18.1)
  -ids [RECOMMENDATION_IDS ...], --recommendation-ids [RECOMMENDATION_IDS ...]
                        The IDs of the recommedation checks to use (e.g. 1.1.1)
  -s [RECOMMENDATION_IDS_TO_SKIP ...], --skip [RECOMMENDATION_IDS_TO_SKIP ...]
                        The IDs of the recommedation checks to SKIP (e.g. 1.1.1)
  --no-ssl-verify       Disables SSL certificate verification (not recommended)
  -p PROFILE, --profile PROFILE
                        Which benchmark profile to use (default: both 1 & 2)
  -r, --remediations    Include remediations in the results output
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        The name of the file to output results to
  -g [IMPLEMENTATION_GROUPS ...], --implementation-groups [IMPLEMENTATION_GROUPS ...]
                        Which CIS Implementation Group to use ['IG1', 'IG2', 'IG3'] (default: all)
  -os, --omit-skipped   Excludes SKIP results from the output
  -f {terminal,yaml,json,csv,xml,txt}, --format {terminal,yaml,json,csv,xml,txt}
                        Output format (default: terminal)
  -mw MAX_WORKERS, --max-workers MAX_WORKERS
                        Maximum number of Worker threads (default: {MAX_WORKERS})
  -d, --debug           Enable debugging mode
  -l [LOG], --log [LOG]
                        Log file path (default: gitlabcis.log)
  -v, --version         Print the currently installed version of gitlabcis
```

#### URL

The URL argument is positional, it does not have any argument flags. This should be the URL path to the GitLab instance, group or project you wish to scan:

```sh
# either of:
https://gitlab.example.com/path/to/project
https://gitlab.example.com/group
https://gitlab.example.com/
```

#### token

`gitlabcis` requires either a [Personal Access Token](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html) or an [OAuth Token](https://docs.gitlab.com/ee/security/tokens/#oauth-20-tokens).

##### Personal Access Token (PAT)

* This can be controlled by an environment variable: `GITLAB_TOKEN`
* Or passed in the command line argument options: `--token TOKEN` / `-t TOKEN`

##### OAuth Token

* This can be controlled by an environment variable: `GITLAB_OAUTH_TOKEN`
* Or passed in the command line argument options: `--oauth-token OAUTH_TOKEN` / `-ot TOKEN`

#### cis_control_ids

> "_Formerly the SANS Critical Security Controls (SANS Top 20) these are now officially called the CIS Critical Security Controls (CIS Controls)._"
>
> _Ref: [CIS Website](https://www.cisecurity.org/controls/cis-controls-list)_

Each control is a different category where controls can be stored.

To run the scanner against a particular control ID, use either of the following options:

```sh
-ci CONTROL_ID
--cis-controls CONTROL_ID
```

* By `default`, _all_ control ID's are included in the scan

#### recommendation_ids

To run the `gitlabcis` scanner against a particular recommendation control, use either of the following options:

```sh
-ids 1.1.1
--recommendation_ids 1.1.1
```

To use multiple id's, append them with a space:

```sh
-ids 1.1.1 2.2.2 3.3.3
```

* By `default` _all_ recommendations are included in scans, unless otherwise controlled with one of the other options

#### skip

To skip (not include in the results) particular recommendations, use either of the following options:

```sh
-s 1.1.1
--skip 1.1.1
```

To skip multiple id's, append them with a space:

```sh
--skip 1.1.1 2.2.2 3.3.3
```

* By `default` _all_ recommendations are included in scans, unless otherwise controlled with one of the other options

#### ssl_verify

You can optionally disable SSL certificate verification with the following option:

```sh
--no-ssl-verify
```

* By `default` this is set to `False`, meaning that we verify SSL certificates in both REST & GraphQL API calls.

#### profile

To run the scanner against a particular profile, (see Profile Definitions section above) use either of the following options:

* By `default` _both_ profiles are included in scans

```sh
-p PROFILE
--profile PROFILE
```

#### remediations

You may wish to include the `remediation` section of the recommendation YAML file in the output. Use either of the following options:

```sh
-r
--remediations
```

* By `default` remediation are _not_ included in the output

#### output

##### Format

* The following formats are accepted: json, xml, csv, yaml, terminal, txt

To control the output format, use either of the following options:

```sh
-f FORMAT
--format FORMAT
```

* By `default`, the `terminal` format is used (return results to stdout)

##### Output File

To set the filename where the results should be output use either of the following options:

```sh
-o FILENAME
--output FILENAME
```

* By `default`, there is _no output file_

#### max_workers

Pool of worker threads to execute tasks concurrently. Multi-threading is enabled by default.

To set the maximum number of worker threads, use either of the following options:

```sh
-mw WORKERS
--max-workers WORKERS
```

* By `default`, there are `15` max_worker threads

#### implementation_groups

> "_In an effort to assist enterprises of every size, IGs are divided into three groups. They are based on the risk profile and resources an enterprise has available to them to implement the CIS Controls._"
>
> _Ref: [CIS Website](https://www.cisecurity.org/controls/implementation-groups)_

To scan against a particular implementation group, use either of the following options:

```sh
-g GROUP_ID
--implementation-groups GROUP_ID
```

* By `default`, _all_ implementation groups are included in a scan.

#### Omit Skipped results

If you wish to exclude `SKIP` results from your output, use either of the following options:

```sh
-os
--omit-skipped
```

* By `default`, this is set to `False` (include skipped)

#### Debugging

To run the tool in debug mode (enable debug level logging) use eiher of the following options:

```sh
-d
--debug
```

* By `default`, this is set to `False` (do not display debug logs)

#### Logging

To output logs to a file, enable file logging mode, use eiher of the following options:

```sh
-l /path/to/gitlabcis.log
--log /path/to/gitlabcis.log
```

* By `default`, **if set** this is set to `./gitlabcis.log`, otherwise no log file is created.

#### Version

To determine what version you're using, run either of the following options:

```sh
-v
--version
```

* You can see what the latest version of the tool is by viewing our [releases page](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/releases)

### Proxy

Under the hood, `gitlabcis` uses [python-gitlab](https://github.com/python-gitlab/python-gitlab/tree/main). Please read their [documentation](https://python-gitlab.readthedocs.io/en/stable/api-usage-advanced.html#proxy-configuration) on setting environment variables to send requests through a proxy.

## gitlabcis Authors

| Author   | Affiliation |
| ------------- | -------------- |
| Nate Rosandich | GitLab |
| Neil McDonald | GitLab |
| Mitra JozeNazemian | GitLab |

## License

`gitlabcis` was published using the [MIT license](https://opensource.org/license/mit), it can be reviewed in the [./LICENSE](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/LICENSE?ref_type=heads) file.

## Changelog

See the [./CHANGELOG.md](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CHANGELOG.md?ref_type=heads) for more information.

## Developers

### Code of Conduct

Review the heading section of [contributing doc (CONTRIBUTING.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CONTRIBUTING.md?ref_type=heads) for the code of conduct.

### Security

Review our [security policy (SECURITY.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/SECURITY.md?ref_type=heads) document which outlines how to disclose a vulnerability.

### Contributing

Do you want to contribute? - Fantastic! Check out the [contributing doc (CONTRIBUTING.md)](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/CONTRIBUTING.md?ref_type=heads) for more information.
