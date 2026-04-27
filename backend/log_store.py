import threading
import time

_lock = threading.Lock()
_MAX = 20

_logs: dict = {
    "drl": [],
    "mappo": [],
    "qos": [],
}


def add(module: str, entry: dict) -> None:
    entry["_ts"] = round(time.time(), 3)
    with _lock:
        bucket = _logs[module]
        bucket.append(entry)
        if len(bucket) > _MAX:
            bucket.pop(0)


def get_all() -> dict:
    with _lock:
        return {k: list(v) for k, v in _logs.items()}
