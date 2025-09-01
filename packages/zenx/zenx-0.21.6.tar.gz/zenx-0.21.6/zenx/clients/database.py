from __future__ import annotations
from abc import ABC, abstractmethod
import collections
from typing import ClassVar, Dict, List, Optional, Type
from structlog import BoundLogger

from zenx.settings import Settings



class DBClient(ABC):
    name: ClassVar[str]
    required_settings: ClassVar[List[str]]
    _registry: ClassVar[Dict[str, Type[DBClient]]] = {}
    

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"DBClient subclass {cls.__name__} must have a 'name' attribute.")
        cls._registry[cls.name] = cls

    
    @classmethod
    def get_db(cls, name: str) -> Type[DBClient]:
        if name not in cls._registry:
            raise ValueError(f"DBClient '{name}' is not registered. Available db clients: {list(cls._registry.keys())}")
        return cls._registry[name]

    
    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        self.logger = logger
        self.settings = settings

        
    @abstractmethod
    async def open(self) -> None:
        ...

    
    @abstractmethod
    async def _connect(self) -> None:
        ...


    @abstractmethod
    async def insert(self, id: str, producer: str) -> bool:
        ...


    @abstractmethod
    async def exists(self, id: str, producer: str) -> bool:
        ...


    @abstractmethod
    async def close(self) -> None:
        ...


class MemoryDB(DBClient):
    name = "memory"
    required_settings = []


    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        super().__init__(logger, settings)
        self.dq = collections.deque(maxlen=self.settings.DQ_MAX_SIZE)


    async def open(self) -> None:
        pass


    async def _connect(self) -> None:
        pass


    async def insert(self, id: str, producer: str) -> bool:
        unique_id = f"{producer}_{id}"
        if unique_id in self.dq:
            self.logger.debug("exists", id=unique_id, db=self.name)
            return False
        self.dq.append(unique_id)
        self.logger.debug("inserted", id=unique_id, db=self.name)
        return True


    async def exists(self, id: str, producer: str) -> bool:
        unique_id = f"{producer}_{id}"
        return unique_id in self.dq
    

    async def close(self) -> None:
        pass


try:
    import redis.asyncio as redis

    class RedisDB(DBClient): # type: ignore [reportRedeclaration]
        name = "redis"
        required_settings = ["DB_HOST", "DB_PORT"]
        
        
        def __init__(self, logger: BoundLogger, settings: Settings) -> None:
            super().__init__(logger, settings)
            self.r: Optional[redis.Redis] = None
            self._record_expiry_sec = self.settings.REDIS_RECORD_EXPIRY_SECONDS

    
        async def open(self) -> None:
            for setting in self.required_settings:
                if not getattr(self.settings, setting):
                    raise ValueError(f"Missing required setting: {setting}")
            try:
                await self._connect()
            except Exception:
                self.logger.exception("db_open_failed", db=self.name)
                raise


        async def _connect(self) -> None:
            self.logger.debug("connecting", db=self.name)
            pool = redis.ConnectionPool(
                host=self.settings.DB_HOST,
                port=self.settings.DB_PORT,
                password=self.settings.DB_PASS,
                socket_timeout=5,
                socket_connect_timeout=5,
                decode_responses=True,
            )
            self.r = redis.Redis(connection_pool=pool)
            await self.r.ping()
            self.logger.info("connected", db=self.name)


        async def insert(self, id: str, producer: str) -> bool:
            unique_id = f"{producer}_{id}"
            result = await self.r.set(unique_id, 1, ex=self._record_expiry_sec, nx=True)
            if result:
                self.logger.debug("inserted", id=unique_id, db=self.name)
                return True
            else:
                self.logger.debug("exists", id=unique_id, db=self.name)
                return False


        async def exists(self, id: str, producer: str) -> bool:
            unique_id = f"{producer}_{id}"
            return bool(await self.r.exists(unique_id))
        

        async def close(self) -> None:
            if self.r:
                await self.r.aclose()

except ModuleNotFoundError:
    # proxy pattern
    class RedisDB(DBClient):
        name = "redis"
        required_settings = []
        
        _ERROR_MESSAGE = (
            f"The '{name}' component is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[redis]'"
        )

        def __init__(self, *args, **kwargs):
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def _connect(self) -> None: pass
        async def insert(self, id: str, producer: str) -> bool: return False
        async def exists(self, id: str, producer: str) -> bool: return False
        async def close(self) -> None: pass
