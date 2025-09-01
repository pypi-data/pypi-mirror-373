import logging
import atexit

# Set a default logging configuration
# If a configuration was set before this was imported this will do nothing.
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")

from . import (
    get_logger,
    unregister_default_log_handler,
    register_default_log_handler,
    get_min_log_level,
)

# Connect to python's logging module
logger = logging.getLogger("amulet.logging")


def on_msg(level: int, msg: str) -> None:
    logger.log(level, msg)


if get_min_log_level() <= 10:
    get_logger().dispatch(10, "Connecting python logger.")

logging_token = get_logger().connect(on_msg)


def python_shutdown() -> None:
    if get_min_log_level() <= 10:
        get_logger().dispatch(10, "Disconnecting python logger.")
    # On python shutdown, disconnect the logger so it can't get called after python has shut down.
    get_logger().disconnect(logging_token)
    # Reconnect the default logger to get logging after python has shut down.
    register_default_log_handler()
    if get_min_log_level() <= 10:
        get_logger().dispatch(10, "Disconnected python logger.")


atexit.register(python_shutdown)

# Disconnect default logging configuration.
# This handler is needed for any logging needed before this script is run.
unregister_default_log_handler()

if get_min_log_level() <= 10:
    get_logger().dispatch(10, "Connected python logger.")
