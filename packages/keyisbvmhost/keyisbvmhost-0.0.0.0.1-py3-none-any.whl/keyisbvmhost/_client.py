
import os
import httpx
import asyncio
import typing as _typing
import logging as logging2
from typing import Union, List, Dict, Tuple, Optional
import datetime
logging2.basicConfig(level=logging2.INFO)

from KeyisBLogging import logging
from typing import Dict, List, Tuple, Optional, cast, AsyncGenerator, Callable
from itertools import count
from aioquic.asyncio.client import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import DataReceived, DatagramReceived, H3Event, HeadersReceived
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent


import time
import json, ssl, asyncio, struct, base64, hashlib
from typing import Any, Dict, Optional
import websockets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import msgpack
import logging
from httpx import Request, Headers, URL
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("websockets").setLevel(logging.DEBUG)

import KeyisBClient
from KeyisBClient import Url
httpxAsyncClient = httpx.AsyncClient(verify=KeyisBClient.ssl_gw_crt_path, timeout=200)

class GNExceptions:
    class ConnectionError:
        class openconnector():
            """Ошибка подключения к серверу openconnector.gn"""
            
            class connection(Exception):
                def __init__(self, message="Ошибка подключения к серверу openconnector.gn. Сервер не найден."):
                    super().__init__(message)

            class timeout(Exception):
                def __init__(self, message="Ошибка подключения к серверу openconnector.gn. Проблема с сетью или сервер перегружен."):
                    super().__init__(message)

            class data(Exception):
                def __init__(self, message="Ошибка подключения к серверу openconnector.gn. Сервер не подтвердил подключение."):
                    super().__init__(message)

        class dns_core():
            """Ошибка подключения к серверу dns.core"""
            class connection(Exception):
                def __init__(self, message="Ошибка подключения к серверу dns.core Сервер не найден."):
                    super().__init__(message)

            class timeout(Exception):
                def __init__(self, message="Ошибка подключения к серверу dns.core Проблема с сетью или сервер перегружен"):
                    super().__init__(message)
    
            class data(Exception):
                def __init__(self, message="Ошибка подключения к серверу dns.core Сервер не подтвердил подключение."):
                    super().__init__(message)
    


        class connector():
            """Ошибка подключения к серверу <?>~connector.gn"""
            
            class connection(Exception):
                def __init__(self, message="Ошибка подключения к серверу <?>~connector.gn. Сервер не найден."):
                    super().__init__(message)

            class timeout(Exception):
                def __init__(self, message="Ошибка подключения к серверу <?>~connector.gn. Проблема с сетью или сервер перегружен"):
                    super().__init__(message)
    
            class data(Exception):
                def __init__(self, message="Ошибка подключения к серверу <?>~connector.gn. Сервер не подтвердил подключение."):
                    super().__init__(message)



from KeyisBClient.gn import GNRequest, GNResponse, GNProtocol




