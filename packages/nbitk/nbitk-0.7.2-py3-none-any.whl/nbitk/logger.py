import logging


def get_formatted_logger(name, config=None):
    """
    Instantiates a python `logging` object for the specified name and verbosity level.
    The function further configures this object so that the logging message it emits
    are formatted to include a time stamp.

    At present, the configuration of the logger is minimal. However, in combination
    with the config object, it is possible to extend this functionality, e.g. to
    format logs and timestamps in various ways.

    Examples:
        >>> from nbitk.logger import get_formatted_logger
        >>> from nbitk.config import Config
        >>> conf = Config()
        >>> conf.load_config('/path/to/config.yaml')
        >>> log = get_formatted_logger(conf)
        >>> log.debug('This is a debug message, of lowest severity, mostly used by programmers')
        >>> log.info('This is a message that may be of interest to users, but quite verbose')
        >>> log.info('This is a warning that users should probably investigate')
        >>> log.error('Something has gone seriously wrong')
        >>> log.fatal('This happens when an exception is raised')

        >>> # The logger can be passed into constructors, so that the object instance can emit its
        >>> # messages in a manner controlled by the user, e.g.
        >>> from nbitk.Services.MinioS3 import MinioS3
        >>> minio = MinioS3(log)

    :param name: name for the logger
    :param config: Config object
    :return:
    """
    # Create a logger
    requested_logger = logging.getLogger(name)

    if config:
        log_level = config.get("log_level")
    else:
        log_level = "INFO"

    # Set the log level
    requested_logger.setLevel(log_level)

    # Check if the logger already has handlers
    if not requested_logger.handlers:
        # Create a console handler
        handler = logging.StreamHandler()

        # Define the format for the log messages,
        # including the date and time stamp
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

        # Set the date format
        date_format = "%Y-%m-%d %H:%M:%S"

        # Create a formatter using the specified format and date format
        formatter = logging.Formatter(log_format, datefmt=date_format)

        # Set the formatter for the handler
        handler.setFormatter(formatter)

        # Add the handler to the logger
        requested_logger.addHandler(handler)

    return requested_logger
