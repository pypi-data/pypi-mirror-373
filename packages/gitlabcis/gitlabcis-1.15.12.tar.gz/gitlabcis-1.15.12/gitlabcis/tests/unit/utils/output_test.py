# -----------------------------------------------------------------------------

from gitlabcis import output

# -----------------------------------------------------------------------------

stats = {
    'PASSED': 1,
    'FAILED': 1,
    'SKIPPED': 1,
    'TOTAL': 3
}

results = [
    {
        'id': '1.1.1',
        'title': 'Something',
        'reason': 'Yes',
        'result': 'PASS'
    },
    {
        'id': '1.1.2',
        'title': 'Something else',
        'reason': 'No',
        'result': 'FAIL'
    },
    {
        'id': '1.1.3',
        'title': 'Something even more else',
        'reason': 'No',
        'result': 'SKIP'
    }
]

# -----------------------------------------------------------------------------


def test_terminal_output():
    output(results, stats, 'terminal', None)

# -----------------------------------------------------------------------------


def test_xml_output():
    with open('results.xml', 'w') as f:
        output(results, stats, 'xml', f)

# -----------------------------------------------------------------------------


def test_json_output():
    with open('results.json', 'w') as f:
        output(results, stats, 'json', f)

# -----------------------------------------------------------------------------


def test_txt_output():
    with open('results.txt', 'w') as f:
        output(results, stats, 'txt', f)

# -----------------------------------------------------------------------------


def test_csv_output():
    with open('results.csv', 'w') as f:
        output(results, stats, 'csv', f)

# -----------------------------------------------------------------------------


def test_yaml_output():
    with open('results.yaml', 'w') as f:
        output(results, stats, 'yaml', f)

# -----------------------------------------------------------------------------


def test_no_results():
    stats = {"PASSED": 5, "TOTAL": 10, "SKIPPED": 10, "FAILED": 0}
    output([], stats, 'terminal', None)

# -----------------------------------------------------------------------------


def test_high_score_csv_results():
    stats = {"PASSED": 9001, "TOTAL": 9001, "SKIPPED": 0, "FAILED": 0}
    output([], stats, 'csv', None)

# -----------------------------------------------------------------------------


def test_zero_division_error():
    stats = {"PASSED": 10, "TOTAL": 10, "SKIPPED": 10, "FAILED": 1}
    output([], stats, 'csv', None)
