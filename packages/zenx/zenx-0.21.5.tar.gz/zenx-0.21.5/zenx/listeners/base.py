from __future__ import annotations 
import asyncio
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Coroutine, Dict, List, Literal, Optional, Type
from structlog import BoundLogger
from dataclasses import dataclass

from zenx.pipelines.manager import PipelineManager
from zenx.settings import Settings


@dataclass
class Message:
    text: str


class Listener(ABC):
    # central registry
    name: ClassVar[str]
    _registry: ClassVar[Dict[str, Type[Listener]]] = {}
    pipelines: ClassVar[List[Literal["preprocess","synoptic_websocket","synoptic_grpc","synoptic_discord"]]]
    custom_settings: ClassVar[Dict[str, Any]] = {}


    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"Listener subclass {cls.__name__} must have a 'name' attribute.")

        cls._registry[cls.name] = cls


    @classmethod
    def get_listener(cls, name: str) -> Type[Listener]:
        if name not in cls._registry:
            raise ValueError(f"Listener '{name}' is not registered. Available listeners: {list(cls._registry.keys())}")
        return cls._registry[name]


    @classmethod
    def listener_list(cls) -> List[str]:
        return list(cls._registry.keys())


    def __init__(self, pm: PipelineManager, logger: BoundLogger, settings: Settings) -> None:
        self.pm = pm
        self.logger = logger
        self.settings = settings
        self.background_tasks = set()

    
    def create_task(self, coro: Coroutine, name: Optional[str] = None) -> None:
        t = asyncio.create_task(coro, name=name)
        self.background_tasks.add(t)
        t.add_done_callback(self.background_tasks.discard)
    

    @abstractmethod
    async def listen(self) -> None:
        """ Long-running process """
        ...


    @abstractmethod
    async def process_message(self, message: Message) -> None:
        ...
