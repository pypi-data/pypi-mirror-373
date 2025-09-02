# -----------------------------------------------------------------------------

from unittest.mock import Mock

# -----------------------------------------------------------------------------


def test_log():

    from gitlabcis.cli import log

    token = 'a real token'
    logFilter = log.CustomLogFilter(token)
    mockLog = Mock()

    mockLog.getMessage.return_value = (
        'Connection pool is full, discarding connection')
    logFilter = log.CustomLogFilter(token)
    assert logFilter.filter(mockLog) is False

    mockLog.getMessage.return_value = f'oh look its my: {token}'
    logFilter = log.CustomLogFilter(token)
    assert logFilter.filter(mockLog) is True
