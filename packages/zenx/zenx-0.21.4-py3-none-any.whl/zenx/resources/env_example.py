ENV_EXAMPLE = """
# Application Environment
APP_ENV="dev"
LOG_LEVEL="DEBUG"

# Scraping Configuration
SESSION_POOL_SIZE="1"
#-- 60 seconds
MAX_SCRAPE_DELAY="60.0" 
#-- max size of the deque for memory database
DQ_MAX_SIZE="100"
#-- 7 days (7*24*60*60)
REDIS_RECORD_EXPIRY_SECONDS="604800" 
CONCURRENCY="1"
TASK_INTERVAL_SECONDS="1.0"
START_OFFSET_SECONDS="60.0"

# Database Configuration
#-- redis
DB_TYPE="memory" 
DB_NAME=
DB_USER=
DB_PASS=
DB_HOST=
#DB_PORT=

# Proxy Configuration
PROXY=

# Synoptic GRPC Configuration
SYNOPTIC_GRPC_SERVER_URI="ingress.opticfeeds.com"
SYNOPTIC_GRPC_TOKEN=
SYNOPTIC_GRPC_ID=

# Synoptic Enterprise GRPC Configuration
SYNOPTIC_ENTERPRISE_USEAST1_GRPC_SERVER_URI="us-east-1.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_EUCENTRAL1_GRPC_SERVER_URI="eu-central-1.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_EUWEST2_GRPC_SERVER_URI="eu-west-2.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_USEAST1CHI2A_GRPC_SERVER_URI="us-east-1-chi-2a.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_USEAST1NYC2A_GRPC_SERVER_URI="us-east-1-nyc-2a.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_APNORTHEAST1_GRPC_SERVER_URI="ap-northeast-1.enterprise.synoptic.com:50051"
SYNOPTIC_ENTERPRISE_GRPC_TOKEN=
SYNOPTIC_ENTERPRISE_GRPC_ID=

# Discord Integration
SYNOPTIC_DISCORD_WEBHOOK=

# WebSocket API Configuration
SYNOPTIC_WS_API_KEY=
SYNOPTIC_WS_STREAM_ID=

SYNOPTIC_FREE_WS_API_KEY=
SYNOPTIC_FREE_WS_STREAM_ID=


# Monitoring Configuration
MONITOR_ITXP_TOKEN=
MONITOR_ITXP_URI=
"""