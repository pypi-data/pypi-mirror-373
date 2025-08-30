import random
from typing import Optional

from v2.nacos import (
    ListInstanceParam,
    NacosNamingService,
    ClientConfig, Instance,
)


class NacosClient:
    def __init__(
        self,
        server_addresses: str,
        namespace_id: str = "",
        log_level: str = "INFO",
    ) -> None:
        self._naming_service: Optional[NacosNamingService] = None
        self._server_addresses = server_addresses
        self._namespace_id = namespace_id
        self._log_level = log_level

    @property
    def naming_service(self) -> NacosNamingService:
        if self._naming_service is None:
            raise RuntimeError("Nacos client is not initialized, call await init() first")
        return self._naming_service

    async def init(self) -> None:
        if self._naming_service is not None:
            return
        cfg = ClientConfig(
            server_addresses=self._server_addresses,
            namespace_id=self._namespace_id,
            log_level=self._log_level,
        )
        cfg.set_load_cache_at_start(False)
        self._naming_service = await NacosNamingService.create_naming_service(cfg)

    async def shutdown(self) -> None:
        if self._naming_service:
            await self._naming_service.shutdown()
            self._naming_service = None

    async def select_healthy_instances(
        self,
        service_name: str,
        group_name: str = "DEFAULT_GROUP",
        clusters: Optional[list[str]] = None,
    ) -> list[Instance]:
        if clusters is None:
            clusters = []
        req = ListInstanceParam(
            service_name=service_name,
            group_name=group_name,
            clusters=clusters,
            healthy_only=True,
            subscribe=True,
        )
        instances = await self.naming_service.list_instances(req)
        return instances

    async def lb_select_one_healthy_instance(
        self,
        service_name: str,
        group_name: str = "DEFAULT_GROUP",
        clusters: Optional[list[str]] = None,
    ) -> Optional[tuple[str, int]]:
        instances = await self.select_healthy_instances(
            service_name=service_name,
            group_name=group_name,
            clusters=clusters,
        )
        if not instances:
            return None
        weights = [instance.weight for instance in instances]
        selection = random.choices(instances, weights)[0]
        return selection.ip, selection.port
