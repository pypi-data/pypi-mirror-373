import logging
import sys

class LogRedirector:
    """Redirects print statements to the logging system."""
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.activated = True

    def write(self, message):
        if message.strip() and self.activated:
            self.activated = False
            self.logger.log(self.level, message.strip())
            self.activated = True

    # Required for compatibility with sys.stdout
    def flush(self):
        pass