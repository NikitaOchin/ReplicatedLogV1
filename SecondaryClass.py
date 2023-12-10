import logging
import multiprocessing

logging.getLogger().setLevel(logging.DEBUG)


class SecondaryClass:
    def __init__(self, host):
        self.host = host
        self.status = multiprocessing.Value('i', 0)
        self.delay_arr = multiprocessing.Array('i', [0, 0])

    status_dict = [
        'Healthy',
        'Suspected',
        'Unhealthy'
    ]

    def next_delay(self):
        if sum(self.delay_arr.get_obj()) == 0:
            self.delay_arr.get_obj()[1] = 1
            return multiprocessing.Value('i', 0)

        buffer = self.delay_arr.get_obj()[1]
        self.delay_arr.get_obj()[1] = sum(self.delay_arr.get_obj())
        self.delay_arr.get_obj()[0] = buffer

        self.set_status()

        return multiprocessing.Value('i', sum(self.delay_arr.get_obj()))

    def clear_delay(self):
        self.delay_arr.get_obj()[0] = 0
        self.delay_arr.get_obj()[1] = 0
        self.set_status()

    def get_status(self):
        return self.status_dict[self.status.value]

    def get_delay(self):
        return multiprocessing.Value('i', sum(self.delay_arr.get_obj()))

    def get_host(self):
        return self.host

    def set_delay(self, delay):
        self.delay_arr = multiprocessing.Array('i', delay)

    def set_status(self):
        delay = sum(self.delay_arr.get_obj())
        if delay > 300:
            self.status.value = 2
        elif delay > 0:
            self.status.value = 1
        else:
            self.status.value = 0
