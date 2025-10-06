#!/usr/bin/env python3
import argparse
import asyncio
from pathlib import Path
from typing import Optional

from fake_useragent import UserAgent
from eth_account.messages import encode_defunct

from incentiv_bot.config import load_env
from incentiv_bot.client import make_web3
from incentiv_bot.wallet import WalletManager
from incentiv_bot.http_client import HttpClient
from incentiv_bot.incentiv_api import IncentivApi
from incentiv_bot.captcha import solve_turnstile


def resolve_proxy(cfg_proxy_file: Optional[str], cli_proxy: Optional[str]) -> Optional[str]:
    if cli_proxy:
        return cli_proxy
    if cfg_proxy_file and Path(cfg_proxy_file).exists():
        for line in Path(cfg_proxy_file).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            return line if "://" in line else f"http://{line}"
    return None


def choose_wallet_for_address(wallets: WalletManager, address: str):
    address_lower = address.lower()
    for w in wallets.iterate_wallets():
        if w.address.lower() == address_lower:
            return w
    raise SystemExit(f"Address not found in accounts: {address}")


async def run_api_action(args) -> None:
    cfg = load_env(args.env)

    proxy_url = resolve_proxy(cfg.proxy_file, args.proxy)

    user_agent = cfg.user_agent or UserAgent().random
    referer = cfg.site_url or "https://testnet.incentiv.io/login"
    origin = referer.split("/login")[0] if "/login" in referer else referer

    async with HttpClient(
        base_url=cfg.api_base,
        user_agent=user_agent,
        proxy=proxy_url,
        referer=referer,
        origin=origin,
    ) as http:
        # Preload bearer if provided in env
        if cfg.auth_bearer:
            http.set_bearer_token(cfg.auth_bearer)
        api = IncentivApi(cfg.api_base, http)

        if args.command == "api-badge":
            res = await api.badge_check()
            print(res)
            return

        if args.command == "api-user":
            res = await api.user()
            print(res)
            return

        if args.command == "api-xp":
            res = await api.xp_chart()
            print(res)
            return

        if args.command == "api-swap-route":
            res = await api.swap_route(args.from_token, args.to_token)
            print(res)
            return

        if args.command == "api-challenge":
            res = await api.challenge(args.address)
            print(res)
            return

        if args.command == "api-login":
            # fetch challenge
            challenge_res = await api.challenge(args.address)
            challenge = None
            if isinstance(challenge_res, dict):
                result = challenge_res.get("result") or {}
                challenge = result.get("message") or result.get("challenge") or result.get("payload")
            if not isinstance(challenge, str) or not challenge.strip():
                raise SystemExit(f"Cannot extract challenge from: {challenge_res}")

            # sign with matching wallet
            if not Path(cfg.accounts_file).exists():
                raise SystemExit("accounts file not found")
            w3 = make_web3(cfg.rpc_url, cfg.chain_id, proxy_url)
            wallets = WalletManager(w3, cfg.accounts_file)
            signer = choose_wallet_for_address(wallets, args.address)
            sig = signer.account.sign_message(encode_defunct(text=challenge)).signature.hex()

            res = await api.login(challenge, sig)
            print(res)
            return

        if args.command == "api-faucet":
            captcha_field = args.captcha_field or cfg.captcha_field or "verificationToken"
            if args.solve:
                if not cfg.captcha_api_key or not cfg.turnstile_sitekey or not cfg.site_url:
                    raise SystemExit("Missing CAPTCHA_API_KEY or TURNSTILE_SITEKEY or SITE_URL for solving")
                token = await solve_turnstile(cfg.captcha_api_key, cfg.turnstile_sitekey, cfg.site_url, proxy_url)
            else:
                if not args.captcha_token:
                    raise SystemExit("Provide --captcha-token or use --solve to auto-solve")
                token = args.captcha_token
            res = await api.faucet(captcha_field, token)
            print(res)
            return

    raise SystemExit("Unknown command")


def main() -> None:
    parser = argparse.ArgumentParser(description="Incentiv EVM bot CLI")
    parser.add_argument("--env", default=None, help="Path to .env file")
    parser.add_argument("--proxy", default=None, help="HTTP/SOCKS proxy URL")

    sub = parser.add_subparsers(dest="command")

    sub.add_parser("api-badge")
    sub.add_parser("api-user")
    sub.add_parser("api-xp")

    p_swap = sub.add_parser("api-swap-route")
    p_swap.add_argument("--from-token", dest="from_token", required=True)
    p_swap.add_argument("--to-token", dest="to_token", required=True)

    p_ch = sub.add_parser("api-challenge")
    p_ch.add_argument("--address", required=True)

    p_login = sub.add_parser("api-login")
    p_login.add_argument("--address", required=True)

    p_faucet = sub.add_parser("api-faucet")
    p_faucet.add_argument("--solve", action="store_true")
    p_faucet.add_argument("--captcha-token", dest="captcha_token", default=None)
    p_faucet.add_argument("--captcha-field", dest="captcha_field", default=None)

    args = parser.parse_args()

    if not args.command:
        cfg = load_env(args.env)
        w3 = make_web3(cfg.rpc_url, cfg.chain_id, resolve_proxy(cfg.proxy_file, args.proxy))
        wallets = WalletManager(w3, cfg.accounts_file)
        if wallets.wallets:
            print(f"Chain ID: {w3.eth.chain_id}")
            print(f"First wallet: {wallets.wallets[0].address}")
        else:
            print(f"Chain ID: {w3.eth.chain_id}")
            print("No wallets loaded")
        return

    asyncio.run(run_api_action(args))


if __name__ == "__main__":
    main()
