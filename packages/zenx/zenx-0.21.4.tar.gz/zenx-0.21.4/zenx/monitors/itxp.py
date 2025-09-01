from structlog import BoundLogger
import socket
from typing import Dict
import httpx
from datetime import datetime, timezone

from zenx.settings import Settings
from zenx.monitors.base import Monitor


try:
    import psutil


    class ItxpMonitor(Monitor): # type: ignore[reportRedeclaration]
        name = "itxp"
        required_settings = ["MONITOR_ITXP_TOKEN"]


        def __init__(self, logger: BoundLogger, settings: Settings) -> None:
            super().__init__(logger, settings)
            self._token = self.settings.MONITOR_ITXP_TOKEN
            self._uri = self.settings.MONITOR_ITXP_URI
            self._client = httpx.AsyncClient()


        @staticmethod
        def _get_system_info() -> Dict:
            return {
                "cpu_percent_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "disk_percent": psutil.disk_usage('/').percent,
                "ram_percent": psutil.virtual_memory().percent,
                "swap_percent": psutil.swap_memory().percent
            }


        async def open(self) -> None:
            pass 


        async def process_stats(self, stats: Dict, producer: str) -> None:
            system_info = self._get_system_info()
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
            payload = {
                "hostname": socket.gethostname(),
                "timestamp": timestamp,
                "apps": {producer: {"last_success": timestamp}},
                **system_info,
            }
            try:
                await self._client.post(self._uri, json=payload, headers={"Authorization": f"Bearer {self._token}"})
            except Exception as e:
                self.logger.error("processing", exception=str(e), monitor=self.name)


        async def close(self) -> None:
            await self._client.aclose()

except ModuleNotFoundError:
    # proxy pattern
    class ItxpMonitor(Monitor):
        name = "itxp"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[itxp]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def process_stats(self, stats: Dict, producer: str) -> None: pass
        async def close(self) -> None: pass
