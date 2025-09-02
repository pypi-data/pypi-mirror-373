import asyncio
import json
import random
from typing import Any, Dict, Optional
from structlog import BoundLogger

from zenx.clients.database import DBClient
from zenx.settings import Settings
from zenx.pipelines.base import Pipeline
from zenx.utils import log_processing_time



def create_pipeline_proxy(pipeline_name: str) -> type:
    class ProxyPipeline(Pipeline):
        name = pipeline_name
        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[websocket]'"
        )

        def __init__(self, *args, **kwargs):
            raise ImportError(self._ERROR_MESSAGE)

        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def send(self, payload: Any) -> None: pass
        async def close(self) -> None: pass

    return ProxyPipeline


try:
    import websockets
    from websockets import ConnectionClosed

    class BaseWebsocketPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "base_websocket"
        ws_stream_api_key: str
        ws_stream_id: str
        

        def __init__(self, logger: BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._api_key = getattr(self.settings, self.ws_stream_api_key)
            self._stream_id = getattr(self.settings, self.ws_stream_id)
            self._endpoint = f"wss://api.synoptic.com/v1/ws?apiKey={self._api_key}"
            self._connected = asyncio.Event()
            self._ws_client: Optional[websockets.ClientConnection] = None
            self._monitor_state_task: Optional[asyncio.Task] = None
            self._listening_task: Optional[asyncio.Task] = None


        async def open(self) -> None:
            for setting in self.required_settings:
                if not getattr(self.settings, setting):
                    raise ValueError(f"Missing required setting for pipeline '{self.name}': {setting}")
            try:
                await self._connect()
            except Exception:
                self.logger.exception("pipeline_open_failed", pipeline=self.name)
                raise
            else:
                self._monitor_state_task = asyncio.create_task(self._monitor_state())
                self._listening_task = asyncio.create_task(self._listen())

        
        async def _monitor_state(self) -> None:
            while True:
                await self._ws_client.wait_closed()
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)
                

        async def _listen(self) -> None:
            try:
                await self._connected.wait()
                self.logger.debug("listening", pipeline=self.name)
                async for msg in self._ws_client:
                    self.logger.debug("response", msg=msg, pipeline=self.name)
            except Exception:
                await asyncio.sleep(1)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._ws_client = await websockets.connect(self._endpoint) 
            msg = json.loads(await self._ws_client.recv())['data']['message']
            if "Invalid secret key" in msg:
                raise Exception(msg)
            self.logger.info("connected", pipeline=self.name, msg=msg)
            self._connected.set()

            
        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            _item = {
                "event": "add-stream-post",
                "data": {
                    "id": item.get("_id"),
                    "idempotencyKey": item.get("_id"),
                    "streamId": self._stream_id,
                    "content": json.dumps({k: v for k, v in item.items() if not k.startswith("_")}),
                    "createdAt": item.get("published_at"),
                },
            }
            await self.send(_item)
            return item
        

        async def send(self, payload: Dict) -> None:
            await self._connected.wait()
            try:
                await self._ws_client.send(json.dumps(payload))
            except ConnectionClosed as e:
                self.logger.error("processing", exception=str(e), payload=payload, pipeline=self.name)


        async def close(self) -> None:
            for t in [self._monitor_state_task, self._listening_task]:
                if t and not t.done():
                    t.cancel()
                    try:
                        await t
                    except asyncio.CancelledError:
                        pass
            await self._ws_client.close()
            self.logger.debug("closed", pipeline=self.name)


    class SynopticWebsocketPipeline(BaseWebsocketPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_websocket"
        required_settings = ["SYNOPTIC_WS_API_KEY", "SYNOPTIC_WS_STREAM_ID"]
        ws_stream_api_key = "SYNOPTIC_WS_API_KEY"
        ws_stream_id = "SYNOPTIC_WS_STREAM_ID"

    class SynopticFreeWebsocketPipeline(BaseWebsocketPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_free_websocket"
        required_settings = ["SYNOPTIC_FREE_WS_API_KEY", "SYNOPTIC_FREE_WS_STREAM_ID"]
        ws_stream_api_key = "SYNOPTIC_FREE_WS_API_KEY"
        ws_stream_id = "SYNOPTIC_FREE_WS_STREAM_ID"

        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            await asyncio.sleep(random.uniform(0.5, 1.0))  # Simulate processing delay
            item = await super().process_item(item, producer)
            return item

except ModuleNotFoundError:
    # proxy pattern
    SynopticWebsocketPipeline = create_pipeline_proxy("synoptic_websocket")
    SynopticFreeWebsocketPipeline = create_pipeline_proxy("synoptic_free_websocket")