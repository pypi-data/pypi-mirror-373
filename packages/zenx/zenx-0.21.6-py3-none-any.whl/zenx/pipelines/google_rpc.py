import asyncio
import random
import importlib
import json
from typing import Any, Dict, Optional
import structlog
from google.protobuf.json_format import MessageToDict


from zenx.pipelines.base import Pipeline
from zenx.clients.database import DBClient
from zenx.settings import Settings
from zenx.utils import log_processing_time



def create_pipeline_proxy(pipeline_name: str) -> type:
    class ProxyPipeline(Pipeline):
        name = pipeline_name
        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[grpc]'"
        )

        def __init__(self, *args, **kwargs):
            raise ImportError(self._ERROR_MESSAGE)

        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def send(self, payload: Any) -> None: pass
        async def close(self) -> None: pass

    return ProxyPipeline


try:
    import grpc

    class BasegRPCPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "base_grpc"
        grpc_server_uri: str
        grpc_token: str
        grpc_id: str


        def __init__(self, logger: structlog.BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._uri = getattr(self.settings, self.grpc_server_uri)
            self._feed_token = getattr(self.settings, self.grpc_token)
            self._feed_id = getattr(self.settings, self.grpc_id)
            self._feed_pb2 = importlib.import_module("zenx.resources.proto.feed_pb2")
            self._feed_pb2_grpc = importlib.import_module("zenx.resources.proto.feed_pb2_grpc")

            self._channel = grpc.aio.secure_channel(self._uri, grpc.ssl_channel_credentials())
            self._stub = self._feed_pb2_grpc.IngressServiceStub(self._channel)
            self._connected = asyncio.Event()
            self._monitor_state_task: Optional[asyncio.Task] = None


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
                state = self._channel.get_state()
                self._monitor_state_task = asyncio.create_task(self._monitor_state(state))


        async def _monitor_state(self, ready_state: grpc.ChannelConnectivity) -> None:
            while True:
                await self._channel.wait_for_state_change(ready_state)
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._channel.get_state(try_to_connect=True)
            await self._channel.channel_ready()
            self.logger.info("connected", pipeline=self.name)
            self._connected.set()


        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            _item = {k: v for k, v in item.items() if not k.startswith("_")}
            feed_message = self._feed_pb2.FeedMessage(
                token=self._feed_token,
                feedId=self._feed_id,
                messageId=item['_id'],
                message=json.dumps(_item),
            )
            await self.send(feed_message)
            return item
        

        async def send(self, payload: Any) -> None:
            await self._connected.wait()
            try:
                grpc_response = await self._stub.SubmitFeedMessage(payload)
                self.logger.debug(
                    "response",
                    body=MessageToDict(grpc_response),
                    feed=self._feed_id,
                    pipeline=self.name
                )
            except grpc.aio.AioRpcError as e:
                self.logger.error("processing", exception=str(e), payload=MessageToDict(payload), feed=self._feed_id, pipeline=self.name)
            

        async def close(self) -> None:
            if self._monitor_state_task and not self._monitor_state_task.done():
                self._monitor_state_task.cancel()
                try:
                    await self._monitor_state_task
                except asyncio.CancelledError:
                    pass
            await self._channel.close()
            self.logger.debug("closed", pipeline=self.name)


    class SynopticgRPCPipeline(BasegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc"
        required_settings = ["SYNOPTIC_GRPC_SERVER_URI", "SYNOPTIC_GRPC_TOKEN", "SYNOPTIC_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_GRPC_ID"


except ModuleNotFoundError:
    SynopticgRPCPipeline = create_pipeline_proxy("synoptic_grpc")




try:
    import grpc

    class BaseEnterprisegRPCPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "base_enterprise_grpc"
        grpc_server_uri: str
        grpc_token: str
        grpc_id: str


        def __init__(self, logger: structlog.BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._uri = getattr(self.settings, self.grpc_server_uri)
            self._feed_token = getattr(self.settings, self.grpc_token)
            self._feed_id = getattr(self.settings, self.grpc_id)
            self._feed_pb2 = importlib.import_module("zenx.resources.enterprise.proto.PublisherMessageService_pb2")
            self._feed_pb2_grpc = importlib.import_module("zenx.resources.enterprise.proto.PublisherMessageService_pb2_grpc")

            self._channel = grpc.aio.insecure_channel(self._uri)
            self._stub = self._feed_pb2_grpc.PublisherMessageServiceStub(self._channel)
            self._connected = asyncio.Event()
            self._monitor_state_task: Optional[asyncio.Task] = None


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
                state = self._channel.get_state()
                self._monitor_state_task = asyncio.create_task(self._monitor_state(state))


        async def _monitor_state(self, ready_state: grpc.ChannelConnectivity) -> None:
            while True:
                await self._channel.wait_for_state_change(ready_state)
                try:
                    await self._connect()
                except Exception:
                    await asyncio.sleep(0.5)


        async def _connect(self) -> None:
            self._connected.clear()
            self.logger.debug("connecting", pipeline=self.name)
            self._channel.get_state(try_to_connect=True)
            await self._channel.channel_ready()
            self.logger.info("connected", pipeline=self.name)
            self._connected.set()


        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            _item = {k: v for k, v in item.items() if not k.startswith("_")}
            feed_message = self._feed_pb2.StreamPost(
                text=json.dumps(_item),
                streamId=self._feed_id,
                idempotencyKey=item['_id'],
            )
            await self.send(feed_message)
            return item
        

        async def send(self, payload: Any) -> None:
            await self._connected.wait()
            try:
                grpc_response = await self._stub.AddStreamPost(payload, metadata=[('x-api-key', self._feed_token)])
                self.logger.debug(
                    "response",
                    body=MessageToDict(grpc_response),
                    feed=self._feed_id,
                    pipeline=self.name
                )
            except grpc.aio.AioRpcError as e:
                self.logger.error("processing", exception=str(e), payload=MessageToDict(payload), feed=self._feed_id, pipeline=self.name)


        async def close(self) -> None:
            if self._monitor_state_task and not self._monitor_state_task.done():
                self._monitor_state_task.cancel()
                try:
                    await self._monitor_state_task
                except asyncio.CancelledError:
                    pass
            await self._channel.close()
            self.logger.debug("closed", pipeline=self.name)


    class SynopticgRPCEnterprisePipeline1(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_useast1"
        required_settings = ["SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

    class SynopticgRPCEnterprisePipeline2(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_eucentral1"
        required_settings = ["SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

    class SynopticgRPCEnterprisePipeline3(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_euwest2"
        required_settings = ["SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

    class SynopticgRPCEnterprisePipeline4(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_useast1chi2a"
        required_settings = ["SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

    class SynopticgRPCEnterprisePipeline5(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_useast1nyc2a"
        required_settings = ["SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

    class SynopticgRPCEnterprisePipeline6(BaseEnterprisegRPCPipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_grpc_apnortheast1"
        required_settings = ["SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI", "SYNOPTIC_ENTERPRISE_GRPC_TOKEN", "SYNOPTIC_ENTERPRISE_GRPC_ID"]
        grpc_server_uri = "SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI"
        grpc_token = "SYNOPTIC_ENTERPRISE_GRPC_TOKEN"
        grpc_id = "SYNOPTIC_ENTERPRISE_GRPC_ID"

except ModuleNotFoundError:
    SynopticgRPCEnterprisePipeline1 = create_pipeline_proxy("synoptic_grpc_useast1")
    SynopticgRPCEnterprisePipeline2 = create_pipeline_proxy("synoptic_grpc_eucentral1")
    SynopticgRPCEnterprisePipeline3 = create_pipeline_proxy("synoptic_grpc_euwest2")
    SynopticgRPCEnterprisePipeline4 = create_pipeline_proxy("synoptic_grpc_useast1chi2a")
    SynopticgRPCEnterprisePipeline5 = create_pipeline_proxy("synoptic_grpc_useast1nyc2a")
    SynopticgRPCEnterprisePipeline6 = create_pipeline_proxy("synoptic_grpc_apnortheast1")

