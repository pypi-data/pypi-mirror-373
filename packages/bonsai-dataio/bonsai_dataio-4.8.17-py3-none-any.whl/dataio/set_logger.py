"""Module with set_logger function.

Part of package 'templates'
Part of the Getting the Data Right project
Created on Jul 25, 2023
@author: Joao Rodrigues
"""

import logging
import os
import sys

# from datetime import datetime
from pathlib import Path
from typing import Union


def set_logger(
    filename: Union[str, Path] = None,
    path: str = os.getcwd(),
    log_level: int = 20,
    log_format: str = ("%(asctime)s | [%(levelname)s]: %(message)s"),
    overwrite=False,
    create_path=False,
) -> None:
    """Initialize the logger.

    This function creates and initializes a log file.
    Logging output is sent both to the file and standard output.
    If 'filename' == None, no file output is written
    To further write to this logger add in the script:

    import logging
    logger = logging.getLogger('root')
    logger.info(<info_string>)
    logger.warning(<warning_string>)
    logger.error(<error_string>)

    Parameters
    ----------
    filename : str
        name of output file
    path : str
        path to folder of output file
    log_level : int
        lowest log level to be reported. Options are:
          10=debug
          20=info
          30=warning
          40=error
          50=critical
    log_format : str
        format of the log
    overwrite : bool
      whether to overwrite existing log file
    create_path : bool
      whether to create path to log file if it does not exist
    """
    try:
        log_format_date = logging.Formatter(log_format, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        raise "Log format not allowed. Try using default instead."

    try:
        logging.basicConfig(level=log_level)
    except ValueError:
        raise "Log level not allowed. Try help(setlogger) for options."

    logger = logging.getLogger("root")
    if logger.hasHandlers():
        logger.handlers.clear()

    # setup writing to console
    handler_stdout = logging.StreamHandler(sys.stdout)
    handler_stdout.setLevel(log_level)
    handler_stdout.setFormatter(log_format_date)
    logger.addHandler(handler_stdout)

    # setup writing to file
    if filename is not None:
        logger.info("Not writing to file")

        try:
            full_path = Path(path).joinpath(filename)
        except TypeError:
            raise (
                f"Cannot combine '{path}' and '{filename}' "
                "in one path, are both types and values valid?"
            )

        if not os.path.exists(path):
            logger.info("Data output path does not exist")
            if create_path:
                os.makedirs(path)
                logger.info("Data output path created")
            else:
                logger.error(" and 'create_path' option is disabled")
                raise FileNotFoundError
        if os.path.exists(full_path):
            logger.info("Data output full path exists")
            if not overwrite:
                logger.error(" and 'overwrite' option is disabled")
                raise FileExistsError

        try:
            handler_file = logging.FileHandler(full_path, mode="w")
        except FileExistsError:
            raise (f"Error opening file path '{full_path}', does it exist?")
        handler_file.setLevel(log_level)
        handler_file.setFormatter(log_format_date)
        logger.addHandler(handler_file)

    # to avoid duplicates
    logger.propagate = False

    # To log uncaught exceptions when running as script
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        logger.error(
            "Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback)
        )

    sys.excepthook = handle_exception

    if filename is not None:
        logger.info(f"Logger initialized at {full_path}")
    else:
        logger.info(f"Logger initialized at console only")
