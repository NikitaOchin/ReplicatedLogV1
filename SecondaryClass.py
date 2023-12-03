import logging
import multiprocessing

logging.getLogger().setLevel(logging.DEBUG)


class SecondaryClass:
    def __init__(self, host, status, delay):
        self.host = host
        self.status = status
        self.delay = delay

    def get_status(self):
        return self.status

    def get_delay(self):
        return self.delay

    def get_host(self):
        return self.delay

    def set_delay(self, delay):
        self.delay = delay

    def set_status(self, status):
        self.status = status
