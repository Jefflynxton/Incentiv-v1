#!/usr/bin/env python3
import argparse
from pathlib import Path
from incentiv_bot.config import load_env
from incentiv_bot.client import make_web3
from incentiv_bot.wallet import WalletManager


def main() -> None:
    parser = argparse.ArgumentParser(description="Incentiv EVM bot CLI")
    parser.add_argument("action", nargs="?", default="info", help="Action: info")
    parser.add_argument("--env", default=None, help="Path to .env file")
    parser.add_argument("--proxy", default=None, help="HTTP proxy URL (overrides PROXY_FILE)")
    args = parser.parse_args()

    cfg = load_env(args.env)

    proxy_url = None
    if args.proxy:
        proxy_url = args.proxy
    elif cfg.proxy_file and Path(cfg.proxy_file).exists():
        # Load first proxy from file
        for line in Path(cfg.proxy_file).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            proxy_url = line if "://" in line else f"http://{line}"
            break

    w3 = make_web3(cfg.rpc_url, cfg.chain_id, proxy_url=proxy_url)

    if args.action == "info":
        print(f"Chain ID: {w3.eth.chain_id}")
        # Wallets optional for info
        wallets = WalletManager(w3, cfg.accounts_file)
        if wallets.wallets:
            print(f"First wallet: {wallets.wallets[0].address}")
        else:
            print("No wallets loaded")
    else:
        raise SystemExit(f"Unknown action: {args.action}")


if __name__ == "__main__":
    main()
