from __future__ import annotations
from typing import Optional, Dict, Any
from .http_client import HttpClient


class IncentivApi:
    def __init__(self, base_url: str, client: HttpClient) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client
        self.token: Optional[str] = None

    async def challenge(self, address: str, type: str = "BROWSER_EXTENSION"):
        params = {"type": type, "address": address}
        return await self.client.get_json("/api/user/challenge", params=params)

    async def login(self, challenge: str, signature: str, type: str = "BROWSER_EXTENSION"):
        body = {"challenge": challenge, "signature": signature, "type": type}
        res = await self.client.post_json("/api/user/login", json_body=body)
        if isinstance(res, dict):
            # token can be at top level or nested in result
            token = (
                res.get("token")
                or res.get("accessToken")
                or res.get("jwt")
                or (res.get("result") or {}).get("token")
                or (res.get("result") or {}).get("accessToken")
            )
            if token:
                self.client.set_bearer_token(token)
                self.token = token
        return res

    async def user(self):
        return await self.client.get_json("/api/user")

    async def faucet(self, captcha_field: str, token: str):
        body = {captcha_field: token}
        return await self.client.post_json("/api/user/faucet", json_body=body)

    async def swap_route(self, from_address: str, to_address: str):
        params = {"from": from_address, "to": to_address}
        return await self.client.get_json("/api/user/swap-route", params=params)

    async def badge_check(self):
        return await self.client.get_json("/api/badge/check")

    async def transaction_badge(self):
        return await self.client.get_json("/api/user/transaction-badge")

    async def xp_chart(self):
        return await self.client.get_json("/api/user/xp/chart")
