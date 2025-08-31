from threading import Lock
from typing import Optional
import random

import nacos
from nacos.listener import SubscribeListener

from .models import Service, Instance
from .service_info_cache import ServiceInfoCache


class NacosClient:
    def __init__(
        self,
        server_addresses: str,
        namespace_id: str = "",
        log_level: str = "INFO",
    ) -> None:
        self._naming_service: Optional[nacos.NacosClient] = None
        self._server_addresses = server_addresses
        self._namespace_id = namespace_id
        self._service_info_cache = ServiceInfoCache()
        self._lock = Lock()
        self._is_setup = True
        self._log_level = log_level

    def __del__(self) -> None:
        self.shutdown()

    @property
    def naming_service(self) -> nacos.NacosClient:
        if self._naming_service is None:
            raise RuntimeError("Nacos client is not initialized, call await init() first")
        return self._naming_service

    def init(self) -> None:
        if self._naming_service is not None:
            return
        self._naming_service = nacos.NacosClient(
            server_addresses=self._server_addresses,
            namespace=self._namespace_id,
            log_level=self._log_level,
        )

    def shutdown(self) -> None:
        if self._naming_service:
            self._naming_service.stop_subscribe()
            self._naming_service = None

    def select_healthy_instances(
        self,
        service_name: str,
        group_name: str = "DEFAULT_GROUP",
        clusters: Optional[list[str]] = None,
    ) -> list[Instance]:
        if clusters is None:
            clusters = []

        clusters_str = ",".join(clusters)

        service_info, is_valid = self._service_info_cache.get_service_info(
            service_name=service_name,
            group_name=group_name,
            clusters=clusters_str,
        )

        if not is_valid:
            new_info = Service.model_validate(
                self.naming_service.list_naming_instance(
                    service_name=service_name,
                    clusters=clusters_str,
                    group_name=group_name,
                    healthy_only=True
                )
            )
            self._service_info_cache.process_service(new_info)

            if service_info is None:
                service_info = new_info

        if self._is_setup:
            self.naming_service.subscribe(
                listener_fn=SubscribeListener(
                    fn=self._subscribe_handler,
                    listener_name="service_info_cache_listener",
                ),
                service_name=service_name,
                group_name=group_name,
                clusters=clusters_str,
                healthy_only=True,
            )
            self._is_setup = False

        instance_list = []
        if service_info is not None and len(service_info.hosts) > 0:
            instance_list = service_info.hosts

        return instance_list

    def lb_select_one_healthy_instance(
        self,
        service_name: str,
        group_name: str = "DEFAULT_GROUP",
        clusters: Optional[list[str]] = None,
    ) -> Optional[tuple[str, int]]:
        instances = self.select_healthy_instances(
            service_name=service_name,
            group_name=group_name,
            clusters=clusters,
        )
        if not instances:
            return None
        weights = [instance.weight for instance in instances]
        selection = random.choices(instances, weights)[0]
        return selection.ip, selection.port

    def _subscribe_handler(self, event, instance):
        print(event, instance)
        # self._service_info_cache.clear_service(
        #     service_name=service_name,
        #     group_name=group_name,
        #     clusters=clusters_str,
        # ),