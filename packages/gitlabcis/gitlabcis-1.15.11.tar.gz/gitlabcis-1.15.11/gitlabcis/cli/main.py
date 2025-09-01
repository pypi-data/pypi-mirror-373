# -----------------------------------------------------------------------------

import logging
import warnings
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from os import environ
from sys import exit

from tqdm import tqdm

from gitlabcis import (__version__, benchmarks, countRecommendations,
                       mapRecommendations, readRecommendations)
from gitlabcis.cli import argsInput, auth, log, output

# -----------------------------------------------------------------------------
# load all of the control functions:
# -----------------------------------------------------------------------------

benchmarkFunctions = [
    getattr(getattr(getattr(benchmarks, catFile), subCatFile), func)
    for catFile in dir(benchmarks)
    if not catFile.startswith('__')
    for subCatFile in dir(getattr(benchmarks, catFile))
    if not subCatFile.startswith('__')
    for func in dir(getattr(getattr(benchmarks, catFile), subCatFile))
    if not func.startswith('__')
]

# -----------------------------------------------------------------------------

PROFILES = [1, 2]
IMPLEMENTATION_GROUPS = ['IG1', 'IG2', 'IG3']
OUTPUT_FORMATS = ['terminal', 'yaml', 'json', 'csv', 'xml', 'txt']
MAX_WORKERS = 15

# -----------------------------------------------------------------------------
# Main:
# -----------------------------------------------------------------------------


