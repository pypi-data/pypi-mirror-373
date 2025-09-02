# 2.2 Build Worker

This section consists of security recommendations for build workers management and use.

Build workers are often called Runners. They are the infrastructure on which the pipeline runs. Build workers are considered sensitive because usually they have access to multiple, if not all, software supply chain components. One worker can run code checkout with source code management access, run tests, and push to the registry which requires access to it. Also, some of the pipeline commands running in a build worker can be vulnerable to attack and enlarge the attack surface. Because of all of that, it is especially important to ensure that the build workers are protected.

## Recommendations

* [2.2.1 - single_use_workers.yml](./single_use_workers.yml)
* [2.2.2 - pass_worker_envs_and_commands.yml](./pass_worker_envs_and_commands.yml)
* [2.2.3 - segregate_worker_duties.yml](./segregate_worker_duties.yml)
* [2.2.4 - restrict_worker_connectivity.yml](./restrict_worker_connectivity.yml)
* [2.2.5 - worker_runtime_security.yml](./worker_runtime_security.yml)
* [2.2.6 - build_worker_vuln_scanning.yml](./build_worker_vuln_scanning.yml)
* [2.2.7 - store_worker_config.yml](./store_worker_config.yml)
* [2.2.8 - monitor_worker_resource_consumption.yml](./monitor_worker_resource_consumption.yml)
