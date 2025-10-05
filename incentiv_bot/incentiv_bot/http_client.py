from __future__ import annotations
from typing import Optional, Dict, Any
import aiohttp


class HttpClient:
    def __init__(
        self,
        base_url: str,
        user_agent: Optional[str] = None,
        proxy: Optional[str] = None,
        referer: Optional[str] = None,
        origin: Optional[str] = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.proxy = proxy
        self.timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        headers: Dict[str, str] = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/json",
        }
        if user_agent:
            headers["User-Agent"] = user_agent
        if origin:
            headers["Origin"] = origin
        if referer:
            headers["Referer"] = referer
        self._headers = headers
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "HttpClient":
        self._session = aiohttp.ClientSession(headers=self._headers, timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session is not None:
            await self._session.close()
            self._session = None

    def set_bearer_token(self, token: str) -> None:
        if self._session is not None:
            self._session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            self._headers["Authorization"] = f"Bearer {token}"

    async def get_json(self, path: str, params: Optional[Dict[str, Any]] = None):
        assert self._session is not None, "HttpClient must be used as an async context manager"
        url = path if path.startswith("http") else f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        async with self._session.get(url, params=params, proxy=self.proxy) as resp:
            resp.raise_for_status()
            if "application/json" in resp.headers.get("Content-Type", ""):
                return await resp.json()
            return await resp.text()

    async def post_json(self, path: str, json_body: Optional[Dict[str, Any]] = None):
        assert self._session is not None, "HttpClient must be used as an async context manager"
        url = path if path.startswith("http") else f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        async with self._session.post(url, json=json_body or {}, proxy=self.proxy) as resp:
            resp.raise_for_status()
            if "application/json" in resp.headers.get("Content-Type", ""):
                return await resp.json()
            return await resp.text()