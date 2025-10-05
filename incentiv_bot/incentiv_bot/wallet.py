from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware import SignAndSendRawMiddlewareBuilder

Account.enable_unaudited_hdwallet_features()


@dataclass
class Wallet:
    address: str
    account: LocalAccount


class WalletManager:
    def __init__(self, web3: Web3, accounts_file: str):
        self.web3 = web3
        self.wallets: List[Wallet] = []
        self._load_accounts(accounts_file)

    def _load_accounts(self, accounts_file: str) -> None:
        path = Path(accounts_file)
        if not path.exists():
            return
        data = json.loads(path.read_text())
        for entry in data:
            try:
                if isinstance(entry, dict) and entry.get("private_key"):
                    acct: LocalAccount = Account.from_key(entry["private_key"])  # type: ignore[assignment]
                    self.wallets.append(Wallet(address=acct.address, account=acct))
                elif isinstance(entry, dict) and entry.get("mnemonic"):
                    acct = Account.from_mnemonic(entry["mnemonic"])  # type: ignore[assignment]
                    self.wallets.append(Wallet(address=acct.address, account=acct))
            except Exception:
                # Skip invalid key/mnemonic entries
                continue

    def attach_wallet(self, wallet: Wallet) -> None:
        builder = SignAndSendRawMiddlewareBuilder(self.web3)
        self.web3.middleware_onion.add(builder.build(account=wallet.account))

    def attach_first_wallet(self) -> Wallet:
        if not self.wallets:
            raise ValueError("No wallets loaded. Provide at least one in accounts.json")
        wallet = self.wallets[0]
        self.attach_wallet(wallet)
        return wallet

    def iterate_wallets(self) -> Iterable[Wallet]:
        yield from self.wallets
