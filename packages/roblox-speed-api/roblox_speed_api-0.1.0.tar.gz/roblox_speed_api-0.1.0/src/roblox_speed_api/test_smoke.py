import asyncio
import pytest

from roblox_speed_api import AsyncRobloxClient

@pytest.mark.asyncio
async def test_smoke_user():
    async with AsyncRobloxClient() as client:
        user = await client.get_user(1)
        assert isinstance(user, dict)
        assert "id" in user