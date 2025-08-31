import threading
import traceback
import time
from datetime import datetime


from .writer import LogWriter


class Logger:
    def __init__(self):
        self.writer = LogWriter()
        self.html_trace = True
        self.screen_trace = False
        self.default_tag_color = {}

    def set_html_trace(self, value):
        self.html_trace = value
        if not self.html_trace:
            import os
            os.system("del trace* 2> nul")

    def set_default_tag_color(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError('Invalid Type used to set default tag color.')
        self.default_tag_color = value

    def set_screen_trace(self, value):
        self.screen_trace = value

    def _write_message(self, msg, color, tag):
        if self.screen_trace:
            print(str(msg))

        if not (_color := self.default_tag_color.get(tag, color)):
            _color = 'White'

        self.writer.write_direct(str(msg), _color, tag)

    def log(self, message, color=None, tag="log"):
        self._write_message(message, color, tag)

    def info(self, message, color=None, tag="info"):
        self._write_message(message, color, tag)

    def debug(self, message, color=None, tag="debug"):
        self._write_message("## " + message, color, tag)

    def warning(self, message, color=None, tag="warning"):
        self._write_message('⚠️' + message, color="gold", tag=tag)

    def error(self, message, tag="error"):
        self._write_message("****" + str(message), color="red", tag=tag)

    def report_exception(self, exc, sleep=None):
        try:
            t = "{}".format(type(threading.currentThread())).split("'")[1].split('.')[1]
        except IndexError:
            t = 'UNKNOWN'

        self.error(f"Bypassing exception at {t} ({exc})", tag="exception")
        self.error(f"**** Exception: <code>{traceback.format_exc()}</code>", tag="exception")

        if sleep:
            time.sleep(sleep)

    def close(self):
        self.writer.close()
