import asyncio
import time
import uuid
from typing import Dict
import functools


def get_time() -> int:
    """ current unix time in milliseconds """
    return int(time.time() * 1000)


def log_processing_time(func):
    @functools.wraps(func)
    async def wrapper(self, item: Dict, producer: str, *args, **kwargs) -> Dict:
        start_time = get_time()
        result = await func(self, item, producer, *args, **kwargs)
        end_time = get_time()
        processed_time = end_time - start_time    
        self.logger.info("processed", id=item['_id'], time_ms=processed_time, pipeline=self.name, started_at=start_time, finished_at=end_time)
        return result
    return wrapper


def get_uuid() -> str:
    return uuid.uuid4().hex


async def cancel_task(t: asyncio.Task) -> None:
    if t and not t.done():
        t.cancel()
        try:
            await t
        except asyncio.CancelledError:
            pass
