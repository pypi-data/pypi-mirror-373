# -----------------------------------------------------------------------------

import logging

# -----------------------------------------------------------------------------


class CustomLogFilter(logging.Filter):

    # -------------------------------------------------------------------------

    def __init__(self, token):

        super().__init__()
        self.token = token

    # -------------------------------------------------------------------------

    def filter(self, record):

        # The connection is being discarded after the request is completed
        # we want to suppress this as it affects the cosmetics of the progress
        if ('Connection pool is full, discarding connection'
                in record.getMessage()):
            return False

        # Suppress any logs containing the token
        record.msg = record.getMessage().replace(self.token, '[REDACTED]')

        return True
