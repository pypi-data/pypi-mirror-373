from __future__ import annotations
from parsel import Selector, SelectorList
from functools import cached_property
import random
from curl_cffi.requests.impersonate import BrowserTypeLiteral
from curl_cffi import AsyncSession, Response as CurlResponse
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Any, ClassVar, Tuple, Type, Dict, get_args
import orjson
from structlog import BoundLogger
from curl_cffi.requests.exceptions import DNSError

from zenx.settings import Settings
from zenx.utils import get_time, get_uuid

@dataclass
class SessionWrapper:
    id: str
    requests: int
    _self: AsyncSession


@dataclass
class Response:
    url: str
    status: int
    text: str
    headers: Dict
    responded_at: int
    requested_at: int
    latency_ms: int
    body: bytes | None = None

    def json(self) -> Any:
        return orjson.loads(self.text)
    
    @cached_property
    def selector(self) -> Selector:
        content_type = self.headers.get('content-type', '').lower()
        if "xml" in content_type or self.text.strip().startswith("<?xml"):
            return Selector(self.text, type='xml')
        return Selector(self.text)
    
    def xpath(self, query: str) -> SelectorList[Selector]:
        return self.selector.xpath(query)


class HttpClient(ABC):
    # central registry
    name: ClassVar[str]
    _registry: ClassVar[Dict[str, Type[HttpClient]]] = {}
    

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"HttpClient subclass {cls.__name__} must have a 'name' attribute.")
        cls._registry[cls.name] = cls


    @classmethod
    def get_client(cls, name: str) -> Type[HttpClient]:
        if name not in cls._registry:
            raise ValueError(f"HttpClient '{name}' is not registered. Available http clients: {list(cls._registry.keys())}")
        return cls._registry[name]
    

    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        self.logger = logger
        self.settings = settings
        self._session_pool: asyncio.Queue[SessionWrapper]
    
    
    @abstractmethod
    async def request(
        self,
        url: str,
        method: str = "GET",
        headers: Dict | None = None,
        proxy: str | None = None,
        use_session_pool: bool = False,
        **kwargs,
    ) -> Response:
        ...
    

    @abstractmethod
    async def close(self) -> None:
        ...



