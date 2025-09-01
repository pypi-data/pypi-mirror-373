from abc import ABC
from typing import Optional

from .rpc_request import Request

CONNECTION_RESET_REQUEST_TYPE = "ConnectResetRequest"
CLIENT_DETECTION_REQUEST_TYPE = "ClientDetectionRequest"


class InternalRequest(Request, ABC):

    def get_module(self) -> str:
        return 'internal'


class HealthCheckRequest(InternalRequest):

    def get_request_type(self):
        return "HealthCheckRequest"


class ConnectResetRequest(InternalRequest):
    serverIp: Optional[str]
    serverPort: Optional[str]

    def get_request_type(self) -> str:
        return CONNECTION_RESET_REQUEST_TYPE


class ClientDetectionRequest(InternalRequest):
    def get_request_type(self) -> str:
        return CLIENT_DETECTION_REQUEST_TYPE


class ServerCheckRequest(InternalRequest):

    def get_request_type(self):
        return "ServerCheckRequest"


class ConnectionSetupRequest(InternalRequest):
    clientVersion: Optional[str] = ''
    tenant: Optional[str] = ''
    labels: dict = {}

    def get_request_type(self):
        return "ConnectionSetupRequest"
