import logging
import traceback

from mds.mng.cli import cli

logger = logging.getLogger("mds")


def start_from_command_line_interface():
    """Access point to CLI API"""
    try:
        cli()
    except Exception as e:
        logger.debug(traceback.format_exc())
        logger.error(e)
        exit(1)
