import asyncio
from typing import Any, Dict, List, Optional

from .client import AsyncRobloxClient
from .exceptions import RobloxAPIError

# Module-level settings/state (simple, process-local)
_SESSION_COOKIE: Optional[str] = None
_MIN_AGE_LIMIT: int = 0  # Placeholder for future content filtering

def _run(coro):
    """
    Run an async coroutine in a fresh event loop.
    Note: don't call from inside an existing async loop.
    """
    return asyncio.run(coro)

async def _new_client() -> AsyncRobloxClient:
    return AsyncRobloxClient(roblosecurity_cookie=_SESSION_COOKIE)

# 1) Avatar image by user id
def robl_id_to_avatar_image(user_id: int, size: str = "720x720", format: str = "Png", circular: bool = False) -> str:
    async def _work() -> str:
        async with AsyncRobloxClient(roblosecurity_cookie=_SESSION_COOKIE) as client:
            data = await client.get_user_avatar_headshot(user_id, size=size, format=format, circular=circular)
            return data.get("imageUrl") or data.get("imageUrlFinal") or ""
    return _run(_work())

# 2) Test Roblox API health (simple smoke pings)
def robl_test_roblox_api() -> Dict[str, Any]:
    async def _work() -> Dict[str, Any]:
        async with AsyncRobloxClient(roblosecurity_cookie=_SESSION_COOKIE) as client:
            async def ping_user():
                try:
                    u = await client.get_user(1)
                    return {"ok": True, "latency_ms": None, "sample": {"id": u.get("id"), "name": u.get("name")}}
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            async def ping_avatar():
                try:
                    a = await client.get_user_avatar_headshot(1)
                    return {"ok": True, "imageUrl": a.get("imageUrl")}
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            async def ping_universe():
                try:
                    uni = await client.get_universe(21532277)  # пример популярной вселенной
                    return {"ok": True, "sample": {"id": uni.get("id"), "name": uni.get("name")}}
                except Exception as e:
                    return {"ok": False, "error": str(e)}

            r_user, r_avatar, r_uni = await asyncio.gather(ping_user(), ping_avatar(), ping_universe())
            return {
                "users.roblox.com": r_user,
                "thumbnails.roblox.com": r_avatar,
                "games.roblox.com": r_uni,
            }
    return _run(_work())

# 3) Friends list
def robl_get_friends(user_id: int) -> List[Dict[str, Any]]:
    async def _work() -> List[Dict[str, Any]]:
        async with AsyncRobloxClient(roblosecurity_cookie=_SESSION_COOKIE) as client:
            data = await client.get_friends(user_id)
            items = data.get("data") or []
            # TODO: в будущем можно зафильтровать по _MIN_AGE_LIMIT, если API даст явный возрастной рейтинг
            return items
    return _run(_work())

# 4) Client-side "age limit" toggle (semantic TBD)
def robl_set_age_limit(min_age: int) -> None:
    global _MIN_AGE_LIMIT
    if min_age < 0:
        raise ValueError("min_age must be >= 0")
    _MIN_AGE_LIMIT = min_age

# 5) Import session via .ROBLOSECURITY cookie
def robl_import_session(cookie: str) -> Dict[str, Any]:
    """
    Stores cookie and returns the authenticated user info if valid.
    """
    if not cookie or not isinstance(cookie, str):
        raise ValueError("cookie must be a non-empty string")
    async def _work() -> Dict[str, Any]:
        global _SESSION_COOKIE
        _SESSION_COOKIE = cookie
        async with AsyncRobloxClient(roblosecurity_cookie=_SESSION_COOKIE) as client:
            try:
                me = await client.get_authenticated_user()
                return {"ok": True, "user": me}
            except RobloxAPIError as e:
                # Likely 401/403 — invalid cookie
                _SESSION_COOKIE = None
                return {"ok": False, "error": f"Auth failed: {e.status_code}", "details": e.body}
            except Exception as e:
                _SESSION_COOKIE = None
                return {"ok": False, "error": str(e)}
    return _run(_work())

# 6) Not supported: username/password login
def robl_create_session(nickname: str, password: str) -> None:
    """
    We intentionally do not support password-based login.
    Use robl_import_session(cookie) with your .ROBLOSECURITY value.
    """
    raise NotImplementedError("Password login is not supported. Use robl_import_session('.ROBLOSECURITY').")