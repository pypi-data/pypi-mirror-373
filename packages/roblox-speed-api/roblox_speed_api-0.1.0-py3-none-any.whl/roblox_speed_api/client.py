from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Optional

import httpx

from ._cache import TTLCache
from .exceptions import RobloxAPIError

_DEFAULT_HEADERS = {
    "Accept": "application/json",
    "User-Agent": "roblox-speed-api/0.1.0 (+https://github.com/yourname/roblox-speed-api)",
}

_AUTH_ONLY_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

class AsyncRobloxClient:
    """
    Async client for select Roblox public web APIs.
    - Retries on 429/5xx with exponential backoff (respects Retry-After).
    - Optional in-memory TTL cache for GET requests.
    - Optional auth via .ROBLOSECURITY cookie with auto X-CSRF handling.
    """

    def __init__(
        self,
        *,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        enable_cache: bool = True,
        cache_ttl: float = 30.0,
        headers: Optional[Dict[str, str]] = None,
        follow_redirects: bool = True,
        roblosecurity_cookie: Optional[str] = None,
    ) -> None:
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._headers = {**_DEFAULT_HEADERS, **(headers or {})}
        self._client = httpx.AsyncClient(timeout=timeout, follow_redirects=follow_redirects)
        self._cache = TTLCache(cache_ttl) if enable_cache else None

        self._auth_cookie: Optional[str] = None
        self._csrf_token: Optional[str] = None
        if roblosecurity_cookie:
            self.import_session_cookie(roblosecurity_cookie)

    async def __aenter__(self) -> "AsyncRobloxClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    # ---------- Auth/session ----------

    def import_session_cookie(self, cookie: str) -> None:
        """
        Import .ROBLOSECURITY cookie (string as copied from browser).
        """
        self._auth_cookie = cookie
        # Important: no 'Bearer' — it's a cookie header
        self._headers["Cookie"] = f".ROBLOSECURITY={cookie}"
        # Reset CSRF so it will be re-fetched on first 403
        self._csrf_token = None
        self._headers.pop("X-CSRF-TOKEN", None)

    async def get_authenticated_user(self) -> Optional[Dict[str, Any]]:
        """
        Returns the authenticated user dict if cookie is valid; otherwise None.
        """
        resp = await self._request("GET", "https://users.roblox.com/v1/users/authenticated", use_cache=False)
        # If not authenticated, Roblox returns 401/403 which _request would raise; catch it at call site if needed
        if isinstance(resp, dict) and resp.get("id"):
            return resp
        return None

    # ---------- Internal helpers ----------

    async def _sleep(self, seconds: float) -> None:
        await asyncio.sleep(seconds)

    def _apply_auth_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        # Ensure CSRF header is present if we already obtained it
        if self._csrf_token:
            headers["X-CSRF-TOKEN"] = self._csrf_token
        return headers

    async def _request(
        self,
        method: str,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Any:
        method_u = method.upper()

        # Cache only GET without body
        if method_u == "GET" and self._cache and use_cache:
            key = self._cache.make_key(method_u, url, params)
            cached = self._cache.get(key)
            if cached is not None:
                return cached

        attempt = 0
        while True:
            try:
                headers = dict(self._headers)
                headers = self._apply_auth_headers(headers)
                resp = await self._client.request(
                    method_u,
                    url,
                    params=params,
                    json=json_body,
                    headers=headers,
                )
            except httpx.RequestError:
                if attempt >= self._max_retries:
                    raise
                await self._sleep(self._backoff_delay(attempt))
                attempt += 1
                continue

            # Handle CSRF token dance for authenticated modifying requests
            if resp.status_code == 403 and "x-csrf-token" in resp.headers:
                # Save token and retry if allowed
                self._csrf_token = resp.headers.get("x-csrf-token") or resp.headers.get("X-CSRF-TOKEN")
                self._headers["X-CSRF-TOKEN"] = self._csrf_token or ""
                if attempt < self._max_retries:
                    attempt += 1
                    await self._sleep(0)
                    continue

            if 200 <= resp.status_code < 300:
                data = self._parse_json_safely(resp)
                if method_u == "GET" and self._cache and use_cache:
                    self._cache.set(self._cache.make_key(method_u, url, params), data)
                return data

            if resp.status_code in (429, 500, 502, 503, 504) and attempt < self._max_retries:
                retry_after = self._retry_after_seconds(resp)
                delay = retry_after if retry_after is not None else self._backoff_delay(attempt)
                await self._sleep(delay)
                attempt += 1
                continue

            # Give up
            body = self._parse_json_safely(resp)
            raise RobloxAPIError(resp.status_code, str(resp.request.url), body)

    def _backoff_delay(self, attempt: int) -> float:
        return self._backoff_factor * (2 ** attempt)

    @staticmethod
    def _retry_after_seconds(resp: httpx.Response) -> Optional[float]:
        h = resp.headers.get("Retry-After")
        if not h:
            return None
        try:
            return float(h)
        except ValueError:
            return None

    @staticmethod
    def _parse_json_safely(resp: httpx.Response) -> Any:
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    # ---------- Public API methods ----------

    # Users
    async def get_user(self, user_id: int) -> Dict[str, Any]:
        url = f"https://users.roblox.com/v1/users/{user_id}"
        return await self._request("GET", url)

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        url = "https://users.roblox.com/v1/usernames/users"
        payload = {"usernames": [username], "excludeBannedUsers": False}
        data = await self._request("POST", url, json_body=payload, use_cache=False)
        try:
            items = data.get("data") or []
            return items[0] if items else None
        except AttributeError:
            return None

    # Friends
    async def get_friends(self, user_id: int) -> Dict[str, Any]:
        """
        Returns {"data": [...]} list of friend user objects.
        May return fewer or require auth depending on privacy settings.
        """
        url = f"https://friends.roblox.com/v1/users/{user_id}/friends"
        return await self._request("GET", url)

    # Groups
    async def get_group(self, group_id: int) -> Dict[str, Any]:
        url = f"https://groups.roblox.com/v1/groups/{group_id}"
        return await self._request("GET", url)

    # Universes/Games
    async def get_universe(self, universe_id: int) -> Dict[str, Any]:
        url = "https://games.roblox.com/v1/games"
        params = {"universeIds": str(universe_id)}
        data = await self._request("GET", url, params=params)
        items = (data or {}).get("data") or []
        if not items:
            raise RobloxAPIError(404, f"{url}?universeIds={universe_id}", {"message": "Universe not found"})
        return items[0]

    # Thumbnails (user avatar/headshot)
    async def get_user_avatar_headshot(
        self,
        user_id: int,
        *,
        size: str = "720x720",
        format: str = "Png",
        circular: bool = False,
    ) -> Dict[str, Any]:
        url = "https://thumbnails.roblox.com/v1/users/avatar"
        params = {
            "userIds": str(user_id),
            "size": size,
            "format": format,
            "isCircular": "true" if circular else "false",
        }
        data = await self._request("GET", url, params=params)
        items = (data or {}).get("data") or []
        if not items:
            import httpx as _httpx
            raise RobloxAPIError(404, str(_httpx.URL(url).copy_merge_params(params)), {"message": "Avatar not found"})
        return items[0]