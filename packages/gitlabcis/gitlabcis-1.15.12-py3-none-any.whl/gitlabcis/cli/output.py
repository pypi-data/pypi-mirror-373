# -----------------------------------------------------------------------------

import csv
import json
from datetime import datetime
from xml.etree import ElementTree as ET  # nosec: B405

import yaml
from defusedxml import ElementTree as DET
from tabulate import tabulate

# -----------------------------------------------------------------------------
# Output:
# -----------------------------------------------------------------------------


def output(results, stats, outputFormat='terminal', outputFile=None):
    """
    Desc: Output the results
    """

    # Terminal Icons:
    CHECK = '\u2714'
    CROSS = '\u2718'
    LINE = '\u0021'

    # Colours:
    GREEN = '\033[32m'
    RED = '\033[91m'
    BLUE = '\033[36m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    if results:

        _sortedResults = sorted(
            results,
            key=lambda col: [int(_id) for _id in col['id'].split('.')])

        # ---------------------------------------------------------------------
        # Terminal output:
        # ---------------------------------------------------------------------

        if outputFormat in ['terminal', 'txt']:

            if _sortedResults:
                _headers = _sortedResults[0].keys()
                _rows = [res.values() for res in _sortedResults]
            else:
                _headers = []
                _rows = []

            for result in _sortedResults:
                result['result'] = (
                    f'{GREEN}PASS {CHECK}{RESET}'
                    if result['result'] == 'PASS'
                    else f'{BLUE}SKIP {LINE}{RESET}'
                    if result['result'] == 'SKIP'
                    else f'{RED}FAIL {CROSS}{RESET}'
                )

            table = tabulate(
                _rows,
                headers=_headers,
                tablefmt='rounded_grid',
                maxcolwidths=[None, 75, 25, None])

            if outputFormat == 'terminal':
                print(f'\nResults:\n\n{table}')  # noqa: E231

            elif outputFormat == 'txt':
                outputFile.write(table)

        # ---------------------------------------------------------------------
        # JSON output:
        # ---------------------------------------------------------------------

        if outputFormat == 'json':

            json.dump(_sortedResults, outputFile, indent=4)

        # ---------------------------------------------------------------------
        # YAML output:
        # ---------------------------------------------------------------------

        if outputFormat == 'yaml':

            yaml.dump(_sortedResults, outputFile, indent=4)

        # ---------------------------------------------------------------------
        # XML output:
        # ---------------------------------------------------------------------

        if outputFormat == 'xml':

            root = ET.Element('root')

            for item in _sortedResults:

                sub_element = ET.SubElement(root, 'item')

                for key, value in item.items():
                    ET.SubElement(sub_element, key).text = str(value)

            outputFile.write(DET.tostring(root, encoding='utf-8').decode())

        # ---------------------------------------------------------------------
        # CSV output:
        # ---------------------------------------------------------------------

        if outputFormat == 'csv':

            if _sortedResults:
                _headers = _sortedResults[0].keys()
            else:
                _headers = []

            writer = csv.DictWriter(outputFile, fieldnames=_headers)

            writer.writeheader()

            for row in _sortedResults:
                writer.writerow(row)

    # -------------------------------------------------------------------------
    # Determine the score - output the stats:
    # -------------------------------------------------------------------------

    try:
        score = round(
            (stats["PASSED"] / (stats["TOTAL"] - stats["SKIPPED"])) * 100, 2)
    except ZeroDivisionError:
        # the total score matched the amount of skipped results
        score = 0

    if score >= 75:
        scoreColor = GREEN
    elif score >= 50 and score < 75:
        scoreColor = YELLOW
    else:
        scoreColor = RED

    print(
        '\nScan finished: '
        f'{datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")}\n\n'
        'Stats:\n\n'
        f' - {GREEN}PASSED: {stats["PASSED"]}/{stats["TOTAL"] - stats["SKIPPED"]}{RESET}\n'  # noqa: E501
        f' - {RED}FAILED: {stats["FAILED"]}/{stats["TOTAL"] - stats["SKIPPED"]}{RESET}\n'  # noqa: E501
        f' - {BLUE}SKIPPED: {stats["SKIPPED"]}/{stats["TOTAL"]}{RESET}\n'
        f' - SCORE: {scoreColor}{score}%{RESET} (excludes SKIPPED)\n'
    )
