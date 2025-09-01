# 2.3 Pipeline Instructions

This section consists of security recommendations for pipeline instructions and commands.

Pipeline instructions are dedicated to taking raw files of source code and running a series of tasks on them to achieve some final artifact as output. They are most of the time written by third-party developers so they should be treated carefully and can also be vulnerable to attack in certain situations. Pipeline instructions files are considered very sensitive, and it is important to secure all their aspects - instructions, access, etc.

## Recommendations

* [2.3.1 - build_steps_as_code.yml](./build_steps_as_code.yml)
* [2.3.2 - build_stage_io.yml](./build_stage_io.yml)
* [2.3.3 - secure_pipeline_output.yml](./secure_pipeline_output.yml)
* [2.3.4 - track_pipeline_files.yml](./track_pipeline_files.yml)
* [2.3.5 - limit_pipeline_triggers.yml](./limit_pipeline_triggers.yml)
* [2.3.6 - pipeline_misconfiguration_scanning.yml](./pipeline_misconfiguration_scanning.yml)
* [2.3.7 - pipeline_vuln_scanning.yml](./pipeline_vuln_scanning.yml)
* [2.3.8 - pipeline_secret_scanning.yml](./pipeline_secret_scanning.yml)
