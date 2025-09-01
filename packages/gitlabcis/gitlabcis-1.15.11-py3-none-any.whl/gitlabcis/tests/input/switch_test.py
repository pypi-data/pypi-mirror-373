# -----------------------------------------------------------------------------


def test_enable_debug(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://gitlab.com/nmcd/pub', '--debug', '--format',
         'json', '--output', 'results.json', '--omit-skipped',
         '--remediations'])

    assert exitCode == 1


def test_enable_debug_with_logging(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://gitlab.com/nmcd/pub', '--debug', '--format',
         'json', '--output', 'results.json', '--omit-skipped', '-l'
         '--remediations'])

    assert exitCode == 1


def test_disable_debug(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://gitlab.com/nmcd/pub', '--format',
         'json', '--output', 'results.json', '--omit-skipped',
         '--remediations'])

    assert exitCode == 1
