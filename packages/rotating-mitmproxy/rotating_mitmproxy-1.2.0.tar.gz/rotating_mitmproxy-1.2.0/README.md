# Rotating MitmProxy

A smart proxy rotator built on mitmproxy that automatically rotates through multiple upstream proxies with health monitoring and failover.

## Features

- **Smart Proxy Rotation**: Round-robin, random, fastest, and smart selection strategies
- **Health Monitoring**: Real-time proxy health scoring and automatic failover
- **High Concurrency**: Handles 100+ concurrent requests efficiently
- **Multiple Formats**: Supports HTTP/SOCKS proxies with authentication
- **Web Dashboard**: Real-time statistics and monitoring interface

## Installation

```bash
pip install rotating-mitmproxy
```

## Quick Start

### 1. Create a proxy list file

```text
# proxy_list.txt
proxy1.example.com:8080
proxy2.example.com:8080
user:pass@proxy3.example.com:8080
socks5://proxy4.example.com:1080
```

### 2. Start the proxy server

```bash
python -m rotating_mitmproxy --proxy-list proxy_list.txt --port 3129
```

### 3. Use the proxy

```python
import requests

proxies = {
    'http': 'http://localhost:3129',
    'https': 'http://localhost:3129'
}

response = requests.get('https://httpbin.org/ip', proxies=proxies)
print(response.json())
```

## Command Line Options

```bash
python -m rotating_mitmproxy [OPTIONS]

Options:
  --proxy-list FILE     Path to proxy list file (required)
  --port PORT          Listen port (default: 3129)
  --strategy STRATEGY  Selection strategy: round-robin, random, fastest, smart (default: smart)
  --health-check       Enable health checking (default: enabled)
  --web-port PORT      Web dashboard port (default: 8081, 0 to disable)
  --verbose LEVEL      Verbosity: quiet, normal, verbose (default: normal)
```

## Proxy List Format

The proxy list file supports multiple formats:

```text
# HTTP proxies
proxy1.example.com:8080
user:pass@proxy2.example.com:8080

# SOCKS proxies  
socks5://proxy3.example.com:1080
socks5://user:pass@proxy4.example.com:1080

# With protocol specification
http://proxy5.example.com:8080
https://proxy6.example.com:8080
```

## Selection Strategies

- **round-robin**: Cycles through proxies in order
- **random**: Selects proxies randomly
- **fastest**: Prefers proxies with lowest response times
- **smart**: Combines health scoring with performance metrics (recommended)

## Web Dashboard

Access the web dashboard at `http://localhost:8081` to view:

- Real-time proxy statistics
- Health scores and response times
- Success/failure rates
- Active connections

## Programmatic Usage

```python
from rotating_mitmproxy import RotatingProxy

# Start proxy server
proxy = RotatingProxy(
    proxy_list_file="proxy_list.txt",
    port=3129,
    strategy="smart"
)

proxy.start()

# Use with requests
import requests
proxies = {'http': 'http://localhost:3129', 'https': 'http://localhost:3129'}
response = requests.get('https://httpbin.org/ip', proxies=proxies)

# Stop server
proxy.stop()
```

## Health Monitoring

The system automatically monitors proxy health by:

- Tracking response times and success rates
- Scoring proxies based on performance
- Temporarily disabling failed proxies
- Gradually re-enabling recovered proxies

## Configuration

Environment variables:

```bash
export ROTATING_PROXY_LIST="proxy_list.txt"
export ROTATING_PROXY_PORT="3129"
export ROTATING_PROXY_STRATEGY="smart"
export ROTATING_PROXY_WEB_PORT="8081"
```

## Testing

```bash
# Run tests
python -m pytest tests/ -v

# Test with example
python examples/basic_example.py
```

## License

MIT License - see LICENSE file for details.
