from typing import Optional

from ..cache.config_subscribe_manager import ConfigSubscribeManager
from ..model.config_request import ConfigChangeNotifyRequest
from ...transport.model.internal_response import NotifySubscriberResponse
from ...transport.model.rpc_request import Request
from ...transport.model.rpc_response import Response
from ...transport.server_request_handler import IServerRequestHandler


class ConfigChangeNotifyRequestHandler(IServerRequestHandler):

    def name(self):
        return "ConfigChangeNotifyRequestHandler"

    def __init__(self, logger, config_subscribe_manager: ConfigSubscribeManager, client_name: str):
        self.logger = logger
        self.config_subscribe_manager = config_subscribe_manager
        self.client_name = client_name

    async def request_reply(self, request: Request) -> Optional[Response]:
        if not isinstance(request, ConfigChangeNotifyRequest):
            return None

        self.logger.info(
            f"received config change push,clientName:{self.client_name},dataId:{request.dataId},group:{request.group},tenant:{request.tenant}")
        await self.config_subscribe_manager.notify_config_changed(request.dataId, request.group,
                                                                  self.config_subscribe_manager.namespace_id)
        return NotifySubscriberResponse()
