import asyncio
from typing import Dict, List
from structlog import BoundLogger

from zenx.exceptions import DropItem
from zenx.pipelines.base import Pipeline
from zenx.clients.database import DBClient
from zenx.settings import Settings


class PipelineManager:


    def __init__(self, pipeline_names: List[str], logger: BoundLogger, db: DBClient, settings: Settings) -> None:
        self.logger = logger
        self.pipelines = {name:Pipeline.get_pipeline(name)(logger, db, settings) for name in pipeline_names}
        self.settings = settings
        self._fire_and_forget_pipelines = [p for p in self.pipelines.values() if p.name != "preprocess"]
        self._background_tasks = set()

    
    async def open_pipelines(self) -> None:
        for pipeline in self.pipelines.values():
            await pipeline.open()
            

    async def process_item(self, item: Dict, producer: str) -> None:
        preprocess_pipeline = self.pipelines.get("preprocess")
        if preprocess_pipeline:
            try:
                item = await preprocess_pipeline.process_item(item, producer)
            except DropItem:
                self.logger.debug("dropped", id=item.get("_id"), pipeline=preprocess_pipeline.name)
                return
            except Exception:
                self.logger.exception("process_item", item=item, pipeline=preprocess_pipeline.name)
                raise
        for pipeline in self._fire_and_forget_pipelines:
            t = asyncio.create_task(pipeline.process_item(item, producer))
            self._background_tasks.add(t)
            t.add_done_callback(self._background_tasks.discard)

    
    async def close_pipelines(self) -> None:
        if self._background_tasks:
            self.logger.debug("waiting", background_tasks=len(self._background_tasks), belong_to="pipeline_manager")
            await asyncio.gather(*self._background_tasks)
        for pipeline in self.pipelines.values():
            await pipeline.close()
