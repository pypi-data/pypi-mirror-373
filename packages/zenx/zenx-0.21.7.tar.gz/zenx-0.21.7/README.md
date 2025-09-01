# ZenX Framework

> A powerful, async-first Python mini-framework for building scalable web scrapers, data pipelines, and real-time listeners

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-0.21.5-blue.svg)](pyproject.toml)

## ✨ Features

- **🕷️ Advanced Web Scraping**: Built-in HTTP clients with session pooling, fingerprinting, and proxy support
- **📡 Real-time Pipelines**: WebSocket, gRPC, and Discord integrations for instant data delivery
- **🎯 Event-driven Architecture**: Reactive listeners for processing real-time events and messages
- **⚡ Async Performance**: Leverages `uvloop` and `asyncio` for maximum concurrency
- **🔧 Plugin System**: Extensible architecture with custom spiders, pipelines, and listeners
- **📊 Built-in Monitoring**: Structured logging with `structlog` and optional performance monitoring
- **🗄️ Flexible Storage**: Support for in-memory and Redis-backed data persistence
- **🚀 Production Ready**: Robust error handling, graceful shutdowns, and configurable concurrency

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install zenx

# With all optional dependencies
pip install zenx[all]

# Specific feature sets
pip install zenx[redis,websocket,grpc]
```

### Create Your First Project

```bash
# Create a new ZenX project
zenx startproject myproject

# Navigate to your project
cd myproject/
```

### Your First Spider

Create a simple spider in `spiders/example_spider.py`:

```python
from zenx.spiders import Spider

class ExampleSpider(Spider):
    name = "example"
    pipelines = ["preprocess"]
    
    async def crawl(self):
        # Make HTTP request
        response = await self.client.request("https://httpbin.org/json")
        
        # Extract data
        data = response.json()
        
        # Process through pipelines
        item = {
            "_id": "example_1",
            "scraped_at": self.settings.current_timestamp,
            "data": data
        }
        
        await self.pm.process_item(item, producer=self.name)
        self.logger.info("Successfully scraped data", item_id=item["_id"])
```

### Run Your Spider

```bash
# Run once
zenx crawl example

# Run continuously
zenx crawl example --forever

# List available components
zenx list
```

## 📚 Core Concepts

### 🕷️ Spiders

Spiders are the core scraping components that define how to extract data from websites:

```python
from zenx.spiders import Spider

class NewsSpider(Spider):
    name = "news"
    pipelines = ["preprocess", "synoptic_websocket"]
    client_name = "curl_cffi"  # HTTP client to use
    
    # Custom settings for this spider
    custom_settings = {
        "CONCURRENCY": 3,
        "TASK_INTERVAL_SECONDS": 2.0
    }
    
    async def crawl(self):
        # Your scraping logic here
        urls = await self.get_urls_to_scrape()
        
        for url in urls:
            try:
                response = await self.client.request(url, use_session_pool=True)
                items = self.parse_response(response)
                
                for item in items:
                    await self.pm.process_item(item, producer=self.name)
                    
            except Exception as e:
                self.logger.error("Failed to process URL", url=url, error=str(e))
    
    def parse_response(self, response):
        # Extract text from HTML
        text = self.extract_text(response.text)
        
        # Return structured data
        return [{
            "_id": f"news_{hash(response.url)}",
            "url": response.url,
            "title": "...",
            "content": text,
            "scraped_at": response.recv_at,
            "published_at": "..."
        }]
```

### 🔄 Pipelines

Pipelines process and route scraped data to various destinations:

```python
from zenx.pipelines.base import Pipeline
import json

