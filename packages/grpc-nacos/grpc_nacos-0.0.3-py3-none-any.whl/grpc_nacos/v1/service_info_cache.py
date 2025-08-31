import threading
from typing import Optional

from .models import Service
from .utils import get_service_cache_key, get_group_name


class ServiceInfoCache:
    def __init__(self):
        self.service_info_map: dict[str, Service] = {}
        self.invalid_service_info: set[str] = set()
        self.lock = threading.Lock()

    def get_service_info(self, service_name: str, group_name: str, clusters: Optional[str] = "") -> tuple[Optional[Service], bool]:
        cache_key = get_service_cache_key(get_group_name(service_name, group_name), clusters)
        with self.lock:
            service = self.service_info_map.get(cache_key)
            is_invalid = (cache_key in self.invalid_service_info) or (service is None)
            return service, not is_invalid

    def process_service(self, service: Service):
        if service is None:
            return

        if len(service.hosts) == 0:
            return

        cache_key = get_service_cache_key(service.name, service.clusters)

        with self.lock:
            old_service = self.service_info_map.get(cache_key, None)
            if old_service is not None and old_service.lastRefTime >= service.lastRefTime:
                return

            self.service_info_map[cache_key] = service
            self.invalid_service_info.discard(cache_key)

    def clear_service(self, service_name: str, group_name: str, clusters: Optional[str] = ""):
        cache_key = get_service_cache_key(get_group_name(service_name, group_name), clusters)
        with self.lock:
            self.invalid_service_info.add(cache_key)
