from typing import Optional

from ..cache.service_info_cache import ServiceInfoCache
from ..model.naming_request import NotifySubscriberRequest
from ..model.naming_response import NotifySubscriberResponse
from ...transport.model.rpc_request import Request
from ...transport.model.rpc_response import Response
from ...transport.server_request_handler import IServerRequestHandler


class NamingPushRequestHandler(IServerRequestHandler):

    def name(self) -> str:
        return "NamingPushRequestHandler"

    def __init__(self, logger, service_info_cache: ServiceInfoCache):
        self.logger = logger
        self.service_info_cache = service_info_cache

    async def request_reply(self, request: Request) -> Optional[Response]:
        if not isinstance(request, NotifySubscriberRequest):
            return None

        self.logger.info("received naming push service info: %s,ackId:%s", str(request.serviceInfo),
                         request.requestId)
        await self.service_info_cache.process_service(request.serviceInfo)
        return NotifySubscriberResponse()
