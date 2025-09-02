"""Module for basic logging setup.

Initializes a logger with console output enabled. Logs messages at INFO level and above.
Designed for command-line applications requiring simple console logging.
"""

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter())
logger.addHandler(console_handler)
