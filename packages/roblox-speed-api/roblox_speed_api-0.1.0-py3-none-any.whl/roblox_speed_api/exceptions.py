from typing import Any, Optional

class RobloxAPIError(Exception):
    def __init__(self, status_code: int, url: str, body: Optional[Any] = None):
        super().__init__(f"Roblox API error {status_code} for {url}")
        self.status_code = status_code
        self.url = url
        self.body = body