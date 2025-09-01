# 2.4 Pipeline Integrity

This section consists of security recommendations for keeping pipeline integrity.

Integrity means ensuring that the pipelines, the dependencies they use, and their artifacts are all authentic and what they intended to be. Securing the pipeline integrity is to verify that every change and process running during the build pipeline run is what it is supposed to be. One way to do that for example is to lock each dependency to a certain secured version. It is important to insist on securing that because this is the way to set trust with the customer.

## Recommendations

* [2.4.1 - sign_artifacts.yml](./sign_artifacts.yml)
* [2.4.2 - lock_dependencies.yml](./lock_dependencies.yml)
* [2.4.3 - validate_dependencies.yml](./validate_dependencies.yml)
* [2.4.4 - create_reproducible_artifacts.yml](./create_reproducible_artifacts.yml)
* [2.4.5 - pipeline_produces_sbom.yml](./pipeline_produces_sbom.yml)
* [2.4.6 - pipeline_sign_sbom.yml](./pipeline_signs_sbom.yml)
