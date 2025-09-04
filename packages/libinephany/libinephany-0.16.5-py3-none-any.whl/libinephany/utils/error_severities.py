# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

import enum
from collections import defaultdict

# ======================================================================================================================
#
# SEVERITIES
#
# ======================================================================================================================


class ErrorSeverities(enum.Enum):

    CRITICAL = "critical"
    HIGH = "high"
    WARNING = "warning"
    INFO = "info"

    @classmethod
    def should_mention(cls, severity: enum.Enum) -> bool:
        """
        :param severity: Severity of the error being sent to slack.
        :return: Whether @channel should be mentioned in the message.
        """

        return severity is cls.CRITICAL or severity is cls.HIGH


SEVERITY_LEVELS = defaultdict(
    lambda: 4,
    {ErrorSeverities.CRITICAL: 0, ErrorSeverities.HIGH: 1, ErrorSeverities.WARNING: 2, ErrorSeverities.INFO: 3},
)
SEVERITY_EMOJIS = defaultdict(
    lambda: ":question:",
    {
        ErrorSeverities.CRITICAL: ":rotating_light:",
        ErrorSeverities.HIGH: ":exclamation:",
        ErrorSeverities.WARNING: ":warning:",
        ErrorSeverities.INFO: ":information_source:",
    },
)
