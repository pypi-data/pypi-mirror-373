import atexit
import signal
import sys
from .core import Logger

# Create a singleton instance
_logger = Logger()


def _handle_exit(signum=None, frame=None):
    """Handler para sinais de término"""
    close()
    if signum is not None:
        sys.exit(0)


if hasattr(signal, 'SIGTERM'):
    signal.signal(signal.SIGTERM, _handle_exit)
if hasattr(signal, 'SIGINT'):
    signal.signal(signal.SIGINT, _handle_exit)

atexit.register(_handle_exit)


def log(message, color=None, tag="log"):
    _logger.log(message, color, tag)


def info(message, color=None, tag="info"):
    _logger.info(message, color, tag)


def debug(message, color=None, tag="debug"):
    _logger.debug(message, color, tag)


def warning(message, color=None, tag="warning"):
    _logger.warning(message, color, tag)


def error(message, tag="error"):
    """Error function - equivalent to original error()"""
    _logger.error(message, tag)


def report_exception(exc, sleep=None):
    """Exception reporting - equivalent to original report_exception()"""
    _logger.report_exception(exc, sleep)

# Configuration functions


def set_html_trace(value):
    """Control HTML trace output"""
    _logger.set_html_trace(value)


def set_screen_trace(value):
    """Control screen trace output"""
    _logger.set_screen_trace(value)


def set_default_tag_color(value):
    _logger.set_default_tag_color(value)


def config(**kwargs):
    """Configure logger settings"""
    from . import config as cfg
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)


def close():
    """Close logger and finalize HTML file"""
    _logger.close()


# Compatibility aliases
finalize = close
