from concurrent.futures import Future
import threading
class Worker(object):
    def __init__(self, fn, args=()):
        self.future = Future()
        self._fn = fn
        self._args = args

    def start(self, cb=None):
        self._cb = cb
        self.future.set_running_or_notify_cancel()
        thread = threading.Thread(target=self.run, args=())
        thread.start()
        return thread

    def run(self):
        try:
            self.future.set_result(self._fn(*self._args))
        except BaseException as e:
            self.future.set_exception(e)

        if(self._cb):
            self._cb(self.future.result())