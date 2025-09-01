# -----------------------------------------------------------------------------

import pytest

# -----------------------------------------------------------------------------


def test_bad_file(capsys):

    with pytest.raises(SystemExit) as execCtx:
        from gitlabcis.utils import readYaml  # noqa: F401

        readYaml('non-existent.yml')

    assert execCtx.value.code == 1
