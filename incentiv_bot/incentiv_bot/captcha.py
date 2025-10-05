from __future__ import annotations
from typing import Optional, Dict, Any
import aiohttp
import asyncio
import time

CREATE_URL = "https://api.2captcha.com/createTask"
RESULT_URL = "https://api.2captcha.com/getTaskResult"


async def solve_turnstile(
    api_key: str,
    sitekey: str,
    page_url: str,
    proxy: Optional[str] = None,
    timeout_seconds: int = 120,
    poll_interval_seconds: int = 5,
) -> str:
    # Use proxyless task by default. Full proxy task needs decomposed proxy details.
    task: Dict[str, Any] = {
        "type": "TurnstileTaskProxyless",
        "websiteURL": page_url,
        "websiteKey": sitekey,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(CREATE_URL, json={"clientKey": api_key, "task": task}) as resp:
            data = await resp.json()
            task_id = data.get("taskId")
            if not task_id:
                raise RuntimeError(f"2captcha createTask error: {data}")

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            await asyncio.sleep(poll_interval_seconds)
            async with session.post(RESULT_URL, json={"clientKey": api_key, "taskId": task_id}) as resp:
                data = await resp.json()
                status = data.get("status")
                if status == "ready":
                    solution = data.get("solution", {})
                    token = solution.get("token")
                    if not token:
                        raise RuntimeError(f"2captcha ready without token: {data}")
                    return token
                if status == "processing":
                    continue
                raise RuntimeError(f"2captcha error: {data}")
        raise TimeoutError("2captcha turnstile solve timeout")