class CustomAPIPipeline(Pipeline):
    name = "custom_api"
    required_settings = ["API_ENDPOINT", "API_KEY"]
    
    async def open(self):
        """Initialize pipeline connections"""
        self.session = self.client.create_session()
    
    async def process_item(self, item, producer):
        """Process each scraped item"""
        # Validate and transform data
        if not item.get("title"):
            raise DropItem("Missing title")
            
        # Enrich with metadata
        item["processed_at"] = time.time()
        item["source"] = producer
        
        return item
    
    async def send(self, payload):
        """Send processed data to external API"""
        await self.session.post(
            self.settings.API_ENDPOINT,
            headers={"Authorization": f"Bearer {self.settings.API_KEY}"},
            json=payload
        )
    
    async def close(self):
        """Cleanup resources"""
        if hasattr(self, 'session'):
            await self.session.close()
```

### 👂 Listeners

Listeners handle real-time events and long-running processes:

```python
from zenx.listeners.base import Listener, Message

class ChatListener(Listener):
    name = "chat"
    pipelines = ["preprocess", "synoptic_discord"]
    
    async def listen(self):
        """Main listening loop"""
        while True:
            try:
                # Connect to message source (WebSocket, queue, etc.)
                async for raw_message in self.message_source():
                    message = Message(text=raw_message)
                    await self.process_message(message)
                    
            except Exception as e:
                self.logger.error("Listen loop error", error=str(e))
                await asyncio.sleep(5)  # Backoff before retry
    
    async def process_message(self, message):
        """Process individual messages"""
        # Parse and structure the message
        item = {
            "_id": f"chat_{hash(message.text)}",
            "content": message.text,
            "timestamp": time.time(),
            "type": "chat_message"
        }
        
        # Send through pipeline
        await self.pm.process_item(item, producer=self.name)
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# Application Configuration
APP_ENV="production"
LOG_LEVEL="INFO"

# Scraping Settings
CONCURRENCY="5"
TASK_INTERVAL_SECONDS="1.0"
SESSION_POOL_SIZE="10"
MAX_SCRAPE_DELAY="30.0"

# Database Configuration
DB_TYPE="redis"  # or "memory"
DB_HOST="localhost"
DB_PORT="6379"
DB_PASS="your_password"

# Proxy Configuration (optional)
PROXY="http://proxy.example.com:8080"

# Pipeline Configurations
SYNOPTIC_GRPC_TOKEN="your_token"
SYNOPTIC_GRPC_ID="your_feed_id"
SYNOPTIC_DISCORD_WEBHOOK="https://discord.com/api/webhooks/..."
```

### Custom Settings

Override settings per spider or globally:

```python
from zenx.settings import Settings

# Custom settings class
class MySettings(Settings):
    CUSTOM_TIMEOUT: int = 30
    RETRY_ATTEMPTS: int = 3
    
# Use in spider
class MySpider(Spider):
    custom_settings = {
        "CUSTOM_TIMEOUT": 60,
        "CONCURRENCY": 1
    }
```

## 🔧 Advanced Usage

### Custom HTTP Clients

Extend the HTTP client system:

```python
from zenx.clients.http import HttpClient, Response

class CustomClient(HttpClient):
    name = "custom_client"
    
    async def request(self, url, method="GET", **kwargs):
        # Custom request logic
        # Add authentication, custom headers, etc.
        return Response(...)
```

### Pipeline Composition

Chain multiple pipelines for complex data flows:

```python
class DataSpider(Spider):
    name = "data_pipeline"
    pipelines = [
        "preprocess",           # Deduplication & validation
        "custom_transform",     # Data transformation
        "synoptic_grpc",       # Real-time streaming
        "backup_storage"       # Backup to database
    ]
```

### Monitoring and Debugging

```python
# Enable detailed logging
import structlog

# Custom debug spider
class DebugSpider(Spider):
    custom_settings = {
        "LOG_LEVEL": "DEBUG",
        "SESSION_POOL_SIZE": 1
    }
    
    async def crawl(self):
        # Add performance monitoring
        start_time = time.time()
        
        # Your scraping logic
        result = await self.scrape_data()
        
        # Log performance metrics
        elapsed = time.time() - start_time
        self.logger.info("Performance", 
                        duration=elapsed, 
                        items_scraped=len(result))
