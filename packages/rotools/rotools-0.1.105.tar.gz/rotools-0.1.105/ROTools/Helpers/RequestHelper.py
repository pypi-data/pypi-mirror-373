import sys
import threading
import time
import traceback

import requests

_local_sessions = threading.local()


def get_session_data():
    if not hasattr(_local_sessions, "session"):
        _local_sessions.session = (requests.Session(), 0)

    session, counter = _local_sessions.session
    counter += 1
    _local_sessions.session = (session, counter)

    return session, counter


def make_request_wrapper(request_cb=None, sleep_times=(1, 5, 10, 15, 20, 25, 30, 30, None), **all_params):
    for sleep_time in sleep_times:
        try:
            return request_cb(**all_params)
        except Exception as e:
            print(f"Error [{repr(e)}] and sleep for {sleep_time}", file=sys.stderr)
            traceback.print_exc()
            if sleep_time is None:
                raise e
            time.sleep(sleep_time)
    raise Exception("Unknown error")
