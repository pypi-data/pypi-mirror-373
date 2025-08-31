import time


class StopWatch:
    def __init__(self):
        self._start_time = time.time()
        self._last_stop_time = self._start_time
        self._named_periods = {}
        self.saved = None

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def __repr__(self):
        return f"{self.saved:>2.1f}"

    def store(self, name):
        _time = time.time()
        self._named_periods[name] = _time - self._last_stop_time
        self._last_stop_time = _time

    def get_time(self, name):
        return self._named_periods[name]

    def get_until_now(self):
        return time.time() - self._start_time

    def is_more_than_restart(self, time_limit_sec):
        _delta = time.time() - self._start_time
        if _delta < time_limit_sec:
            return False
        self._start_time = time.time()
        return True

    def stop(self):
        self.saved = time.time() - self._start_time
