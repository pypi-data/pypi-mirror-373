# -----------------------------------------------------------------------------


def test_version(cmdline):
    exitCode, std = cmdline(['gitlabcis', '--version'])
    print(std.out)
    assert exitCode == 0
