# -----------------------------------------------------------------------------

import re

# -----------------------------------------------------------------------------


def test_no_token_value(cmdline):

    for token in ['--token', '-t', '--oauth-token', '-ot']:
        exitCode, std = cmdline(
            ['gitlabcis', 'https://gitlab.com/nmcd/pub', token, ''])

        assert re.match(
            r'Error: The token provided failed to authenticate to*',
            str(std.out))

# -----------------------------------------------------------------------------


def test_no_url(cmdline):
    exitCode, std = cmdline(['gitlabcis', '--debug'])
    assert exitCode == 2

# -----------------------------------------------------------------------------


def test_dodgy_token_value(cmdline):
    for token in ['--token', '-t', '--oauth-token', '-ot']:
        exitCode, std = cmdline(
            ['gitlabcis', 'https://gitlab.com/nmcd/pub',
             token, 'this-aint-no-token'])

        assert re.match(
            r'Error: The token provided failed to authenticate to*',
            str(std.out))

# -----------------------------------------------------------------------------


def test_no_token_var(cmdline, monkeypatch):

    for var in ['GITLAB_TOKEN', 'GITLAB_OAUTH_TOKEN']:
        # temporarily remove the token from the environment
        monkeypatch.delenv(var, raising=False)

        exitCode, std = cmdline(
            ['gitlabcis', 'https://gitlab.com/nmcd/pub'])

        assert re.match(
            'Error: No token found, you must either have the environment '
            r'variable*',
            str(std.out))

# -----------------------------------------------------------------------------


def test_no_output_file(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://gitlab.com/nmcd/pub', '--token', 'fake-token',
         '--format', 'json'])

    assert ((exitCode == 1) or re.match(
        r'Error: Output format provided but no output file provided',
        str(std.out)))

# -----------------------------------------------------------------------------


def test_two_urls(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://gitlab.com/nmcd/pub',
         'https://gitlab.com/nmcd/pub', '--token', 'fake-token'])

    _err = str(std.out)
    assert (
        re.match(r'Error: No access token found', _err) or
        re.match(r'Error: Only one URL is currently supported', _err))

# -----------------------------------------------------------------------------


def test_fake_url(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://nmcd.gitlab.com/nmcd/pub'])

    assert exitCode == 1

# -----------------------------------------------------------------------------


def test_debug(cmdline):
    exitCode, std = cmdline(
        ['gitlabcis', 'https://nmcd.gitlab.com/nmcd/pub', '--token',
         'fake-token', '--debug'])

    assert exitCode == 1