class CurlCffiClient(HttpClient):
    name = "curl_cffi"


    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        super().__init__(logger, settings)
        self._fingerprints: Tuple[str] = get_args(BrowserTypeLiteral)
        self._session_pool = asyncio.Queue(maxsize=settings.SESSION_POOL_SIZE)
        self._fill_session_pool()
        

    def _fill_session_pool(self) -> None:
        for _ in range(self.settings.SESSION_POOL_SIZE):
            impersonate = self._get_random_fingerprint()
            obj = SessionWrapper(id=get_uuid(), requests=0, _self=AsyncSession(max_clients=1, impersonate=impersonate))
            self._session_pool.put_nowait(obj)
        self.logger.debug("created", sessions=self._session_pool.qsize(), client=self.name)


    def _get_random_fingerprint(self) -> str:
        chosen_fingerprint = random.choice(self._fingerprints) 
        return chosen_fingerprint
    
    
    async def _replace_session(self, existing_session: SessionWrapper) -> None:
        await existing_session._self.close()
        obj = SessionWrapper(id=get_uuid(), requests=0, _self=AsyncSession(max_clients=1, impersonate=self._get_random_fingerprint()))
        self._session_pool.put_nowait(obj)
        self.logger.debug("replaced", old_session=existing_session.id, new_session=obj.id, client=self.name)


    def create_session(self, impersonate: str = "chrome", **kwargs) -> AsyncSession:
        if impersonate == "random":
            impersonate = self._get_random_fingerprint()
        session = AsyncSession(max_clients=1, impersonate=impersonate, **kwargs)
        self.logger.debug("created", impersonate=session.impersonate, client=self.name)
        return session


    async def request(
        self,
        url: str,
        method: str = "GET",
        headers: Dict | None = None,
        proxy: str | None = None,
        use_session_pool: bool = False,
        *,
        impersonate: str | None = None,
        session: AsyncSession | None = None,
        **kwargs,
    ) -> Response:
        if use_session_pool:
            # each session has its own fingerprint set
            kwargs.pop("impersonate", None)
            session_wrapper = await self._session_pool.get()
            try:
                req_at = get_time()
                response: CurlResponse = await asyncio.wait_for(session_wrapper._self.request(
                    url=url, 
                    method=method, 
                    headers=headers, 
                    proxy=proxy,
                    verify=False,
                    **kwargs,
                ), timeout=kwargs.get("timeout",20)+5)
                recv_at = get_time()
                latency = recv_at - req_at
                session_wrapper.requests +=1
                self.logger.debug("response", status=response.status_code, url=url, session_id=session_wrapper.id, requests=session_wrapper.requests, client=self.name, requested_at=req_at, responded_at=recv_at, latency_ms=latency)
            except TimeoutError:
                self.logger.error("timeout", url=url, client=self.name)
                await self._replace_session(session_wrapper)
                raise
            except DNSError:
                self.logger.error("dns_error", url=url, client=self.name)
                await self._replace_session(session_wrapper)
                raise
            except Exception:
                self.logger.error("request", url=url, client=self.name)
                await self._replace_session(session_wrapper)
                raise
            else:
                if response.status_code != 200:
                    await self._replace_session(session_wrapper)
                else:
                    self._session_pool.put_nowait(session_wrapper)

        elif session:
            kwargs.pop("impersonate", None)
            try:
                req_at = get_time()
                response: CurlResponse = await asyncio.wait_for(session.request(
                    url=url,
                    method=method, 
                    headers=headers, 
                    proxy=proxy,
                    verify=False,
                    **kwargs,
                ), timeout=kwargs.get("timeout",20)+5)
                recv_at = get_time()
                latency = recv_at - req_at
                self.logger.debug("response", status=response.status_code, url=url, impersonate=session.impersonate, client=self.name, requested_at=req_at, responded_at=recv_at, latency_ms=latency)
            except TimeoutError:
                self.logger.error("timeout", url=url, client=self.name)
                raise
            except DNSError:
                self.logger.error("dns_error", url=url, client=self.name)
                raise
            except Exception:
                self.logger.exception("request", url=url, client=self.name)
                raise

        else:
            if impersonate is None:
                impersonate = self._get_random_fingerprint()
            async with AsyncSession() as session:
                try:
                    req_at = get_time()
                    response: CurlResponse = await asyncio.wait_for(session.request(
                        url=url, 
                        method=method, 
                        headers=headers, 
                        proxy=proxy,
                        verify=False,
                        impersonate=impersonate,
                        **kwargs,
                    ), timeout=kwargs.get("timeout",20)+5)
                    recv_at = get_time()
                    latency = recv_at - req_at
                    self.logger.debug("response", status=response.status_code, url=url, impersonate=impersonate, client=self.name, requested_at=req_at, responded_at=recv_at, latency_ms=latency)
                except TimeoutError:
                    self.logger.error("timeout", url=url, client=self.name)
                    raise
                except DNSError:
                    self.logger.error("dns_error", url=url, client=self.name)
                    raise
                except Exception:
                    self.logger.exception("request", url=url, client=self.name)
                    raise

        return Response(
            url=response.url,
            status=response.status_code,
            text=response.text,
            headers=dict(response.headers),
            requested_at=req_at,
            responded_at=recv_at,
            latency_ms=latency,
            body=response.content,
        )
    
    
    async def close(self) -> None:
        count = self._session_pool.qsize()
        async with asyncio.TaskGroup() as tg:
            while not self._session_pool.empty():
                session_wrapper = await self._session_pool.get()
                tg.create_task(session_wrapper._self.close())
        self.logger.debug("closed", sessions=count, client=self.name)
