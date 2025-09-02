import logging
import sys

from rich import traceback
from rich.console import Console
from rich.logging import RichHandler

# Colorful logging
# https://rich.readthedocs.io/en/latest/logging.html
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=Console(file=sys.stderr))],
)

# Add colorful tracebacks to crash with elegance
# https://rich.readthedocs.io/en/latest/traceback.html
traceback.install()

# Silence pagination logger
logging.getLogger("arkindex.pagination").setLevel(logging.WARNING)


def enable_verbose_mode():
    # Restore pagination logger
    logging.getLogger("arkindex.pagination").setLevel(logging.INFO)

    logger = logging.getLogger(__name__)
    for logger_name in logging.root.manager.loggerDict:
        if logger_name.startswith(logger.name):
            logging.getLogger(logger_name).setLevel(logging.DEBUG)
    logger.info("Verbose mode enabled")
