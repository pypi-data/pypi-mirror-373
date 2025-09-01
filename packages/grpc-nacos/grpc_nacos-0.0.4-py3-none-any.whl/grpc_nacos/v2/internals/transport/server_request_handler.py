from abc import ABC, abstractmethod
from typing import Optional

from .model.internal_request import ClientDetectionRequest
from .model.internal_response import ClientDetectionResponse
from .model.rpc_request import Request
from .model.rpc_response import Response


class IServerRequestHandler(ABC):

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    async def request_reply(self, request: Request) -> Optional[Response]:
        pass


class ClientDetectionRequestHandler(IServerRequestHandler):
    def name(self) -> str:
        return "ClientDetectionRequestHandler"

    async def request_reply(self, request: Request) -> Optional[Response]:
        if not isinstance(request, ClientDetectionRequest):
            return None

        return ClientDetectionResponse()

