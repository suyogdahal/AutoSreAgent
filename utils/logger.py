from loguru import logger
import sys

# Remove any default handlers
logger.remove()

# Add a handler that only shows INFO level and above
logger.add(sys.stderr, level="INFO")
