# AsyncSOCKS

High-performance async SOCKS5 proxy library specifically designed for Pyrogram and Hydrogram.

## Features

- **Zero dependencies** - Pure Python 3.11+ implementation
- **Async-only** - Built with asyncio for maximum performance
- **SOCKS5 support** - Username/password authentication
- **Source address binding** - For multiple IP scenarios
- **Pyrogram/Hydrogram ready** - Direct integration support
- **High concurrency** - Optimized for 100+ simultaneous connections

## Installation

```bash
pip install asyncsocks
```

## Quick Start

```python
import asyncio
from asyncsocks import AsyncSOCKSSocket

async def main():
    # Basic usage
    s = AsyncSOCKSSocket()
    s.set_proxy("127.0.0.1", 1080, "user", "pass")
    await s.connect("149.154.167.50", 443)
    
    # Use with Pyrogram/Hydrogram
    reader, writer = s.reader, s.writer
    
    # Clean shutdown
    await s.aclose()

asyncio.run(main())
```

## Pyrogram Integration

```python
from pyrogram import Client
from asyncsocks import AsyncSOCKSSocket

# Create SOCKS connection
socks = AsyncSOCKSSocket()
socks.set_proxy("127.0.0.1", 1080, "user", "pass")

# Use as raw connection in Pyrogram
app = Client("session", raw_connection=socks)
```

## API Reference

### AsyncSOCKSSocket

- `set_proxy(host, port, username=None, password=None)` - Configure proxy
- `connect(target_host, target_port, timeout=30.0, source_address=None)` - Connect through proxy
- `close()` - Sync close
- `aclose()` - Async close  
- `reader` - StreamReader property
- `writer` - StreamWriter property

### Exceptions

- `SOCKSError` - Base exception
- `AuthenticationError` - Auth failed
- `ConnectionError` - Connection failed

## License

MIT License