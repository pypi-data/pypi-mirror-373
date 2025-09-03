from typing import Any, Dict
import json
from structlog import BoundLogger

from zenx.pipelines.base import Pipeline
from zenx.clients.database import DBClient
from zenx.settings import Settings
from zenx.utils import log_processing_time


try: 
    from httpx import AsyncClient

    class SynopticDiscordPipeline(Pipeline): # type: ignore[reportRedeclaration]
        name = "synoptic_discord"
        required_settings = ["SYNOPTIC_DISCORD_WEBHOOK"]
        
        
        def __init__(self, logger: BoundLogger, db: DBClient, settings: Settings) -> None:
            super().__init__(logger, db, settings)
            self._uri = settings.SYNOPTIC_DISCORD_WEBHOOK
            self._client = AsyncClient(headers={"Content-Type": "application/json"})


        async def open(self) -> None:
            for setting in self.required_settings:
                if not getattr(self.settings, setting):
                    raise ValueError(f"Missing required setting: {setting}")
        
        
        @log_processing_time
        async def process_item(self, item: Dict, producer: str) -> Dict:
            _item = {k: v for k, v in item.items() if not k.startswith("_")}
            _item['producer'] = producer
            message_content = f"```json\n{json.dumps(_item, indent=4)}\n```"
            payload = {"content": message_content}
            await self.send(payload)
            return item
        

        async def send(self, payload: Dict) -> None:
            try:
                await self._client.post(self._uri, json=payload)
            except Exception as e:
                self.logger.error("processing", exception=str(e), payload=payload, pipeline=self.name)


        async def close(self) -> None:
            if hasattr(self, "_client") and self._client:
                await self._client.aclose()

except ModuleNotFoundError:
    # proxy pattern
    class SynopticDiscordPipeline(Pipeline):
        name = "synoptic_discord"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[discord]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def process_item(self, item: Dict, producer: str) -> Dict: return {}
        async def send(self, payload: Any) -> None: pass
        async def close(self) -> None: pass
