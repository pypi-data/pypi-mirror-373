
# ZenX

A fast, efficient and minimal web scraping framework built on top of asyncio and uvloop.

## Table of Contents

- [High-Level Overview](#high-level-overview)
- [Installation](#installation)
- [Quickstart](#quickstart)
  - [1. Create a new project](#1-create-a-new-project)
  - [2. Define a spider](#2-define-a-spider)
  - [3. Run the spider](#3-run-the-spider)
  - [4. List available spiders](#4-list-available-spiders)
- [Configuration](#configuration)
- [Built-in Components](#built-in-components)
  - [HTTP Clients](#http-clients)
  - [Databases](#databases)
  - [Pipelines](#pipelines)

## High-Level Overview

The framework is composed of the following key components:

- **Spiders**: Responsible for fetching web pages and extracting data. Each spider is a class that implements `zenx.spiders.base.Spider` interface.

- **Pipelines**: Process the data extracted by spiders. Each pipeline is a class that implements `zenx.pipelines.base.Pipeline` interface. Pipelines can be used to clean, validate, store or forward data to third party services.

- **Engine**: Responsible for managing the life-cylce of spiders.

- **CLI**: Command-line interface (CLI) for managing spiders and running crawls. 

## Installation

To install ZenX, you can use pip:

```bash
pip install zenx
```

To install ZenX with all optional dependencies for built-in components (Redis, gRPC, WebSockets, Discord), you can use:

```bash
pip install 'zenx[all]'
```

Alternatively, you can install specific optional dependencies:

```bash
pip install 'zenx[redis]'   # For Redis database support
pip install 'zenx[grpc]'    # For gRPC pipeline support
pip install 'zenx[websocket]' # For WebSocket pipeline support
pip install 'zenx[discord]'  # For Discord pipeline support
```

## Quickstart

To get started with ZenX, you can create a new project and define a spider.

### 1. Create a new project

```bash
zenx startproject myproject
```

This will create a new directory called `myproject` with the following structure:

```
myproject/
└── spiders/
    └── __init__.py
```

### 2. Define a spider

Create a new file in the `myproject/spiders` directory (e.g., `myproject/spiders/myspider.py`) and define a spider:

```python
from zenx.spiders.base import Spider
from zenx.clients.http import Response

class MySpider(Spider):
    name = "myspider"
    pipelines = ["preprocess"] # multiple pipelines can be passed here

    async def crawl(self) -> None:
        response = await self.client.get("https://example.com")
        await self.process_response(response)

    async def process_response(self, response: Response) -> None:
        item = self.parse(response)
        # Asynchronously handle the pipelines processing
        self.create_task(self.pm.process_item(item, self.name))

    def parse(self, response: Response) -> Dict:
        return {
            "_id": 1,
            "title": response.xpath("//h1/text()").get(),
        }
```

### 3. Run the spider

To run the spider, use the `crawl` command:

```bash
zenx crawl myspider
```

This will run the `myspider` spider and print the extracted data to the console.

#### Running Multiple Spiders

You can run multiple spiders at once by passing their names to the `crawl` command:

```bash
zenx crawl spider1 spider2
```

To run all available spiders, use the `all` keyword:

```bash
zenx crawl all
```

#### Forever Mode

ZenX can run spiders continuously in "forever mode". This is useful for long-running spiders that need to monitor websites for changes. To enable forever mode, use the `--forever` flag:

```bash
zenx crawl myspider --forever
```

### 4. List available spiders

To see a list of available spiders, use the `list` command:

```bash
 zenx list
```

## Configuration

ZenX allows for flexible configuration through environment variables or a `.env` file. Below are the key settings you can adjust to customize its behavior:

- `APP_ENV`: Specifies the application environment (e.g., `dev`, `prod`).
- `SESSION_POOL_SIZE`: Defines the number of sessions in session pool.
- `MAX_SCRAPE_DELAY`: Sets the maximum allowed delay (in seconds) between an item's publication and its scraping.
- `DQ_MAX_SIZE`: Configures the maximum size of the deque used by the in-memory database.
- `REDIS_RECORD_EXPIRY_SECONDS`: Determines how long (in seconds) records are stored in Redis before expiring.
- `DB_TYPE`: Selects the database backend to use (`memory` for in-memory, `redis` for Redis).
- `DB_NAME`: The name of the database to connect to (if applicable).
- `DB_USER`: The username for database authentication (if applicable).
- `DB_PASS`: The password for database authentication (if applicable).
- `DB_HOST`: The hostname or IP address of the database server.
- `DB_PORT`: The port number for the database server.
- `PROXY_V4`: Specifies an IPv4 proxy to be used for outgoing requests.
- `PROXY_V6`: Specifies an IPv6 proxy to be used for outgoing requests.
- `SYNOPTIC_GRPC_SERVER_URI`: The URI for the gRPC server endpoint.
- `SYNOPTIC_GRPC_TOKEN`: The authentication token for gRPC communication.
- `SYNOPTIC_GRPC_ID`: A unique identifier for gRPC messages.
- `SYNOPTIC_API_KEY`: The API key required for accessing the Synoptic API via websockets.
- `SYNOPTIC_STREAM_ID`: The stream ID for publishing data to the Synoptic API via websockets.
- `SYNOPTIC_DISCORD_WEBHOOK`: The webhook URL for sending messages to a Discord channel.

## Built-in Components

ZenX provides several pre-built components to streamline common web scraping tasks. These include HTTP clients for making requests, databases for data storage, and pipelines for processing scraped items.

### HTTP Clients

ZenX offers the following HTTP client out-of-the-box:

- **`curl_cffi`**: A client that leverages `curl-cffi` for making HTTP requests. This client is capable of impersonating various browsers, which can be useful for avoiding detection or blocks.

#### Session Usage

The client supports session management to maintain state (like cookies) across multiple requests and improve performance by reusing connections.

- **Enabling Sessions**: To use sessions for a request within your spider, set the `use_sessions=True` parameter when making a request through `self.client`:

  ```python
  response = await self.client.get("https://example.com/page1", use_sessions=True)
  ```

- **Session Pool**: The `curl_cffi` client maintains a pool of sessions. The size of this pool is controlled by the `SESSION_POOL_SIZE` environment variable. By default, each session in the pool will have a randomly assigned browser fingerprint for impersonation.

- **Important Note**: If `use_sessions` is `False` (the default), each request will be made with a new, independent session and a randomly chosen browser fingerprint. This is suitable for single, isolated requests.

### Databases

ZenX supports the following database backends:

- **`memory`**: An in-memory database that utilizes a deque for temporary data storage. This is ideal for development, testing, and scenarios where persistence is not required.
- **`redis`**: A persistent database solution using Redis. This is suitable for production environments.
  - **Dependencies**: `redis` (install with `pip install 'zenx[redis]'`)
  - **Required Settings**: `DB_HOST`, `DB_PORT`, `DB_PASS`

### Pipelines

Pipelines process items after they are scraped by spiders. ZenX includes the following built-in pipelines:

- **`preprocess`**: This pipeline pre-processes items before they proceed to other pipelines. It handles deduplication: if an item contains an `_id` field, the `preprocess` pipeline uses this field to check if the item has already been processed. If a duplicate `_id` is found, the item is dropped.
- **`synoptic_websocket`**: A pipeline designed to send processed items to the Synoptic API via a WebSocket connection. It requires the item to contain a `_content` field, which should hold the pre-formatted message intended for the Synoptic server.
  - **Dependencies**: `websockets` (install with `pip install 'zenx[websocket]'`)
  - **Required Settings**: `SYNOPTIC_API_KEY`, `SYNOPTIC_STREAM_ID`
- **`synoptic_grpc`**: This pipeline sends items to the Synoptic API using a gRPC connection. 
  - **Dependencies**: `grpcio` (install with `pip install 'zenx[grpc]'`)
  - **Required Settings**: `SYNOPTIC_GRPC_SERVER_URI`, `SYNOPTIC_GRPC_TOKEN`, `SYNOPTIC_GRPC_ID`
- **`synoptic_discord`**: A pipeline for sending items to a Discord webhook. This is useful for notifications or logging scraped data to a Discord channel.
  - **Dependencies**: `httpx` (install with `pip install 'zenx[discord]'`)
  - **Required Settings**: `SYNOPTIC_DISCORD_WEBHOOK`
