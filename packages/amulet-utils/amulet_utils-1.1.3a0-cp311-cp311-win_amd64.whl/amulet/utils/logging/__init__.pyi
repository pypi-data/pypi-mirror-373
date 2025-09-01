from __future__ import annotations

import typing

import amulet.utils.event

from . import _logging

__all__: list[str] = [
    "get_logger",
    "get_min_log_level",
    "register_default_log_handler",
    "set_min_log_level",
    "unregister_default_log_handler",
]

def get_logger() -> amulet.utils.event.Event[int, str]:
    """
    Get the logger event.
    This is emitted with the message and its level every time a message is logged.
    """

def get_min_log_level() -> int:
    """
    Get the maximum message level that will be logged.
    Registered handlers may be more strict.
    Thread safe.
    """

def register_default_log_handler() -> None:
    """
    Register the default log handler.
    This is registered by default with a log level of 20.
    Thread safe.
    """

def set_min_log_level(level: typing.SupportsInt) -> None:
    """
    Set the maximum message level that will be logged.
    Registered handlers may be more strict.
    Thread safe.
    """

def unregister_default_log_handler() -> None:
    """
    Unregister the default log handler.
    Thread safe.
    """
