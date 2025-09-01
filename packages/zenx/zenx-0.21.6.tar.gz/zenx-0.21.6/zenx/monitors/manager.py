import asyncio
from typing import Dict, List
from structlog import BoundLogger

from zenx.monitors.base import Monitor
from zenx.settings import Settings


class MonitorManager:


    def __init__(self, monitor_names: List[str], logger: BoundLogger, settings: Settings) -> None:
        self.logger = logger
        self.monitors = {name:Monitor.get_monitor(name)(logger, settings) for name in monitor_names}
        self.settings = settings
        self._background_tasks = set()

    
    async def open_monitors(self) -> None:
        for monitor in self.monitors.values():
            await monitor.open()
            

    async def process_item(self, stats: Dict, producer: str) -> None:
        for monitor in self.monitors.values():
            t = asyncio.create_task(monitor.process_stats(stats, producer))
            self._background_tasks.add(t)
            t.add_done_callback(self._background_tasks.discard)

    
    async def close_monitors(self) -> None:
        if self._background_tasks:
            self.logger.debug("waiting", background_tasks=len(self._background_tasks), belong_to="monitor_manager")
            await asyncio.gather(*self._background_tasks)
        for monitor in self.monitors.values():
            await monitor.close()
