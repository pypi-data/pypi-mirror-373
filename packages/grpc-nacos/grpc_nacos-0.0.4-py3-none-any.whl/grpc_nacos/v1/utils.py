from typing import Optional
import time


def get_group_name(service_name: str, group_name: str):
    return f"{group_name}@@{service_name}"


def get_service_cache_key(service_name: str, clusters: Optional[str] = None):
    if not clusters:
        return service_name
    return f"{service_name}@@{clusters}"


def get_current_time_millis():
    t = time.time()
    return int(round(t * 1000))