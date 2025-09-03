# Configuration for logging in test_rest_api package
dictConfig: dict = {
    # Version of the logging configuration schema
    "version": 1,
    # If set to True then all loggers from the default configuration will be disabled
    # Only the once defined in this configuration will be available, which is not what we want
    # We need to make sure custom loggers created from root logger is not disabled
    # We need to make sure third party libraries loggers are not disabled
    # The logger will silently discard anything logged to it, not even propagating entries to a parent logger
    # Set disable_existing_loggers to False for avoiding the above cases
    "disable_existing_loggers": False,
    # Define formatters
    "formatters": {
        # Add simple formatter for test_rest_api_console_handler
        "simple": {
            # Format log records with date time, log level and message
            "format": "%(asctime)s  %(levelname)-8s➜ %(message)s",
            # Date time format for log records
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        # Add custom formatter for test_rest_api_report_handler
        "test_rest_api_report_formatter": {
            # Custom class created to format log records
            "()": "test_rest_api.logging.formatters.TestRestApiReportFormatter",
            # Date time format for log records
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    # Define filters
    "filters": {
        # Add custom filter for test_rest_api_console_handler
        "test_rest_api_console_filter": {
            # Custom class created to filter console log records
            "()": "test_rest_api.logging.filters.TestRestApiConsoleFilter"
        },
        # Add custom filter for test_rest_api_report_handler
        "test_rest_api_report_filter": {
            # Custom class created to filter report log records
            "()": "test_rest_api.logging.filters.TestRestApiReportFilter"
        }
    },
    # Define handlers
    "handlers": {
        # Add custom stderr handler to log messages to console
        "test_rest_api_console_handler": {
            # Sends logging output to streams such as sys.stdout, sys.stderr or any file-like object
            # More precisely, any object which supports write() and flush() methods
            "class": "logging.StreamHandler",
            # Set level to DEBUG to log all messages
            "level": "DEBUG",
            # Custom formatter defined in formatters
            "formatter": "simple",
            # Predefined file objects that correspond to Python's standard error streams
            "stream": "ext://sys.stderr",
            # Custom filters defined in filters
            "filters": ["test_rest_api_console_filter"]
        },
        # Add custom handler to log messages to report
        "test_rest_api_report_handler": {
            # Custom class created to handle report log records
            "()": "test_rest_api.logging.handlers.TestRestApiReportHandler",
            # Set level to DEBUG to log all messages
            "level": "DEBUG",
            # Custom formatter defined in formatters
            "formatter": "test_rest_api_report_formatter",
            # Custom filters defined in filters
            "filters": ["test_rest_api_report_filter"]
        },
        # Supports sending logging messages to a queue
        # Along with the QueueListener class, QueueHandler can be used to let handlers do their work on a
        # separate thread from the one which does the logging
        # This is important in web applications and also other service applications where threads servicing clients
        # need to respond as quickly as possible, while any potentially slow operations
        # such as sending an email via SMTPHandler are done on a separate thread
        # When created via configuration using dictConfig() listener attribute will contain a QueueListener instance
        # for use with this handler. Otherwise, it will be None.
        # Hence, we don't need to create QueueListener instance
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            # Add all handlers to queue handler
            "handlers": ["test_rest_api_console_handler", "test_rest_api_report_handler"],
            # If respect_handler_level is True, a handler’s level is respected
            # (compared with the level for the message) when deciding whether to pass messages to that handler;
            # Otherwise, the behaviour is as in previous Python versions - to always pass each message to each handler.
            "respect_handler_level": True
        }
    },
    # Define loggers
    "loggers": {
        # Root logger
        "root": {
            # Set level to DEBUG to log all messages
            "level": "DEBUG",
            # Root logger will only have queue handler
            "handlers": ["queue_handler"]
        }
    }
}
