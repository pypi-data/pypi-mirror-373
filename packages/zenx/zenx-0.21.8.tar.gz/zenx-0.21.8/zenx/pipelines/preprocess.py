from typing import Any, Dict

from zenx.pipelines.base import Pipeline
from zenx.exceptions import DropItem
from zenx.utils import log_processing_time



class PreprocessPipeline(Pipeline):
    name = "preprocess"
    required_settings = []


    async def open(self) -> None: 
        pass 
    
    
    @log_processing_time
    async def process_item(self, item: Dict, producer: str) -> Dict:
        self.drop_if_scraped_too_late(item)
        _id = item.get("_id")
        if _id:
            inserted = await self.db.insert(_id, producer)
            if not inserted:
                raise DropItem

        if "scraped_at" in item and "responded_at" in item:
            scraped_time = item['scraped_at'] - item['responded_at']
            self.logger.info("scraped", id=item.get("_id"), item=item, time_ms=scraped_time)
        else:
            self.logger.info("scraped", id=item.get("_id"), item=item)
            
        return item
    

    async def send(self, payload: Any) -> None:
        pass


    async def close(self) -> None: 
        pass
