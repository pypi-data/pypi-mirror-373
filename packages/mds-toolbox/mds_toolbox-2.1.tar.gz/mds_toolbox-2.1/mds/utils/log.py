import logging.config

from mds.conf import settings
from mds.utils.module_loading import import_string

LOGGER_NAME = "mds"

DEFAULT_LOGGING = {
    "disable_existing_loggers": False,
    "formatters": {
        "blank": {"format": "%(message)s"},
        "simple": {
            "datefmt": "%Y-%m-%dT%H:%M:%SZ",
            "format": "[%(asctime)s] - %(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "level": "DEBUG",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        LOGGER_NAME: {
            "handlers": ["console"],
            "level": settings.LOG_LEVEL,
        },
    },
    "version": 1,
}


def configure_logging(
    logging_config: str, logging_settings: dict, log_level: str
) -> None:
    """

    Args:
        logging_config: Callable to use to configure logging
        logging_settings: Dictionary of logging settings
        log_level: Logging level
    """
    if logging_config:
        logging_config_func = import_string(logging_config)

        # Call custom logging config function first to avoid overrides
        if logging_settings:
            logging_config_func(logging_settings)

    if log_level:
        # Update logging level before applying default config
        DEFAULT_LOGGING["loggers"][LOGGER_NAME]["level"] = log_level

    # Apply the updated logging config
    logging.config.dictConfig(DEFAULT_LOGGING)

    # Ensure logger picks up the new level
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)
