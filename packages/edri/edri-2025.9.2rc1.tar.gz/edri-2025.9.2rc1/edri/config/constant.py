from enum import IntEnum, unique, auto

SWITCH_BYTES_LENGTH = 16  # Number of bytes in the switch identifier
SWITCH_MAX_SIZE = 0xFFFFFFFF  # Maximum value for a 32-bit unsigned integer
SWITCH_COMMANDS = (1 << SWITCH_BYTES_LENGTH * 8) - 1  # Total number of possible commands
SCHEDULER_TIMEOUT_MAX = 2_147_483  # Maximum timeout value for the scheduler, equivalent to INT_MAX without the last three digits
STREAM_CLOSE_MARK = "#&@"  # Marker used to indicate the end of a stream


@unique
class SwitchMessages(IntEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return last_values[-1] - count

    NEW_DEMANDS = SWITCH_COMMANDS
    LAST_MESSAGES = auto()


@unique
class ApiType(IntEnum):
    WS = 0
    REST = auto()
    HTML = auto()
