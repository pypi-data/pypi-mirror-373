# -----------------------------------------------------------------------------

from argparse import ArgumentParser, FileType

# -----------------------------------------------------------------------------
# Obtain input from the user:
# -----------------------------------------------------------------------------


def args(version, PROFILES, IMPLEMENTATION_GROUPS, OUTPUT_FORMATS,
         MAX_WORKERS):

    # -------------------------------------------------------------------------

    parser = ArgumentParser(
        description=f'GitLab CIS Benchmark Scanner Version: {version}\n'
    )

    # -------------------------------------------------------------------------

    # Add arguments
    parser.add_argument(
        'url',
        metavar='URL',
        nargs='*',
        type=str,
        help='The URL to the GitLab instance, group or project to audit'
    )

    parser.add_argument(
        '-t',
        '--token',
        dest='token',
        metavar='TOKEN',
        type=str,
        help='GitLab Personal Access Token'
    )

    parser.add_argument(
        '-ot',
        '--oauth-token',
        dest='oauth_token',
        metavar='OAUTH_TOKEN',
        type=str,
        help='GitLab OAUTH Token'
    )

    parser.add_argument(
        '-ci',
        '--cis-controls',
        dest='cis_controls',
        metavar='CIS_CONTROL_IDS',
        nargs='*',
        type=float,
        help='The IDs of the CIS Controls to check against (e.g. 18.1)'
    )

    parser.add_argument(
        '-ids',
        '--recommendation-ids',
        dest='recommendation_ids',
        metavar='RECOMMENDATION_IDS',
        nargs='*',
        type=str,
        help='The IDs of the recommendation checks to use (e.g. 1.1.1)'
    )

    parser.add_argument(
        '-s',
        '--skip',
        dest='skip_recommendation_ids',
        metavar='RECOMMENDATION_IDS_TO_SKIP',
        nargs='*',
        type=str,
        help='The IDs of the recommendation checks to SKIP (e.g. 1.1.1)'
    )

    parser.add_argument(
        '--no-ssl-verify',
        dest='no_ssl_verify',
        action='store_true',
        help='Disables SSL certificate verification (not recommended)'
    )

    parser.add_argument(
        '-p',
        '--profile',
        dest='profile',
        metavar='PROFILE',
        type=int,
        choices=PROFILES,
        help='Which benchmark profile to use (default: both 1 & 2)'
    )

    parser.add_argument(
        '-r',
        '--remediations',
        dest='remediations',
        action='store_true',
        help='Include remediations in the results output'
    )

    parser.add_argument(
        '-o',
        '--output',
        dest='output_file',
        metavar='OUTPUT_FILE',
        type=FileType('w', encoding='utf-8'),
        help='The name of the file to output results to'
    )

    parser.add_argument(
        '-g',
        '--implementation-groups',
        dest='implementation_groups',
        metavar='IMPLEMENTATION_GROUPS',
        nargs='*',
        type=str,
        choices=IMPLEMENTATION_GROUPS,
        help=f'Which CIS Implementation Group to use {IMPLEMENTATION_GROUPS} '
             '(default: all)'
    )

    parser.add_argument(
        '-os',
        '--omit-skipped',
        dest='omit_skipped',
        action='store_true',
        help='Excludes SKIP results from the output'
    )

    parser.add_argument(
        '-f',
        '--format',
        dest='output_format',
        default='terminal',
        type=str,
        choices=OUTPUT_FORMATS,
        help='Output format (default: terminal)'
    )

    parser.add_argument(
        '-mw',
        '--max-workers',
        dest='max_workers',
        default=MAX_WORKERS,
        type=int,
        help='Maximum number of Worker threads (default: {MAX_WORKERS})'
    )

    parser.add_argument(
        '-d',
        '--debug',
        dest='debug',
        action='store_true',
        help='Enable debugging mode'
    )

    parser.add_argument(
        '-l',
        '--log',
        nargs='?',
        dest='log',
        const='gitlabcis.log',
        default=None,
        type=str,
        help='Log file path (default: gitlabcis.log)'
    )

    parser.add_argument(
        '-v',
        '--version',
        dest='version',
        action='store_true',
        help='Print the currently installed version of gitlabcis'
    )

    # -------------------------------------------------------------------------

    # Parse arguments
    userArgs = parser.parse_args()

    # -------------------------------------------------------------------------

    if userArgs.version:
        print(f'gitlabcis version: {version}')
        exit(0)

    if not userArgs.url:
        parser.print_usage()
        exit(2)

    # -------------------------------------------------------------------------

    return userArgs
