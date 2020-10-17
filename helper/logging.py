#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Helper functions and classes for logging
"""

import logging


class DisableLogger(object):
    def __init__(self, active=False, level="CRITICAL"):
        self.active = active
        self.level = convert_str_logging_level(level)

    def __enter__(self):
        if self.active:
            logging.disable(self.level)

    def __exit__(self, a, b, c):
        if self.active:
            logging.disable(logging.NOTSET)


def configure_logging(
    filepath, logging_level="INFO", model="", timestamp="", stream=None, use_color=True
):
    fmt = f"[{model}][{timestamp}][%(asctime)s][%(levelname)7s][%(filename)s:%(lineno)d][%(funcName)s]%(message)s"
    lvl = convert_str_logging_level(logging_level)
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.setLevel(lvl)

    if use_color is True:

        from colorlog import ColoredFormatter

        color_fmt = "%(log_color)s" + fmt
        console_formatter = ColoredFormatter(
            color_fmt,
            datefmt=None,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
            secondary_log_colors={},
            style="%",
        )
    else:
        console_formatter = logging.Formatter(fmt)

    file_formatter = logging.Formatter(fmt)

    fh = logging.FileHandler(filepath)
    fh.setLevel(lvl)
    fh.setFormatter(file_formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(stream)
    ch.setLevel(lvl)
    ch.setFormatter(console_formatter)
    logger.addHandler(ch)


def convert_str_logging_level(str_level: str):
    if str_level.upper() == "DEBUG":
        return logging.DEBUG
    elif str_level.upper() == "INFO":
        return logging.INFO
    elif str_level.upper() == "WARNING":
        return logging.WARNING
    elif str_level.upper() == "ERROR":
        return logging.ERROR
    elif str_level.upper() == "CRITICAL":
        return logging.CRITICAL
