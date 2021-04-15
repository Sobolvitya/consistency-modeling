import time


def current_time_ms():
    return round(time.time() * 1000)


def current_time_ns():
    return round(time.time() * 1000 * 1000)


def chunks(lst, n) -> list:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
