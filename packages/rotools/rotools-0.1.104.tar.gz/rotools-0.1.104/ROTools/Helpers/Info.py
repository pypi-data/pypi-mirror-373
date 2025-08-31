import os
import sys
from datetime import datetime, timezone

import humanize


def print_info():
    python_ver = sys.version.replace('\n', ' ')
    print()
    print(f"Build version    \t: {os.getenv('RR_BUILD_VERSION', 'undefined')}")
    print(f"Build time UTC   \t: {os.getenv('RR_BUILD_TIME', 'undefined')}")
    print(f"Current time UTC \t: {datetime.now(timezone.utc)}")
    if os.getenv('RR_BUILD_TIME') is not None:
        build_old = humanize.naturaltime(datetime.now(timezone.utc) - datetime.fromisoformat(os.getenv('RR_BUILD_TIME')))
        print(f"Build old\t\t: {build_old}")
    print(f"PWD              \t: {os.getcwd()}")
    print(f"Python           \t: {python_ver}")
    print("---")
    print()
