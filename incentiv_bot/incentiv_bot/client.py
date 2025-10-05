from typing import Optional
from web3 import Web3


class ChainIdMismatch(RuntimeError):
    pass


def make_web3(
    rpc_url: str,
    expected_chain_id: int,
    request_timeout_seconds: int = 30,
    proxy_url: Optional[str] = None,
) -> Web3:
    request_kwargs = {"timeout": request_timeout_seconds}
    if proxy_url:
        request_kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
    provider = Web3.HTTPProvider(rpc_url, request_kwargs=request_kwargs)
    w3 = Web3(provider)
    chain_id = w3.eth.chain_id
    if chain_id != expected_chain_id:
        raise ChainIdMismatch(
            f"Unexpected chain id: got {chain_id}, expected {expected_chain_id}"
        )
    return w3
