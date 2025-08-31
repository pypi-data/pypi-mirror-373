import signal
import threading


class SignalHandler:
    _instance = None

    def __init__(self, use_exception=False):
        if self._instance is not None:
            raise Exception("This class is a singleton!")

        SignalHandler._instance = self

        self.stop_event = threading.Event()

        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls()
        return cls._instance

    def exit_gracefully(self, *args):
        print("SIGNAL STOP")
        self.stop_event.set()

    def is_exit_app(self):
        return self.stop_event.is_set()
