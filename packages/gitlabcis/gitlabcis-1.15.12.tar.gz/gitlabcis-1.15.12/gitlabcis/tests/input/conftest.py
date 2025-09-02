# -----------------------------------------------------------------------------

import sys

import pytest

# -----------------------------------------------------------------------------


@pytest.fixture
def cmdline(capsys, monkeypatch):
    def _cmdline(args):
        # Patch sys.argv with the provided args
        monkeypatch.setattr(sys, 'argv', args)

        try:
            with pytest.raises(SystemExit) as execCtx:
                from gitlabcis.__main__ import main  # noqa: F401
            # return an exit code:
            code = execCtx.value.code

        except pytest.fail.Exception:
            print('SystemExit was not raised')
            code = 0

        # return exec, capsys.readouterr()
        return code, capsys.readouterr()

    return _cmdline