def main():

    # -------------------------------------------------------------------------
    # Obtain Input:
    # -------------------------------------------------------------------------

    args = argsInput.args(__version__, PROFILES, IMPLEMENTATION_GROUPS,
                          OUTPUT_FORMATS, MAX_WORKERS)

    # -------------------------------------------------------------------------
    # Token heirarchy:
    # -------------------------------------------------------------------------

    # If a user provided a token via an arg, that should take highest priority,
    # next is the $GITLAB_TOKEN environment variable:

    token = None
    usingOauth = True if args.oauth_token else False

    for token in [args.token, args.oauth_token, environ.get('GITLAB_TOKEN')]:
        if token is not None:
            break

    if token is None:
        print(
            'Error: No token found, you must either have the environment '
            'variables: "GITLAB_TOKEN" / "GITLAB_OAUTH_TOKEN" or provide a '
            'token via the command line (--token/--oauth-token).'
        )
        exit(1)

    # -------------------------------------------------------------------------
    # Input sanity:
    # -------------------------------------------------------------------------

    if args.output_format.lower() != 'terminal' and args.output_file is None:
        print(
            'Error: Output format provided but no output file provided'
        )
        exit(1)

    if len(args.url) > 1:
        print('Error: Only one URL is currently supported')
        exit(1)
    else:
        args.url = args.url[0]

    # -------------------------------------------------------------------------
    # Logging:
    # -------------------------------------------------------------------------

    if args.debug is False:
        logLevel = 'INFO'
        logging.getLogger('gql.transport.requests').setLevel(logging.ERROR)
    else:
        logLevel = 'DEBUG'

    # base config
    log_config = {
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'level': getattr(logging, logLevel.upper())
    }

    # add file handler if log file is specified
    if args.log:
        log_config['filename'] = args.log
        log_config['filemode'] = 'a'  # append mode

    logging.basicConfig(**log_config)

    # Suppress tokens in logs & max pool size:
    logFilter = log.CustomLogFilter(token)
    logging.getLogger('urllib3.connectionpool').addFilter(logFilter)
    logging.getLogger().addFilter(logFilter)

    logging.debug(f'args: {args}')

    # suppress self-signed cert warnings in requests:
    if args.no_ssl_verify is True:
        ssl_verify = False
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        logging.warning('SSL certificate verification disabled')
    else:
        ssl_verify = True

    # -------------------------------------------------------------------------
    # Auth to GitLab:
    # -------------------------------------------------------------------------

    gl = auth.GitlabCIS(args.url, token, usingOauth, ssl_verify)

    # -------------------------------------------------------------------------

    # Load the filtered controls from user input:
    filteredRecommendations = readRecommendations(args)
    if len(filteredRecommendations) == 0:
        print('Error: No recommendations were found.')
        exit(1)

    # -------------------------------------------------------------------------

    # format the plan:
    _prof = args.profile if args.profile else ', '.join(
        str(p) for p in PROFILES)

    _ciCon = ', '.join(
        str(ci)
        for ci in args.cis_controls
        if args.cis_controls) if args.cis_controls else 'All applicable'

    _impl = ', '.join(
        args.implementation_groups
        if args.implementation_groups
        else IMPLEMENTATION_GROUPS)

    _start = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

    workers = args.max_workers if args.max_workers else MAX_WORKERS

    # -------------------------------------------------------------------------

    # determine benchmarks to exec:
    _filteredRecs = len(filteredRecommendations)
    if _filteredRecs == countRecommendations():
        _recs = len(benchmarkFunctions)
    else:
        _recs = _filteredRecs

    # Print the plan to the user:
    print(
        f'\nRunning CIS benchmark scanner: \n\n'
        f' - Scan Started: {_start}\n'
        f' - Host: {gl.userInputHost}\n'
        f' - {"Group" if gl.isGroup else "Project" if gl.isProject else "Instance"}: {gl.userInputPath}\n'  # noqa: E501
        f' - Output Format: {args.output_format}\n'
        f' - Output File: {args.output_file.name if args.output_file else "stdout"}\n'  # noqa: E501
        f' - Profile(s) applied: {_prof}\n'
        f' - CIS Controls: {_ciCon}\n'
        f' - Implementation Group(s): {_impl}\n'
        f' - Maximum worker threads: {workers}\n'
        f' - Benchmark controls: {_recs}\n\n'
    )

    # -------------------------------------------------------------------------
    # Map the benchmark controls:
    # -------------------------------------------------------------------------

    results = []
    stats = {
        'PASSED': 0,
        'FAILED': 0,
        'SKIPPED': 0,
        'TOTAL': _recs
    }

    mappedFuncs = mapRecommendations(
        benchmarkFunctions, filteredRecommendations)

    # -------------------------------------------------------------------------
    # Store benchmark results:
    # -------------------------------------------------------------------------

    Benchmark = namedtuple('Benchmark', ['projectCheck', 'result', 'func'])

    def executeBenchmark(_projectFunction, _projectCheck, glEntity, glObject,
                         **kwargs):
        """
        We need to set glEntity and glObject as their own vars as we cannot
        pass dot notation from the GitlabCIS cls obj

        Inputs:
            - _projectFunction: The actual func() to execute
            - _projectCheck: The yaml object of the recommendation
            - glEntity: The entity (group/project)
            - glObject: The gitlab authed object
            - kwargs: The extra attrs created from GitlabCIS cls obj
        """

        logging.debug(f'Executing benchmark: {_projectFunction.__name__}')

        return Benchmark(
            projectCheck=_projectCheck,
            result=_projectFunction(glEntity, glObject, **kwargs),
            func=_projectFunction)

    # -------------------------------------------------------------------------

    try:

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(
                    executeBenchmark, _projectFunction, _projectCheck,
                    gl.glEntity, gl.glObject, **gl.kwargs)
                for _projectFunction, _projectCheck in mappedFuncs.items()
            ]

            for future in tqdm(
                as_completed(futures),
                total=len(mappedFuncs),
                colour='green',
                desc='Scanning',
                bar_format=(
                    '{l_bar}{bar}| {n_fmt}/{total_fmt} completed '
                    '[elapsed: {elapsed} remaining: {remaining}]')):
                _res = future.result()

                try:
                    if next(iter(_res.result)) is True:
                        _resStr = 'PASS'
                        stats['PASSED'] += 1
                    elif next(iter(_res.result)) is False:
                        _resStr = 'FAIL'
                        stats['FAILED'] += 1
                    elif next(iter(_res.result)) is None:
                        _resStr = 'SKIP'
                        stats['SKIPPED'] += 1
                except TypeError:
                    logging.error(f'Function: {_res.func.__name__} did '
                                  'not return a dict')
                    exit(1)

                result = {
                    'id': _res.projectCheck['id'],
                    'title': _res.projectCheck['title'],
                    'reason': list(_res.result.values())[0],
                    'result': _resStr
                }

                if args.remediations is True:
                    result['remediation'] = _res.projectCheck['remediation']

                if args.omit_skipped is True \
                        and result.get('result') == 'SKIP':
                    continue

                results.append(result)

        output.output(results, stats, args.output_format, args.output_file)

    except KeyboardInterrupt:
        exit(1)

# -----------------------------------------------------------------------------


if __name__ == "__main__":
    main()
