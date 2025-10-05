#!/usr/bin/env python3
from dataclasses import dataclass
from typing import Optional
import os
from dotenv import load_dotenv


@dataclass
class BotConfig:
    rpc_url: str
    chain_id: int
    accounts_file: str
    proxy_file: Optional[str]

    # API and site
    api_base: str
    site_url: Optional[str]
    user_agent: Optional[str]

    # Captcha
    turnstile_sitekey: Optional[str]
    captcha_api_key: Optional[str]
    captcha_field: str

    # Amounts
    tcent_transfer: float
    smpl_transfer: float
    bull_transfer: float
    flip_transfer: float
    tcent_swap: float
    smpl_swap: float
    bull_swap: float
    flip_swap: float
    bundle_amount: float


def load_env(env_path: Optional[str] = None) -> BotConfig:
    load_dotenv(dotenv_path=env_path or ".env")

    def must(name: str) -> str:
        value = os.getenv(name, "").strip()
        if not value:
            raise ValueError(f"Missing required env var: {name}")
        return value

    rpc_url = must("RPC_URL")
    chain_id = int(must("CHAIN_ID"))
    accounts_file = os.getenv("ACCOUNTS_FILE", "accounts.json").strip()
    proxy_file_raw = os.getenv("PROXY_FILE", "").strip()
    proxy_file = proxy_file_raw if proxy_file_raw else None

    api_base = os.getenv("API_BASE", "https://api.testnet.incentiv.io").strip()
    site_url = os.getenv("SITE_URL", "https://testnet.incentiv.io/login").strip() or None
    user_agent = os.getenv("USER_AGENT", "").strip() or None

    turnstile_sitekey = os.getenv("TURNSTILE_SITEKEY", "").strip() or None
    captcha_api_key = os.getenv("CAPTCHA_API_KEY", "").strip() or None
    captcha_field = os.getenv("CAPTCHA_FIELD", "cf-turnstile-response").strip() or "cf-turnstile-response"

    def f(name: str, default: float) -> float:
        raw = os.getenv(name)
        return float(raw) if raw else default

    return BotConfig(
        rpc_url=rpc_url,
        chain_id=chain_id,
        accounts_file=accounts_file,
        proxy_file=proxy_file,
        api_base=api_base,
        site_url=site_url,
        user_agent=user_agent,
        turnstile_sitekey=turnstile_sitekey,
        captcha_api_key=captcha_api_key,
        captcha_field=captcha_field,
        tcent_transfer=f("TCENT_TRANSFER_AMOUNT", 0.1),
        smpl_transfer=f("SMPL_TRANSFER_AMOUNT", 0.1),
        bull_transfer=f("BULL_TRANSFER_AMOUNT", 0.1),
        flip_transfer=f("FLIP_TRANSFER_AMOUNT", 0.1),
        tcent_swap=f("TCENT_SWAP_AMOUNT", 0.1),
        smpl_swap=f("SMPL_SWAP_AMOUNT", 0.1),
        bull_swap=f("BULL_SWAP_AMOUNT", 0.1),
        flip_swap=f("FLIP_SWAP_AMOUNT", 0.1),
        bundle_amount=f("BUNDLE_ACTION_AMOUNT", 0.1),
    )