class AsyncClient:
    def __init__(self):
        self.__dns_core__ipv4 = '51.250.85.38:52943'
        self.__dns_gn__ipv4 = None

        self.__user = {}
        self.__current_session = {}
        self.__request_callbacks = {}
        self.__response_callbacks = {}

        self._client: QuicClient = QuicClient()

        self._active_connections: Dict[str, Any] = {}

    async def _getCoreDNS(self, domain: str):
        try:
            if self.__dns_gn__ipv4 is None:
                r1 = await httpxAsyncClient.request('GET', f'https://{self.__dns_core__ipv4}/gn/getIp?d=dns.gn')
                if r1.status_code != 200:
                    raise GNExceptions.ConnectionError.dns_core.data
                r1_data = r1.json()
                self.__dns_gn__ipv4 = r1_data['ip'] + ':' + str(r1_data['port'])


            r2 = await httpxAsyncClient.request('GET', f'https://{self.__dns_gn__ipv4}/gn/getIp?d={domain}')
        except httpx.TimeoutException:
            raise GNExceptions.ConnectionError.dns_core.timeout
        except:
            raise GNExceptions.ConnectionError.dns_core.connection

        if r2.status_code != 200:
            raise GNExceptions.ConnectionError.dns_core.data

        r2_data = r2.json()

        return r2_data

    def addRequestCallback(self, callback: Callable, name: str):
        self.__request_callbacks[name] = callback

    def addResponseCallback(self, callback: Callable, name: str):
        self.__response_callbacks[name] = callback

  
    async def connect(self, domain: str):
        if domain in self._active_connections:
            return

        data = await self._getCoreDNS(domain)
        # подключаемся к серверу gn-proxy
        await self._client.connect(data['ip'], data['port'])
        self._active_connections[domain] = 'active'

    async def disconnect(self):
        await self._client.disconnect()


    def _return_token(self, bigToken: str, s: bool = True) -> str:
        return bigToken[:128] if s else bigToken[128:]


    async def request(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]) -> GNResponse:
        """
        Build and send a async request.
        
        ```python
        gnAsyncClient = KeyisBClient.AsyncClient()
        async def func():
            response = await gnAsyncClient.request(GNRequest('GET', Url('gn://example.com/example')))
            command = response.command()
            data = response.payload()
        ```
        """






        if isinstance(request, GNRequest):
            

            if request.url.hostname not in self._active_connections:
                await self.connect(request.url.hostname)
                


            for f in self.__request_callbacks.values():
                asyncio.create_task(f(request))

            r = await self._client.asyncRequest(request)

            for f in self.__response_callbacks.values():
                asyncio.create_task(f(r))

            return r
        
        # else:
        #     async def wrapped(request) -> AsyncGenerator[GNRequest, None]:
        #         async for req in request:
        #             if req.gn_protocol is None:
        #                 req.setGNProtocol(self.__current_session['protocols'][0])
        #             req._stream = True
                    
        #             for f in self.__request_callbacks.values():
        #                 asyncio.create_task(f(req))
                        
        #             yield req
        #     r = await self.client.asyncRequest(wrapped(request))
        
        #     for f in self.__response_callbacks.values():
        #         asyncio.create_task(f(r))
                
        #     return r

    async def requestStream(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]) -> AsyncGenerator[GNResponse, None]:
        """
        Build and send a async request.
        """
        if isinstance(request, GNRequest):
            if request.gn_protocol is None:
                request.setGNProtocol(self.__current_session['protocols'][0])
                
            for f in self.__request_callbacks.values():
                asyncio.create_task(f(request))

            async for response in self.client.asyncRequestStream(request):
                    
                for f in self.__response_callbacks.values():
                    asyncio.create_task(f(response))

                yield response
        else:
            async def wrapped(request) -> AsyncGenerator[GNRequest, None]:
                async for req in request:
                    if req.gn_protocol is None:
                        req.setGNProtocol(self.__current_session['protocols'][0])
                            
                    for f in self.__request_callbacks.values():
                        asyncio.create_task(f(req))
                        
                    req._stream = True
                    yield req
            async for response in self.client.asyncRequestStream(wrapped(request)):
                
                for f in self.__response_callbacks.values():
                    asyncio.create_task(f(response))

                yield response









# gn:quik

from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.events import QuicEvent, StreamDataReceived, StreamReset
from aioquic.quic.connection import END_STATES
import asyncio
from collections import deque
from typing import Dict, Deque, Tuple, Optional, List

# ---------------------------------------------------------------------------
#  Raw QUIC client with a dedicated SYS‑stream that consumes ~90 % CWND
# ---------------------------------------------------------------------------
#  Основная идея:
#  • Один постоянный bidirectional stream (sys_stream_id) используется для 
#    служебных сообщений.
#  • Остальные запросы открываются в обычных потоках (user streams).
#  • Отправка данных идёт через собственный scheduler: берём 9 «квантов» из
#    SYS‑очереди и 1 квант из USER‑очереди, пока есть SYS‑данные.
#  • Таким образом SYS‑канал получает ~90 % пропускной способности.
# ---------------------------------------------------------------------------

import asyncio
import time
from collections import deque
from dataclasses import dataclass
from itertools import count
from typing import Deque, Dict, Optional, Tuple, Union

from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived, StreamReset


