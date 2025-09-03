import time
from typing import Any, Dict, Tuple, Optional

CacheKey = Tuple[str, str, Tuple[Tuple[str, str], ...]]  # method, url, sorted(params)

class TTLCache:
    def __init__(self, ttl_seconds: float = 30.0):
        self.ttl = ttl_seconds
        self._store: Dict[CacheKey, Tuple[float, Any]] = {}

    def _now(self) -> float:
        return time.monotonic()

    def get(self, key: CacheKey) -> Optional[Any]:
        item = self._store.get(key)
        if not item:
            return None
        ts, value = item
        if self._now() - ts > self.ttl:
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: CacheKey, value: Any) -> None:
        self._store[key] = (self._now(), value)

    @staticmethod
    def make_key(method: str, url: str, params: Optional[dict]) -> CacheKey:
        params_tuple: Tuple[Tuple[str, str], ...] = tuple(sorted((params or {}).items()))
        return (method.upper(), url, params_tuple)