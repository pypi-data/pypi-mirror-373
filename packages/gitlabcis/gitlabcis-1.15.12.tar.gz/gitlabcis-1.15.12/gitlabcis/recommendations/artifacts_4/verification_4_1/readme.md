# 4.1 Verification

This section consists of security recommendations for managing verification of artifacts.

When build artifacts are being pushed to the registry, a lot of different attacks can happen: a malicious artifact with the same name can be pushed, the artifact can be stolen over the network or if the registry is hacked, etc. It is important to secure artifacts by ensuring various verification methods, listed in the recommendations in this section, are available.

## Recommendations

* [4.1.1 - sign_artifacts_in_build_pipeline.yml](./sign_artifacts_in_build_pipeline.yml)
* [4.1.2 - encrypt_artifacts_before_distribution.yml](./encrypt_artifacts_before_distribution.yml)
* [4.1.3 - only_authorized_platforms_can_decrypt_artifacts.yml](./only_authorized_platforms_can_decrypt_artifacts.yml)
