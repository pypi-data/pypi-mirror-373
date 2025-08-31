import os
import sys
import time
import threading
from datetime import datetime

from . import config


def get_local_timestamp():
    x = datetime.now()
    return "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond / 1000)


class LogWriter:
    def __init__(self):
        self.filename = os.path.join(config.log_dir, config.main_filename)
        os.makedirs(config.log_dir, exist_ok=True)

        self.trace_file = None
        self.__last_color = None
        self.last_flush = 0
        self.trace_lock = threading.Lock()
        self.current_size = 0

        self.log_files_limit_count = config.log_files_limit_count
        self.log_files_limit_size = config.log_files_limit_size

        self._remove_existing_footer()

    def _remove_existing_footer(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r+', encoding='utf-8') as f:
                    content = f.read()
                    footer = "<!-- CONTAINER_END -->\n</div>\n</body>\n</html>"
                    if content.endswith(footer):
                        new_content = content[:-len(footer)]
                        f.seek(0)
                        f.write(new_content)
                        f.truncate()
            except Exception:
                pass

    def _load_template(self):
        template_path = os.path.join(os.path.dirname(__file__), config.template_file)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return content.replace('<!-- CONTAINER_END --></div></body></html>', '')
        except Exception:
            return """<!DOCTYPE html>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<style>
font { white-space: pre; }
</style>
<body bgcolor="black" text="white">
"""

    def _remove_extra_files(self, pattern, limit):
        import glob
        try:
            files = glob.glob(pattern)
            if len(files) > limit:
                files.sort()
                for f in files[:-limit]:
                    os.remove(f)
        except Exception:
            pass

    def _handle_new_log_file(self, file_name, file_pattern, fd):
        target = file_pattern % (fd)
        limit_count = self.log_files_limit_count

        target += ".tmp"
        limit_count -= 1

        try:
            os.rename(file_name, target)
        except OSError:
            pass

        self._remove_extra_files(file_pattern % "*", limit_count)

        cmd = "{ "
        cmd += "/bin/gzip -c " + target + " > " + target[:-4] + " 2> /dev/null ; "
        cmd += "/bin/rm -f " + target + " 2> /dev/null; "
        cmd += "/bin/rm -f trace_*.dat.tmp 2> /dev/null; "
        cmd += "/bin/rm -f ErrorLog_*.txt.gz.tmp 2> /dev/null; "
        cmd += "} &"
        os.system(cmd)

    def write_direct(self, msg, color, tag):
        escape_table = str.maketrans({
            '<': '&lt;',
            '>': '&gt;'
        })
        msg = msg.translate(escape_table)
        msg = msg.replace('\n', '<br>').replace('\r\n', '<br>').replace('=>', '&rArr;')

        x = datetime.now()
        date_str = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % (x.year, x.month, x.day, x.hour, x.minute, x.second, x.microsecond // 1000)
        _msg = date_str + ' - ' + msg
        formated_msg = f'<font color="{color}" tag="{tag}">{_msg}</font>\n'

        self.trace_lock.acquire()

        if not self.trace_file:
            if os.path.exists(self.filename):
                self.trace_file = open(self.filename, 'a', encoding='utf-8')
            else:
                self.trace_file = open(self.filename, 'w', encoding='utf-8')
                self.trace_file.write(self._load_template())

        try:
            self.trace_file.write(formated_msg)
        except Exception:
            pass

        try:
            t = time.monotonic()
            if t - self.last_flush > 2:
                self.trace_file.flush()
                self.last_flush = t
        except Exception:
            pass

        self.trace_lock.release()

    def close(self):
        if self.trace_file is None:
            return

        self.trace_lock.acquire()
        try:
            if self.trace_file:
                self.trace_file.write("<!-- CONTAINER_END -->\n</div>\n</body>\n</html>")
                self.trace_file.close()
                self.trace_file = None
        except Exception:
            pass
        finally:
            self.trace_lock.release()
