import logging
import multiprocessing

logging.getLogger().setLevel(logging.DEBUG)


class CountDownLatch:
    def __init__(self, count, app):
        self.app = app
        self.count = count
        self.lock = multiprocessing.Condition()

    def count_down(self):
        self.app.logger.debug(f"count_down with {self.count.value}")
        with self.lock:
            self.count.value -= 1
            if self.count.value <= 0:
                self.lock.notify_all()

    def awaiter(self):
        self.app.logger.debug(f"awaiter with {self.count.value}")
        with self.lock:
            while self.count.value > 0:
                self.lock.wait()
