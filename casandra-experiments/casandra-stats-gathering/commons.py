import time


def current_milli_time_ms():
    return round(time.time() * 1000)


def current_milli_time_ns():
    return round(time.time() * 1000 * 1000)
