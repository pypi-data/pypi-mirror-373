import atexit
import signal
import sys
import importlib.resources
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


def log_html_config(**kwargs):
    """
    Change default configuration values.

    Parameters:
        log_dir (str): Directory where log files will be stored.
                       Default: "logs".

        main_filename (str): Name of the main HTML log file.
                             Default: "log.html".

        log_files_limit_count (int): Maximum number of log files allowed in the
                                     directory before rotation starts.
                                     Default: 30.

        log_files_limit_size (int): Maximum allowed size (in bytes) for each
                                    log file before rotation occurs.
                                    Default: 3 MB.

        template_file (str): Path to the HTML template file used to render logs.
                             Default: "template.html".

    Returns:
        None: The function creates or updates log files in the log directory,
              but does not return a value.
    """
    from . import config as cfg
    for key, value in kwargs.items():
        if hasattr(cfg, key):
            setattr(cfg, key, value)


def close():
    """Close logger and finalize HTML file"""
    _logger.close()


# Compatibility aliases
finalize = close
