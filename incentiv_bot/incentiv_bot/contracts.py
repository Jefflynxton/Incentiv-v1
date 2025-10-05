from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List
from web3 import Web3

ERC20_ABI: List[dict] = [
    {
        "constant": True,
        "inputs": [{"name": "owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": False,
        "inputs": [{"name": "spender", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [
            {"name": "owner", "type": "address"},
            {"name": "spender", "type": "address"},
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function",
    },
]


@dataclass
class ERC20Helper:
    web3: Web3
    address: str

    def _contract(self):
        return self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.address),
            abi=ERC20_ABI,
        )

    def decimals(self) -> int:
        return int(self._contract().functions.decimals().call())

    def balance_of(self, owner: str) -> int:
        return int(
            self._contract()
            .functions.balanceOf(self.web3.to_checksum_address(owner))
            .call()
        )

    def approve(self, spender: str, amount: int):
        return (
            self._contract()
            .functions.approve(self.web3.to_checksum_address(spender), int(amount))
            .transact()
        )

    def transfer(self, to: str, amount: int):
        return (
            self._contract()
            .functions.transfer(self.web3.to_checksum_address(to), int(amount))
            .transact()
        )


class ContractCaller:
    def __init__(self, web3: Web3, address: str, abi: List[dict]):
        self.web3 = web3
        self.contract = web3.eth.contract(
            address=web3.to_checksum_address(address),
            abi=abi,
        )

    def call(self, fn_name: str, *args, **kwargs):
        return getattr(self.contract.functions, fn_name)(*args, **kwargs).call()

    def transact(self, fn_name: str, *args, **kwargs):
        return getattr(self.contract.functions, fn_name)(*args, **kwargs).transact()
