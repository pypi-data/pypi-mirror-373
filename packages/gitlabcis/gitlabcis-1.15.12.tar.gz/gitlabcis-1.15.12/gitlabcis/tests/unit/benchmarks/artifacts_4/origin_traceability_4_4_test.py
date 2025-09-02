# -----------------------------------------------------------------------------

import pytest  # noqa: F401
from conftest import run

from gitlabcis.benchmarks.artifacts_4 import origin_traceability_4_4

# -----------------------------------------------------------------------------


def test_artifact_origin_info(glEntity, glObject):

    test = origin_traceability_4_4.artifact_origin_info

    run(glEntity, glObject, test, None)
