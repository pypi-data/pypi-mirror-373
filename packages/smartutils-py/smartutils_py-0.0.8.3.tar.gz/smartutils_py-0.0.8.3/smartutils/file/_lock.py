import contextlib
import os
import threading

# from fcntl import LOCK_EX, LOCK_UN, LOCK_SH, flock
# import portalocker
from smartutils.log import logger


class Lock:
    def __init__(self, directory):
        self._file_name = os.path.join(directory, "_cook_server_lock")
        self._fd = open(self._file_name, "w")

    def _record(self):
        self._fd.write(f"{os.getpid()}\n{threading.current_thread().ident}")

    @contextlib.contextmanager
    def read_lock(self):
        self.lock()
        yield
        # flock(self._fd, LOCK_SH)
        # with portalocker.Lock(self._file_name) as f:
        #     yield
        self.unlock()

    @contextlib.contextmanager
    def write_lock(self):
        self.lock()
        self._record()
        yield
        self.unlock()
        # TODO: LOCK_NB非阻塞
        # flock(self._fd, LOCK_EX)
        # self._record()

    def lock(self): ...

    def unlock(self):
        ...
        # flock(self._fd, LOCK_UN)
        # self._fd.write("")
        # self._fd.close()

    def __del__(self):
        try:
            self._fd.close()
        except Exception as e:
            logger.error(f"Lock del err={e}")