class RawQuicClient(QuicConnectionProtocol):
    """Чистый‑QUIC клиент с приоритизированным SYS‑каналом + стриминг."""

    SYS_RATIO_NUM = 9  # SYS 9/10
    SYS_RATIO_DEN = 10
    KEEPALIVE_INTERVAL = 10  # сек
    KEEPALIVE_IDLE_TRIGGER = 30  # сек

    # ────────────────────────────────────────────────────────────────── init ─┐
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._sys_stream_id: Optional[int] = None
        self._queue_sys: Deque[Tuple[int, bytes, bool]] = deque()
        self._queue_user: Deque[Tuple[int, bytes, bool]] = deque()

        # <‑‑ Future | Queue[bytes | None]
        self._inflight: Dict[int, Union[asyncio.Future, asyncio.Queue[Optional[GNResponse]]]] = {}
        self._inflight_streams: Dict[int, bytearray] = {}
        self._sys_inflight: Dict[int, asyncio.Future] = {}
        self._buffer: Dict[Union[int, str], bytearray] = {}

        self._sys_budget = self.SYS_RATIO_NUM
        self._sys_id_gen = count(1)  # int64 message‑id generator

        self._last_activity = time.time()
        self._running = True
        self._ping_id_gen = count(1)  # int64 ping‑id generator
        asyncio.create_task(self._keepalive_loop())

    # ───────────────────────────────────────── private helpers ─┤
    def _activity(self):
        self._last_activity = time.time()

    async def _keepalive_loop(self):
        while self._running:
            await asyncio.sleep(self.KEEPALIVE_INTERVAL)
            idle_time = time.time() - self._last_activity
            if idle_time > self.KEEPALIVE_IDLE_TRIGGER:
                self._quic.send_ping(next(self._ping_id_gen))
                self.transmit()
                self._last_activity = time.time()

    def stop(self):
        self._running = False

    # ───────────────────────────────────────────── events ─┤
    def quic_event_received(self, event: QuicEvent) -> None:  # noqa: C901
        # ─── DATA ───────────────────────────────────────────
        if isinstance(event, StreamDataReceived):
            #print(event)
            # SYS поток
            if event.stream_id == self._sys_stream_id:
                buf = self._buffer.setdefault("sys", bytearray())
                buf.extend(event.data)
                while True:
                    if len(buf) < 12:
                        break
                    msg_id = int.from_bytes(buf[:8], "little")
                    size = int.from_bytes(buf[8:12], "little")
                    if len(buf) < 12 + size:
                        break
                    payload = bytes(buf[12 : 12 + size])
                    del buf[: 12 + size]
                    fut = self._sys_inflight.pop(msg_id, None) if msg_id else None
                    if fut and not fut.done():
                        fut.set_result(payload)
            # USER поток
            else:
                handler = self._inflight.get(event.stream_id)
                if handler is None:
                    return
                
                # Чтение в зависимости от режима
                if isinstance(handler, asyncio.Queue): # стрим от сервера
                    # получаем байты

                    buf = self._buffer.setdefault(event.stream_id, bytearray())
                    buf.extend(event.data)

                    if len(buf) < 8: # не дошел даже frame пакета
                        return
                    
                    # получаем длинну пакета
                    mode, stream, lenght = GNResponse.type(buf)

                    if mode != 4: # не наш пакет
                        self._buffer.pop(event.stream_id)
                        return
                    
                    if not stream: # клиент просил стрим, а сервер прислал один пакет
                        self._buffer.pop(event.stream_id)
                        return
                    
                    # читаем пакет
                    if len(buf) < lenght: # если пакет не весь пришел, пропускаем
                        return
                    
                    # пакет пришел весь

                    # берем пакет
                    data = buf[:lenght]

                    # удаляем его из буфера
                    del buf[:lenght]
                        
                    
                    r = GNResponse.deserialize(data, 2)
                    handler.put_nowait(r)
                    if event.end_stream:
                        handler.put_nowait(None)
                        self._buffer.pop(event.stream_id)
                        self._inflight.pop(event.stream_id, None)



                else:  # Future
                    buf = self._buffer.setdefault(event.stream_id, bytearray())
                    buf.extend(event.data)
                    if event.end_stream:
                        self._inflight.pop(event.stream_id, None)
                        data = bytes(self._buffer.pop(event.stream_id, b""))
                        if not handler.done():
                            handler.set_result(data)

        # ─── RESET ──────────────────────────────────────────
        elif isinstance(event, StreamReset):
            handler = self._inflight.pop(event.stream_id, None) or self._sys_inflight.pop(
                event.stream_id, None
            )
            if handler is None:
                return
            if isinstance(handler, asyncio.Queue):
                handler.put_nowait(None)
            else:
                if not handler.done():
                    handler.set_exception(RuntimeError("stream reset"))

    # ─────────────────────────────────────────── scheduler ─┤
    def _enqueue(self, sid: int, blob: bytes, end_stream: bool, is_sys: bool):
        (self._queue_sys if is_sys else self._queue_user).append((sid, blob, end_stream))

    def _schedule_flush(self):
        while (self._queue_sys or self._queue_user) and self._quic._close_event is None:
            q = None
            if self._queue_sys and (self._sys_budget > 0 or not self._queue_user):
                q = self._queue_sys
                self._sys_budget -= 1
            elif self._queue_user:
                q = self._queue_user
                self._sys_budget = self.SYS_RATIO_NUM
            if q is None:
                break
            sid, blob, end_stream = q.popleft()
            self._quic.send_stream_data(sid, blob, end_stream=end_stream)
        self.transmit()
        self._activity()

    # ─────────────────────────────────────────── public API ─┤
    async def ensure_sys_stream(self):
        if self._sys_stream_id is None:
            self._sys_stream_id = self._quic.get_next_available_stream_id()
            self._enqueue(self._sys_stream_id, b"", False, True)  # dummy
            self._schedule_flush()

    async def send_sys(self, request: GNRequest, response: bool = False) -> Optional[bytes]:
        await self.ensure_sys_stream()
        if response:
            msg_id = next(self._sys_id_gen)
            blob = request.serialize(2)
            payload = (
                msg_id.to_bytes(8, "little") + len(blob).to_bytes(4, "little") + blob
            )
            fut = asyncio.get_running_loop().create_future()
            self._sys_inflight[msg_id] = fut
            self._enqueue(self._sys_stream_id, payload, False, True)
            self._schedule_flush()
            return await fut
        payload = (0).to_bytes(8, "little") + request.serialize(2)
        self._enqueue(self._sys_stream_id, payload, False, True)
        self._schedule_flush()
        return None

    async def request(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]):
        if isinstance(request, GNRequest):
            blob = request.serialize(2)
            sid = self._quic.get_next_available_stream_id()
            self._enqueue(sid, blob, True, False)
            self._schedule_flush()

            
            fut = asyncio.get_running_loop().create_future()
            self._inflight[sid] = fut
            return await fut
        
        else:
            sid = self._quic.get_next_available_stream_id()
            #if sid in self._quic._streams and not self._quic._streams[sid].is_finished:

            async def _stream_sender(sid, request: AsyncGenerator[GNRequest, Any]):
                _last = None
                async for req in request:
                    _last = req
                    blob = req.serialize(2)
                    self._enqueue(sid, blob, False, False)


                    self._schedule_flush()

                    print(f'Отправлен stream запрос {req}')
                

                _last.setPayload(None)
                _last.setMethod('gn:end-stream')
                blob = _last.serialize(2)
                self._enqueue(sid, blob, True, False)
                self._schedule_flush()
            
            asyncio.create_task(_stream_sender(sid, request))

                
            fut = asyncio.get_running_loop().create_future()
            self._inflight[sid] = fut
            return await fut
    
    async def requestStream(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]) -> asyncio.Queue[GNResponse]:
        if isinstance(request, GNRequest):
            blob = request.serialize(2)
            sid = self._quic.get_next_available_stream_id()
            self._enqueue(sid, blob, False, False)
            self._schedule_flush()

            
            q = asyncio.Queue()
            self._inflight[sid] = q
            return q
            
        else:
            sid = self._quic.get_next_available_stream_id()

            async def _stream_sender(sid, request: AsyncGenerator[GNRequest, Any]):
                _last = None
                async for req in request:
                    _last = req
                    blob = req.serialize(2)
                    self._enqueue(sid, blob, False, False)


                    self._schedule_flush()

                    print(f'Отправлен stream запрос {req}')
                

                _last.setPayload(None)
                _last.setMethod('gn:end-stream')
                blob = _last.serialize(2)
                self._enqueue(sid, blob, True, False)
                self._schedule_flush()
            
            asyncio.create_task(_stream_sender(sid, request))

                
            q = asyncio.Queue()
            self._inflight[sid] = q
            return q

        

