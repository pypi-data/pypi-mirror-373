# roblox-speed-api

Fast, asyncio-friendly Roblox Web API client with retries and caching.

- Async-first (`httpx`)
- Retries with exponential backoff (handles 429 and 5xx; respects `Retry-After`)
- Optional in-memory TTL cache for GETs
- Minimal, typed-friendly return dicts

PyPI name: `roblox-speed-api`  
Import: `import roblox_speed_api`

## Install

```bash
pip install roblox-speed-api