```

### Background Tasks

Handle long-running operations:

```python
class BackgroundSpider(Spider):
    async def crawl(self):
        # Start background monitoring task
        self.create_task(
            self.monitor_health(),
            name="health_monitor_cancellable"
        )
        
        # Main scraping logic
        await self.main_scraping_logic()
    
    async def monitor_health(self):
        """Long-running background task"""
        while True:
            # Health check logic
            await asyncio.sleep(30)
```

## 📖 API Reference

### Spider API

| Method | Description |
|--------|-------------|
| `crawl()` | Main scraping method (abstract) |
| `extract_text(html)` | Extract clean text from HTML |
| `create_task(coro)` | Create managed background task |
| `client.request()` | Make HTTP requests |
| `pm.process_item()` | Send item through pipelines |

### Pipeline API

| Method | Description |
|--------|-------------|
| `open()` | Initialize pipeline (abstract) |
| `process_item()` | Process scraped item (abstract) |
| `send()` | Send data to destination (abstract) |
| `close()` | Cleanup resources (abstract) |
| `drop_if_scraped_too_late()` | Utility for filtering old items |

### Listener API

| Method | Description |
|--------|-------------|
| `listen()` | Main listening loop (abstract) |
| `process_message()` | Handle individual messages (abstract) |
| `create_task()` | Create managed background task |
| `pm.process_item()` | Send item through pipelines |

## 🎯 Built-in Pipelines

### Available Pipelines

- **`preprocess`**: Deduplication and basic validation
- **`synoptic_websocket`**: Stream to Synoptic WebSocket API
- **`synoptic_grpc`**: Stream to Synoptic gRPC service
- **`synoptic_discord`**: Send notifications to Discord webhooks

### Pipeline Configuration

```python
# Multiple regions for gRPC
pipelines = [
    "preprocess",
    "synoptic_grpc_useast1",     # US East
    "synoptic_grpc_eucentral1",  # EU Central
    "synoptic_grpc_useast1chi2a" # Chicago
]
```

## 🛠️ CLI Commands

### Basic Commands

```bash
# List all available components
zenx list

# Run single spider
zenx crawl spider_name

# Run multiple spiders
zenx crawl spider1 spider2 spider3

# Run all spiders
zenx crawl all

# Run spider continuously
zenx crawl spider_name --forever

# Start listener
zenx listen listener_name

# Create new project
zenx startproject myproject
```

### Development Workflow

```bash
# 1. Create project
zenx startproject newscraper
cd newscraper/

# 2. Create spider
cat > spiders/news.py << 'EOF'
from zenx.spiders import Spider

class NewsSpider(Spider):
    name = "news"
    pipelines = ["preprocess"]
    
    async def crawl(self):
        # Your implementation
        pass
EOF

# 3. Test spider
zenx crawl news

# 4. Production deployment
zenx crawl news --forever
```

## 🔍 Examples

### Complete Web Scraper

```python
# spiders/ecommerce.py
from zenx.spiders import Spider
import re