class QuicClient:
    """Обёртка‑фасад над RawQuicClient."""

    def __init__(self):
        self._quik_core: Optional[RawQuicClient] = None
        self._client_cm = None

    async def connect(self, ip: str, port: int):
        cfg = QuicConfiguration(is_client=True, alpn_protocols=["gn:backend"])
        cfg.load_verify_locations(KeyisBClient.ssl_gw_crt_path)

        self._client_cm = connect(
            ip,
            port,
            configuration=cfg,
            create_protocol=RawQuicClient,
            wait_connected=True,
        )
        self._quik_core = await self._client_cm.__aenter__()

    async def disconnect(self):
        self._quik_core.close()
        await self._quik_core.wait_closed()
        self._quik_core = None

    def syncRequest(self, request: GNRequest):
        return asyncio.get_event_loop().run_until_complete(self.asyncRequest(request))

    async def asyncRequest(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]) -> GNResponse:
        if self._quik_core is None:
            raise RuntimeError("Not connected")
        
        resp = await self._quik_core.request(request)
        return GNResponse.deserialize(resp, 2)

    async def asyncRequestStream(self, request: Union[GNRequest, AsyncGenerator[GNRequest, Any]]) -> AsyncGenerator[GNResponse, None]:
        
        if self._quik_core is None:
            raise RuntimeError("Not connected")

        queue = await self._quik_core.requestStream(request)

        while True:
            chunk = await queue.get()
            if chunk is None or chunk.command == 'gn:end-stream':
                break
            yield chunk


