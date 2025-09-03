import atexit
import logging.config
import logging.handlers
from .config import dictConfig


def setup_root_logger():
    """ Setup root logger with filters, formatters, handlers and loggers """
    # Configure root logger using dictConfig
    logging.config.dictConfig(dictConfig)
    # Returns queue_handler handler which is defined in config
    queue_handler = logging.getHandlerByName("queue_handler")
    # Check if queue handler exists
    if queue_handler is not None:
        # Start listener for queue handler
        queue_handler.listener.start()
        # Register queue handler cleanup method to perform clean up upon interpreter termination
        atexit.register(queue_handler.listener.stop)