class EcommerceSpider(Spider):
    name = "ecommerce"
    pipelines = ["preprocess", "custom_api", "synoptic_grpc"]
    
    custom_settings = {
        "CONCURRENCY": 3,
        "TASK_INTERVAL_SECONDS": 2.0,
        "SESSION_POOL_SIZE": 5
    }
    
    async def crawl(self):
        categories = ["electronics", "books", "clothing"]
        
        for category in categories:
            await self.scrape_category(category)
    
    async def scrape_category(self, category):
        base_url = f"https://example-store.com/{category}"
        
        # Get product listings
        response = await self.client.request(
            f"{base_url}?page=1",
            use_session_pool=True
        )
        
        # Parse product URLs
        product_urls = self.extract_product_urls(response.text)
        
        # Scrape each product
        for url in product_urls:
            await self.scrape_product(url, category)
    
    def extract_product_urls(self, html):
        pattern = r'href="(/products/[^"]+)"'
        return [f"https://example-store.com{match}" 
                for match in re.findall(pattern, html)]
    
    async def scrape_product(self, url, category):
        try:
            response = await self.client.request(url, use_session_pool=True)
            
            # Extract product data
            title = self.extract_title(response.text)
            price = self.extract_price(response.text)
            description = self.extract_text(response.text)
            
            item = {
                "_id": f"product_{hash(url)}",
                "url": url,
                "title": title,
                "price": price,
                "description": description,
                "category": category,
                "scraped_at": response.recv_at,
                "responded_at": response.recv_at
            }
            
            await self.pm.process_item(item, producer=self.name)
            
        except Exception as e:
            self.logger.error("Product scraping failed", 
                            url=url, error=str(e))
    
    def extract_title(self, html):
        # Custom extraction logic
        match = re.search(r'<h1[^>]*>([^<]+)</h1>', html)
        return match.group(1) if match else "Unknown"
    
    def extract_price(self, html):
        # Extract price with regex
        match = re.search(r'\$(\d+\.?\d*)', html)
        return float(match.group(1)) if match else 0.0
```

### Real-time Data Listener

```python
# listeners/market_data.py
from zenx.listeners.base import Listener, Message
import websockets
import json

class MarketDataListener(Listener):
    name = "market_data"
    pipelines = ["preprocess", "synoptic_grpc", "price_alerts"]
    
    async def listen(self):
        while True:
            try:
                await self.connect_to_market_feed()
            except Exception as e:
                self.logger.error("Market feed error", error=str(e))
                await asyncio.sleep(10)
    
    async def connect_to_market_feed(self):
        uri = "wss://ws.marketfeed.com/realtime"
        headers = {"Authorization": f"Bearer {self.settings.MARKET_API_KEY}"}
        
        async with websockets.connect(uri, extra_headers=headers) as ws:
            # Subscribe to channels
            await ws.send(json.dumps({
                "action": "subscribe",
                "channels": ["prices", "trades", "orderbook"]
            }))
            
            async for raw_message in ws:
                message = Message(text=raw_message)
                await self.process_message(message)
    
    async def process_message(self, message):
        try:
            data = json.loads(message.text)
            
            if data.get("type") == "price_update":
                item = {
                    "_id": f"price_{data['symbol']}_{data['timestamp']}",
                    "symbol": data["symbol"],
                    "price": data["price"],
                    "volume": data["volume"],
                    "timestamp": data["timestamp"],
                    "type": "price_update"
                }
                
                await self.pm.process_item(item, producer=self.name)
                
        except Exception as e:
            self.logger.error("Message processing failed", 
                            message=message.text, error=str(e))
```

## 🚀 Deployment

### Production Configuration

```python
# settings/production.py
from zenx.settings import Settings

class ProductionSettings(Settings):
    APP_ENV = "production"
    LOG_LEVEL = "INFO"
    CONCURRENCY = 10
    SESSION_POOL_SIZE = 20
    DB_TYPE = "redis"
    
    # Production-specific timeouts
    MAX_SCRAPE_DELAY = 30.0
    TASK_INTERVAL_SECONDS = 0.5
```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run spider continuously
CMD ["zenx", "crawl", "your_spider", "--forever"]
```

### Process Management

```bash
# Using systemd
[Unit]
Description=ZenX Spider Service
After=network.target

[Service]
Type=simple
User=zenx
WorkingDirectory=/opt/zenx
ExecStart=/opt/zenx/venv/bin/zenx crawl production_spider --forever
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/username/zenx.git
cd zenx

# Install development dependencies
pip install -e ".[all,dev]"

# Run tests
pytest

# Run linting
flake8 zenx/
mypy zenx/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [Full documentation](https://zenx.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/username/zenx/issues)
- **Discussions**: [GitHub Discussions](https://github.com/username/zenx/discussions)
- **Email**: support@zenx.dev

---

**Built with ❤️ for the Python community**
