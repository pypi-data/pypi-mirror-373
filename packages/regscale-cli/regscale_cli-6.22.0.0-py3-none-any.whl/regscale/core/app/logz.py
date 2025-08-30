#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rich Logging"""

# standard python imports
import logging
import os
import tempfile
from logging.handlers import TimedRotatingFileHandler
from typing import Any, Optional

import click
from rich.logging import RichHandler
from rich.traceback import install
from rich.console import Console

from regscale import exceptions

if not os.getenv("REGSCALE_DEBUG", False):
    install(suppress=[click, exceptions])


def create_logger(propagate: Optional[bool] = None, custom_handler: Optional[Any] = None) -> logging.Logger:
    """
    Create a logger for use in all cases

    :param Optional[bool] propagate: Whether to propagate the logger, defaults to None
    :param Optional[Any] custom_handler: Custom handler to add to the logger, defaults to None
    :return: logger object
    :rtype: logging.Logger
    """
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    # Try to get the log width from the environment variable, default to 160 if not set
    try:
        width = int(os.environ.get("REGSCALE_LOG_WIDTH"))  # Default to 160 if not set
        rich_handler = RichHandler(rich_tracebacks=False, markup=True, show_time=False, console=Console(width=width))
    except (TypeError, ValueError):
        # If the value is not an integer, set it to None (goes to default to use the full width of the terminal)
        # Without this except block, the logs do NOT print
        rich_handler = RichHandler(rich_tracebacks=False, markup=True, show_time=False)

    rich_handler.setLevel(loglevel)

    # Only create file handler if not in container
    handlers: list[logging.Handler] = [rich_handler]
    if os.getenv("REGSCALE_ECS", False) != "True":
        file_handler = TimedRotatingFileHandler(
            filename=f"{tempfile.gettempdir()}{os.sep}RegScale.log",
            when="D",
            interval=3,
            backupCount=10,
        )
        file_handler.setLevel(loglevel)
        handlers.append(file_handler)

    if custom_handler:
        handlers.append(custom_handler)

    logging.getLogger("botocore").setLevel(logging.CRITICAL)
    logging.basicConfig(
        level=loglevel,
        format="%(asctime)s [%(levelname)-5.5s]  %(message)s",
        datefmt="[%Y/%m/%d %H:%M;%S]",
        handlers=handlers,
        force=os.getenv("REGSCALE_ECS", False) == "True",
    )

    logger = logging.getLogger("regscale")
    logger.handlers = handlers
    logger.setLevel(loglevel)
    logger.parent.handlers = []
    if propagate is not None:
        logger.propagate = propagate
    return logger
