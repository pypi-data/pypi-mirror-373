## ZenX

Minimal async framework for scraping and streaming data into pluggable pipelines. It provides:

- **Spiders**: short-lived async scrapers producing items
- **Listeners**: long-running async consumers producing messages
- **Pipelines**: post-processing and delivery (preprocess, gRPC, WebSocket, Discord)
- **Clients**: HTTP client (curl-cffi) and DB clients (in-memory, Redis) for deduplication
- **Engine**: orchestrates settings, logging, concurrency, and lifecycle
- **CLI**: project scaffolding and execution with `typer`

Everything below is derived from the codebase (no assumptions).

### Requirements

- Python >= 3.12

### Install

Basic install (published package):

```bash
uv pip install zenx
```

Optional extras (enable additional pipelines/clients):

```bash
# choose what you need
uv pip install 'zenx[redis]'
uv pip install 'zenx[grpc]'
uv pip install 'zenx[websocket]'
uv pip install 'zenx[itxp]'

# or everything
uv pip install 'zenx[all]'
```

Development (editable) install from a local clone:

```bash
uv pip install -e .
# with extras, for example
uv pip install -e '.[grpc]'
```

### CLI

ZenX exposes a CLI via `zenx.cli:app`.

```bash
zenx list
zenx crawl <spider> [--forever]
zenx crawl all [--forever]
zenx crawl <spider1> <spider2> ... [--forever]
zenx listen <listener>
zenx startproject <project_name>
```

- `list`: shows registered spiders, listeners and active built-in pipelines
- `crawl`: runs one or more spiders
  - `--forever`: schedules `crawl()` at fixed intervals with configured concurrency
- `listen`: runs a listener
- `startproject`: scaffolds a project (see Project layout)

### Project layout and dynamic discovery

`zenx startproject myproj` creates the following (relative to current directory):

```
./myproj/
  ├─ spiders/__init__.py
  └─ listeners/__init__.py
./zenx.toml             # project = "myproj"
./.gitignore            # from zenx.resources.gitignore
./.env.example          # from zenx.resources.env_example
```

On each CLI invocation, ZenX loads `zenx.toml` and dynamically imports `spiders`, `listeners`, and `pipelines` from `project = "..."`. Place your custom components inside `myproj/spiders`, `myproj/listeners`, or `myproj/pipelines` and they will be auto-registered.

### Configuration (environment)

All settings come from `zenx.settings.Settings` (pydantic-settings). A `.env` file is automatically discovered via `dotenv` (see `.env.example`). Key fields:

- General: `APP_ENV` ("dev"/"prod"), `LOG_LEVEL`
- Scheduling: `CONCURRENCY`, `TASK_INTERVAL_SECONDS`, `START_OFFSET_SECONDS`
- Scrape rules: `MAX_SCRAPE_DELAY`
- HTTP: `PROXY`, `SESSION_POOL_SIZE`
- DB: `DB_TYPE` ("memory"|"redis"), `DQ_MAX_SIZE`, `REDIS_RECORD_EXPIRY_SECONDS`, `DB_HOST`, `DB_PORT`, `DB_PASS`
- Pipelines (examples):
  - gRPC: `SYNOPTIC_GRPC_SERVER_URI`, `SYNOPTIC_GRPC_TOKEN`, `SYNOPTIC_GRPC_ID`
  - Enterprise gRPC (per region): `SYNOPTIC_ENTERPRISE_*`
  - WebSocket: `SYNOPTIC_WS_API_KEY`, `SYNOPTIC_WS_STREAM_ID`
  - Free WebSocket: `SYNOPTIC_FREE_WS_API_KEY`, `SYNOPTIC_FREE_WS_STREAM_ID`
  - Discord: `SYNOPTIC_DISCORD_WEBHOOK`
  - Monitoring: `MONITOR_ITXP_TOKEN`, `MONITOR_ITXP_URI`

Copy `.env.example` to `.env` and fill in as needed.

### Logging

Structured logging via `structlog`:

- `APP_ENV=dev`: human-friendly console rendering
- `APP_ENV=prod`: JSON logs to `./logs/<spider|listener>.log`

### Execution model

Engine (`zenx.engine.Engine`) handles lifecycle:

- Loads settings and logger per spider/listener
- Instantiates HTTP and DB clients
- Opens pipelines before work, closes them on shutdown
- For spiders:
  - `--forever`: schedules `crawl()` at `TASK_INTERVAL_SECONDS`, staggering across `CONCURRENCY`
  - `dev` env: limits active pipelines to `preprocess` only (others disabled)
- For listeners:
  - `listen()` runs until cancelled; same pipeline behavior as spiders

Graceful shutdown waits for background tasks and closes resources.

### Built-in components

Spiders/Listeners are discovered dynamically. The base classes provide central registries and simple APIs.

#### Spider base (`zenx.spiders.base.Spider`)

Implement:

- Class attributes:
  - `name: str` (unique registry key)
  - `pipelines: list[str]` (e.g., `["preprocess", "synoptic_grpc"]`)
  - Optional: `client_name = "curl_cffi"`, `custom_settings = { ... }`
