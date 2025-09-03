# TPS Agent

A lightweight Python library for measuring and throttling TPS (Transactions Per Second) in distributed applications. TPS Agent collects metrics locally and sends them to a centralized TPS Collector server.

## Features

- **Decorators**: Simple `@measure_tps` and `@throttle` decorators
- **Local Storage**: Temporary local storage with automatic cleanup
- **Reliable Transmission**: Automatic retry and acknowledgment mechanism
- **Agent Health**: Heartbeat monitoring with the collector
- **Async Support**: Works with both sync and async functions
- **Zero Configuration**: Works out of the box with sensible defaults

## Installation

```bash
pip install tps-agent
```

## Quick Start

### 1. Configure the Agent

```python
from tps_agent import configure_agent

# Configure once at application startup
configure_agent(
    collector_url="http://tps-collector:8080",
    server_id="web-server-1"
)
```

### 2. Use Decorators

```python
from tps_agent import measure_tps, throttle

@measure_tps(gateway="payment_api")
def process_payment(amount):
    # Your payment processing logic
    return {"status": "success", "amount": amount}

@throttle(gateway="external_api", max_tps=100)
@measure_tps(gateway="external_api")
def call_external_service():
    # This will be throttled to max 100 TPS
    # and metrics will be collected
    return requests.get("https://api.example.com/data")

# Async functions are supported too
@measure_tps(gateway="async_api")
async def async_operation():
    await asyncio.sleep(0.1)
    return "done"
```

## Configuration

### Environment Variables

```bash
# Required
TPS_COLLECTOR_URL=http://localhost:8080
TPS_SERVER_ID=my-server-1

# Optional
TPS_BATCH_SIZE=100
TPS_TRANSMISSION_INTERVAL=60
TPS_MAX_RETRIES=3
TPS_LOCAL_RETENTION_MINUTES=10
TPS_ENABLE_METRICS=true
TPS_ENABLE_THROTTLING=true
```

### Programmatic Configuration

```python
from tps_agent import configure_agent, AgentConfig

config = AgentConfig(
    server_id="web-server-1",
    collector_url="http://tps-collector:8080",
    batch_size=50,
    transmission_interval=30,
    max_retries=5
)

configure_agent(config=config)
```

## Advanced Usage

### Custom Tags

```python
@measure_tps(gateway="user_api", tags={"version": "v2", "region": "us-east"})
def get_user_profile(user_id):
    return {"user_id": user_id, "name": "John Doe"}
```

### Error Tracking

```python
@measure_tps(gateway="risky_operation", track_errors=True)
def risky_operation():
    if random.random() < 0.1:
        raise ValueError("Something went wrong")
    return "success"
```

### Agent Statistics

```python
from tps_agent import get_agent

agent = get_agent()
stats = agent.get_stats()
print(f"Local metrics: {stats['local_metrics_count']}")
print(f"Total stored: {stats['total_metrics_stored']}")
```

## How It Works

1. **Local Collection**: Decorators collect metrics (duration, success/failure, errors) locally
2. **Batching**: Metrics are batched in memory for efficient transmission
3. **Transmission**: Batches are sent to the collector at regular intervals
4. **Acknowledgment**: Collector confirms receipt, agent cleans up local data
5. **Retry Logic**: Failed transmissions are retried with exponential backoff
6. **Heartbeat**: Agent sends periodic health updates to collector

## Integration Examples

### Flask Application

```python
from flask import Flask
from tps_agent import configure_agent, measure_tps

app = Flask(__name__)

# Configure at startup
configure_agent(
    collector_url="http://tps-collector:8080",
    server_id="flask-app-1"
)

@app.route('/api/users/<user_id>')
@measure_tps(gateway="user_api", endpoint="get_user")
def get_user(user_id):
    # Your logic here
    return {"user_id": user_id}

if __name__ == '__main__':
    app.run()
```

### FastAPI Application

```python
from fastapi import FastAPI
from tps_agent import configure_agent, measure_tps

app = FastAPI()

# Configure at startup
@app.on_event("startup")
async def startup():
    configure_agent(
        collector_url="http://tps-collector:8080",
        server_id="fastapi-app-1"
    )

@app.get("/api/users/{user_id}")
@measure_tps(gateway="user_api", endpoint="get_user")
async def get_user(user_id: str):
    # Your async logic here
    return {"user_id": user_id}
```

## License

MIT License
