import threading
from shift.helpers.utils import write_log


class Worker(object):
    def __init__(self, fn, args=()):
        self._fn = fn
        self._args = args

    def start(self, on_error=None, on_finish=None):
        self._on_error = on_error
        self._on_finish = on_finish
        thread = threading.Thread(target=self.run)
        thread.start()
        return thread

    def run(self):
        try:
            result = self._fn(*self._args)
            if self._on_finish:
                self._on_finish(result)
        except Exception as e:
            write_log("ERROR", str(e))
            if self._on_error:
                self._on_error(e)