- Methods:
  - `async def crawl(self) -> None`: produce responses and call `process_response`
  - `async def process_response(self, response: Response) -> None`: parse and push items into pipelines

Helper methods:

- `extract_text(html)` for HTML-to-text
- `create_task(coro, name=None)` to track background tasks

HTTP client response offers `json()`, `selector/xpath()`, `urljoin()`.

#### Listener base (`zenx.listeners.base.Listener`)

Implement:

- Class attributes:
  - `name: str` (unique)
  - `pipelines: list[str]` (e.g., `["preprocess", "synoptic_websocket"]`)
  - Optional: `custom_settings = { ... }`
- Methods:
  - `async def listen(self) -> None`: long-running loop producing `Message`
  - `async def process_message(self, message: Message) -> None`: parse and push items into pipelines

#### Pipelines (`zenx.pipelines.*`)

All pipelines subclass `Pipeline` and are auto-registered. The `PipelineManager` runs `preprocess` first, then fans out to remaining pipelines concurrently (fire-and-forget).

- `preprocess.PreprocessPipeline` (always recommended first)
  - Deduplicates using the configured DB client if item has `_id`
  - Drops too-late items based on `MAX_SCRAPE_DELAY`
  - Logs processing time and item metadata

- gRPC pipelines (`uv pip install 'zenx[grpc]'`):
  - `google_rpc.SynopticgRPCPipeline`
  - Enterprise variants per region: `synoptic_grpc_useast1`, `synoptic_grpc_eucentral1`, `synoptic_grpc_euwest2`, `synoptic_grpc_useast1chi2a`, `synoptic_grpc_useast1nyc2a`, `synoptic_grpc_apnortheast1`
  - Convert items to Protobuf messages and call the remote service asynchronously with automatic reconnect

- WebSocket pipelines (`uv pip install 'zenx[websocket]'`):
  - `websocket.SynopticWebsocketPipeline`
  - `websocket.SynopticFreeWebsocketPipeline`
  - Maintain a persistent WS connection and send stream posts

- Discord pipeline (uses `httpx`, included in base deps):
  - `discord.SynopticDiscordPipeline`
  - Posts JSON-rendered items to a Discord webhook

All pipelines implement: `open()`, `process_item(item, producer)`, `send(payload)`, and `close()`.

#### Clients

- HTTP (`zenx.clients.http.CurlCffiClient`):
  - Session pool with rotating browser fingerprints (`curl-cffi` impersonation)
  - `request(url, method="GET", headers=None, proxy=None, use_session_pool=False, **kwargs)` → `Response`
  - `Response` provides `json()`, `selector/xpath()`, `urljoin()` and timing metadata

- DB (`zenx.clients.database`):
  - `MemoryDB` (in-memory deque), `RedisDB` (requires `redis` extra)
  - Both expose `insert(id, producer)` returning `True` if new (used for dedup), and `exists(...)`

#### Monitors

Monitoring primitives live under `zenx.monitors`:

- `ItxpMonitor` (`uv pip install 'zenx[itxp]'`): posts system stats and success heartbeats to a configured endpoint

Note: Monitors are provided with a `MonitorManager`, ready for integration in custom flows.

### Minimal examples

Create a project and a simple spider:

```bash
zenx startproject myproj
cp .env.example .env
```

Create `myproj/spiders/example.py`:

```python
from zenx.spiders import Spider
from zenx.clients.http import Response

class ExampleSpider(Spider):
    name = "example"
    pipelines = ["preprocess"]  # add other pipelines as needed

    async def crawl(self) -> None:
        resp = await self.client.request("https://httpbin.org/json", use_session_pool=True)
        await self.process_response(resp)

    async def process_response(self, response: Response) -> None:
        item = {
            "_id": response.url,  # for dedup
            "published_at": response.requested_at,
            "scraped_at": response.responded_at,
            "title": response.json().get("slideshow", {}).get("title"),
        }
        await self.pm.process_item(item, producer=self.name)
```

Run it:

```bash
zenx list
zenx crawl example

# schedule forever with concurrency 2 (set in .env)
zenx crawl example --forever
```

Listener skeleton (create `myproj/listeners/example_listener.py`):

```python
from zenx.listeners import Listener, Message

class ExampleListener(Listener):
    name = "example_listener"
    pipelines = ["preprocess"]

    async def listen(self) -> None:
        await self.process_message(Message(text="hello world"))

    async def process_message(self, message: Message) -> None:
        item = {"_id": "msg-1", "published_at": 0, "scraped_at": 0, "text": message.text}
        await self.pm.process_item(item, producer=self.name)
```

```bash
zenx listen example_listener
```

### Programmatic usage and debugging

- Programmatic run:

```python
from zenx.engine import Engine
from zenx.discovery import discover_local_module

discover_local_module("spiders")
Engine(forever=False).run_spider("example")
```

- Debug runner:

```bash
python -m zenx.debug_runner example
```

### Notes

- In `APP_ENV=dev`, only the `preprocess` pipeline is kept active automatically for safety.
- For Redis, ensure `DB_HOST` and `DB_PORT` are set; records expire after `REDIS_RECORD_EXPIRY_SECONDS`.
- Pipelines using optional dependencies raise clear ImportError messages if the extra is not installed.


