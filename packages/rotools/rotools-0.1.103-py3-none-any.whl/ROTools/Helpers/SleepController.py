import time


class SleepController:
    def __init__(self, single_sleep, wake_up_cb):
        self._single_sleep = single_sleep
        self._wake_up_cb = wake_up_cb
        if self._wake_up_cb is None:
            self._wake_up_cb = lambda: False

    def sleep_for(self, sleep_time):
        _start_time = time.time()
        _delta = 0
        while _delta < sleep_time and not self._wake_up_cb():
            time.sleep(self._single_sleep)
            _delta = time.time() - _start_time
