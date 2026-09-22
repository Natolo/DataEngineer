import logging
from .validation import InvalidDatetimeError, parse_datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    parse_datetime("not-a-datetime")
except InvalidDatetimeError as error:
    logger.warning("Failed to parse datetime: %s", error)

logger.info("Script finished.")