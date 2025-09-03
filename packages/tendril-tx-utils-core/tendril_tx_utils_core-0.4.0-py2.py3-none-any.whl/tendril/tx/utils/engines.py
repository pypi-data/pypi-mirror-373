

from tendril.tx.utils.logger import TwistedLoggerMixin


class AsyncEngineBase(TwistedLoggerMixin):
    def __init__(self, *args, **kwargs):
        self._running = False
        super(AsyncEngineBase, self).__init__(*args, **kwargs)

    def _start(self):
        raise NotImplementedError

    def start(self):
        if not self._running:
            self._start()
            self._running = True

    def _stop(self):
        raise NotImplementedError

    def stop(self):
        if self._running:
            self._stop()
            self._running = False
