#!/usr/bin/env python3
"""
This file provides loggers.
"""

# ruff: noqa: E501

import os
import sys
import logging

# Singleton solution provided by https://stackoverflow.com/a/54209647


class Singleton(type):
    """
    Singleton class used as metaclass by :py:class:`logger.Logging`.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Logging(metaclass=Singleton):
    """
    Logging class.
    """

    logger = None
    log_file = "/tmp/qecore_logger.log"

    def __init__(self) -> None:
        """
        Initiating logger class with some basic logging setup.
        """

        self.logger = logging.getLogger("qecore_logger")
        self.logger.setLevel(logging.DEBUG)
        # Disable default handler.
        self.logger.propagate = False

        formatter = logging.Formatter(
            "[%(levelname)s] %(asctime)s: [%(filename)s:%(lineno)d] %(func_name)s: %(message)s"
        )

        # Default umask is 0o022 which turns off permissions for groups and others.
        # We need the logger file to be readable and modifiable by anyone.
        os.umask(0)

        # Setup of file handler.
        # All DEBUG and higher level logs will be going to the file.
        file_handler = logging.FileHandler(self.log_file)
        # This log file should be readable and writable by any user.
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        file_handler.set_name("qecore_file_handler")

        # Setup of console handler.
        # All INFO and higher level logs will be going to the console.
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        console_handler.set_name("qecore_console_handler")

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

        self.logger.addFilter(FuncFilter())

    def qecore_debug_to_console(self) -> None:
        """
        Set file handler level to DEBUG to get the output to console.
        """

        for handler in self.logger.handlers:
            if handler.get_name() == "qecore_console_handler":
                handler.setLevel(logging.DEBUG)
                break

    def qecore_truncate_the_logger_file(self) -> None:
        """
        If the Logging class is used from multiple files or scripts especially when
        running one script from another, the logger is not found and file is deleted,
        making previous logs disappear.

        Lets just null the file on request. In our case we can Null the file in our
        TestSandbox __init__ as that is perfect place to know we started over.
        """

        # Null the file only if it exists.
        # If it does not, no problem, do nothing.
        if os.path.isfile(self.log_file):
            # Default umask is 0o022 which turns off permissions for groups and others.
            os.umask(0)

            # Create a specific file descriptor for our needs with proper permissions.
            descriptor = os.open(
                path=self.log_file,
                flags=(os.O_CREAT | os.O_TRUNC),  # Create if not existing, truncate.
                mode=0o666,
            )
            # Close the file descriptor.
            os.close(descriptor)


class FuncFilter(logging.Filter):
    """
    Simple logging Filter to get name of the function the log is called from.
    """

    def filter(self, record):
        # Have to walk the frame a bit back.
        # 1. filter, 2. handle, 3. _log, 4. debug, 5. Original calling function.
        record.func_name = str(
            sys._getframe().f_back.f_back.f_back.f_back.f_back.f_code.co_name
        )
        return True
