import enum
from contextlib import contextmanager

class Verbosity(enum.IntEnum):
    CRITICAL = 0
    ERROR = 1
    WARNING = 2
    INFO = 3
    DEBUG = 4

@contextmanager
def logger_config(verbosity: Verbosity):
    old_verbosity = logger.verbosity
    logger.set_verbosity(verbosity)
    yield
    logger.set_verbosity(old_verbosity)


class Logger:

    def __init__(self):
        self.verbosity = Verbosity.INFO

    def set_verbosity(self, verbosity):
        self.verbosity = verbosity

    def _log(self, level, message):
        lines = str(message).split('\n')
        print(f"[{level}] {lines[0]}")
        for line in lines[1:]:
            print(f"\t{line}")

    def info(self, message):
        if self.verbosity >= Verbosity.INFO:
            self._log("INFO", message)

    def debug(self, message, br = None):
        if self.verbosity >= Verbosity.DEBUG:
            if br: message = "{0} bytes: {1}".format(br.tell(), message)
            self._log("DEBUG", message)

    def warning(self, message):
        if self.verbosity >= Verbosity.WARNING:
            self._log("WARNING", message)

    def error(self, message):
        self._log("ERROR", message)

logger = Logger()
