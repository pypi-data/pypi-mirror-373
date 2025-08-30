import asyncio
from typing import Any, Optional
from collections import OrderedDict

import grpc

from .client import NacosClient


Endpoint = tuple[str, int]


class NacosChannel:
    def __init__(
        self,
        nacos_client: NacosClient,
        service_name: str,
        *,
        group_name: str = "DEFAULT_GROUP",
        clusters: Optional[list[str]] = None,
        default_credentials: Optional[grpc.ChannelCredentials] = None,
        options: Optional[list[tuple[str, str]]] = None,
        max_idle_channels: int = 64,
    ) -> None:
        self._nacos = nacos_client
        self._service_name = service_name
        self._group_name = group_name
        self._clusters = list(clusters) if clusters is not None else None
        self._default_credentials = default_credentials
        self._options = list(options or [])
        self._max_idle_channels = max_idle_channels

        self._channels: OrderedDict[tuple[str, int], grpc.aio.Channel] = OrderedDict()
        self._closed = False

    async def close(self) -> None:
        if self._closed:
            return
        channels = list(self._channels.values())
        self._channels.clear()
        for ch in channels:
            try:
                await ch.close()
            except Exception:
                pass
        self._closed = True

    # ---- channel-like factory methods ----
    def unary_unary(
        self,
        method: str,
        *,
        request_serializer=None,
        response_deserializer=None,
        **kwargs,
    ):
        return _UnaryUnaryCallable(
            self, method, request_serializer, response_deserializer, kwargs
        )

    def unary_stream(
        self,
        method: str,
        *,
        request_serializer=None,
        response_deserializer=None,
        **kwargs,
    ):
        return _UnaryStreamCallable(
            self, method, request_serializer, response_deserializer, kwargs
        )

    def stream_unary(
        self,
        method: str,
        *,
        request_serializer=None,
        response_deserializer=None,
        **kwargs,
    ):
        return _StreamUnaryCallable(
            self, method, request_serializer, response_deserializer, kwargs
        )

    def stream_stream(
        self,
        method: str,
        *,
        request_serializer=None,
        response_deserializer=None,
        **kwargs,
    ):
        return _StreamStreamCallable(
            self, method, request_serializer, response_deserializer, kwargs
        )

    def _get_or_create_channel(
        self, endpoint: Endpoint, creds: Optional[grpc.ChannelCredentials]
    ) -> grpc.aio.Channel:
        host, port = endpoint
        key = (host, port)
        
        ch = self._channels.get(key)
        if ch is not None:
            self._channels.move_to_end(key, last=True)
            return ch

        target = f"{host}:{port}"
        if creds is None:
            new_channel = grpc.aio.insecure_channel(target, options=self._options)
        else:
            new_channel = grpc.aio.secure_channel(target, creds, options=self._options)

        if self._max_idle_channels > 0 and len(self._channels) >= self._max_idle_channels:
            old_key, old_channel = self._channels.popitem(last=False)
            try:
                asyncio.create_task(old_channel.close())
            except Exception:
                pass
        self._channels[key] = new_channel
        return new_channel

    async def _pick_channel(self) -> grpc.aio.Channel:
        if self._closed:
            raise RuntimeError("NacosChannel is closed")
        endpoint = await self._nacos.lb_select_one_healthy_instance(
            service_name=self._service_name,
            group_name=self._group_name,
            clusters=self._clusters,
        )
        if endpoint is None:
            raise RuntimeError(
                "No healthy instances available; ensure channel is started and service has healthy instances"
            )
        creds = self._default_credentials
        return self._get_or_create_channel(endpoint, creds)


class _BaseCallable:
    def __init__(
        self,
        parent: NacosChannel,
        method: str,
        request_serializer,
        response_deserializer,
        mc_kwargs: dict[str, Any],
    ):
        self._parent = parent
        self._method = method
        self._request_serializer = request_serializer
        self._response_deserializer = response_deserializer
        self._mc_kwargs = mc_kwargs

    async def _get_underlying(self, method_name: str):
        ch = await self._parent._pick_channel()
        fn = getattr(ch, method_name)
        return fn(
            self._method,
            request_serializer=self._request_serializer,
            response_deserializer=self._response_deserializer,
            **self._mc_kwargs,
        )


class _UnaryUnaryCallable(_BaseCallable):
    async def __call__(
        self,
        request,
        *,
        timeout=None,
        metadata=None,
        credentials=None,
        wait_for_ready=None,
        compression=None,
    ):
        mc = await self._get_underlying("unary_unary")
        return await mc(
            request,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )

    async def with_call(
        self,
        request,
        *,
        timeout=None,
        metadata=None,
        credentials=None,
        wait_for_ready=None,
        compression=None,
    ):
        mc = await self._get_underlying("unary_unary")
        return await mc.with_call(
            request,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )


class _UnaryStreamCallable(_BaseCallable):
    def __call__(self, *args, **kwargs):  # pragma: no cover - explicit unsupported path
        raise NotImplementedError(
            "unary_stream is not supported in simplified NacosChannel; use direct grpc channel"
        )


class _StreamUnaryCallable(_BaseCallable):
    async def __call__(
        self,
        request_iterator,
        *,
        timeout=None,
        metadata=None,
        credentials=None,
        wait_for_ready=None,
        compression=None,
    ):
        mc = await self._get_underlying("stream_unary")
        return await mc(
            request_iterator,
            timeout=timeout,
            metadata=metadata,
            credentials=credentials,
            wait_for_ready=wait_for_ready,
            compression=compression,
        )


class _StreamStreamCallable(_BaseCallable):
    def __call__(self, *args, **kwargs):  # pragma: no cover - explicit unsupported path
        raise NotImplementedError(
            "stream_stream is not supported in simplified NacosChannel; use direct grpc channel"
        )
