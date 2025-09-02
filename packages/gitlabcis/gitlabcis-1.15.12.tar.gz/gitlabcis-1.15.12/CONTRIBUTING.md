## Developer Certificate of Origin

Contributions to this repository are subject to the [Developer Certificate of Origin](https://docs.gitlab.com/legal/developer_certificate_of_origin/#developer-certificate-of-origin-version-11). By submitting any contribution to this project, you agree to be bound by these terms and certify that your contributions meet the requirements specified therein.

## Contributing

Thanks for considering to contribute to the GitLab CIS Scanner project (gitlabcis). Contributions of all forms are always welcome!

## Git Commit Guidelines

This project uses commit messages to automatically determine the type of change.
Messages should adhere to the conventions of [Conventional Commits (v1.0.0-beta.2)](https://www.conventionalcommits.org/en/v1.0.0-beta.2/).

### Commit msg Syntax

```sh
<type>[optional scope]: <description>

[optional body]

[optional footer]
```

#### Examples

```sh
feat(auth): add login functionality  # Correct type, subject, within 72 characters

fix(api): Correct data parsing bug   # Correct type, subject, within 72 characters

docs(readme): update installation guide  # Correct type, subject, within 72 characters
```

## Reporting feature requests / bugs

Please [raise an issue](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/issues) for feature requests or bugs

## Setup Dev Environment

Check out [the docs](https://gitlab.com/gitlab-security-oss/cis/gitlabcis/-/blob/main/docs/readme.md?ref_type=heads#for-developers-install) on how to install the dependencies.

```sh
# obtain a copy of the repo
git clone git@gitlab.com:gitlab-security-oss/cis/gitlabcis.git
cd gitlabcis

# install the dependencies
make

# OR without `make`:
python3 -m pip install -q .
python3 -m pip install -q .\[test,build\]

# start working out of a feature branch
git checkout -b feat/idea
```

### Pre-commit hooks

We use pre-commit hooks to ensure that what's committed to the repository has already passed validation checks locally.

Review the `.pre-commit-config.yaml` to see what checks run.

### Run CLI live tests against the source code

When you make a change to the codebase in _your_ branch, run `make install` again, to recieve a _fresh_ copy of `gitlabcis` to run live tests against.

```sh
# gitlabcis should now be added to the PATH:
gitlabcis https://gitlab.example.com/path/to/project

# for CLI arg help see:
gitlabcis --help
```

## Running unit tests

To run all of the pytest tests:

```sh
# inside the gitlabcis dir run:
pytest -s -vv tests/

# or without debug in stdout:
pytest tests
```

## Contributing to the GitLab CIS Benchmark

If you would like to propose changes to our CIS Benchmark, please create an account on the [Workbench](https://workbench.cisecurity.org/) portal and submit your proposal for review. If changes are accepted, please feel free to open an issue or merge request to update the scanner.
