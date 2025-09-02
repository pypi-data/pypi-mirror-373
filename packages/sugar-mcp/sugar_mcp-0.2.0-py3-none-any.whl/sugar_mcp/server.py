import json
import os

from mcp.server.fastmcp import FastMCP
from sugar.chains import OPChain, BaseChain
from sugar_mcp.models import asdict

from typing import Literal, Optional


def get_chain(chain_id: int):
    """Initialize the appropriate chain based on chain_id"""
    if chain_id == 8453:
        return BaseChain()
    elif chain_id == 10:
        return OPChain()
    raise ValueError(f"Unsupported chain_id: {chain_id}")

mcp = FastMCP("sugar-mcp")


@mcp.tool()
async def get_all_tokens(listed_only: bool = False, chain_id: int = 10):
    """
     Retrieve all tokens supported by the protocol.

     Args:
         listed_only (bool): If True, only return tokens that are marked as 'listed'.
         chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

     Returns:
         List[Token]: A list of Token objects.
     """
    with get_chain(chain_id) as chain:
        tokens = chain.get_all_tokens()
        return json.dumps([asdict(t) for t in tokens])


@mcp.tool()
async def get_prices(chain_id: int = 10):
    """
    Retrieve prices for a list of tokens in terms of the stable token.

    Args:
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        List[Price]: A list of Price objects with token-price mappings.
    """
    with get_chain(chain_id) as chain:
        tokens = chain.get_all_tokens()
        prices = chain.get_prices(tokens)
        return json.dumps([asdict(t) for t in prices])


@mcp.tool()
async def get_pools(chain_id: int = 10):
    """
    Retrieve all liquidity pools or swap pools depending on the flag.

    Args:
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        List[LiquidityPool] or List[LiquidityPoolForSwap]: A list of pool objects.
    """
    with get_chain(chain_id) as chain:
        pools = chain.get_pools()
        return json.dumps([asdict(p) for p in pools])


@mcp.tool()
async def get_pool_by_address(address: str, chain_id: int = 10):
    """
    Retrieve detailed pool information by contract address.

    Args:
        address (str): The address of the liquidity pool contract.
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        Optional[LiquidityPool]: The matching LiquidityPool object, or None if not found.
    """
    with get_chain(chain_id) as chain:
        pool = chain.get_pool_by_address(address)
        if pool is None:
            return json.dumps(None)
        return json.dumps(asdict(pool))


@mcp.tool()
async def get_pools_for_swaps(chain_id: int = 10):
    """
    Retrieve all pools suitable for swaps and path finding.

    Args:
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        List[LiquidityPoolForSwap]: A list of simplified pool objects for swaps.
    """
    with get_chain(chain_id) as chain:
        pools = chain.get_pools_for_swaps()
        return json.dumps([asdict(p) for p in pools])


@mcp.tool()
async def get_latest_pool_epochs(chain_id: int = 10):
    """
    Retrieve the latest epoch data for all pools.

    Args:
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        List[LiquidityPoolEpoch]: A list of the most recent epochs across all pools.
    """
    with get_chain(chain_id) as chain:
        epochs = chain.get_latest_pool_epochs()
        return json.dumps([asdict(ep) for ep in epochs])


@mcp.tool()
async def get_pool_epochs(lp: str, offset: int = 0, limit: int = 10, chain_id: int = 10):
    """
    Retrieve historical epoch data for a given liquidity pool.

    Args:
        lp (str): Address of the liquidity pool.
        offset (int): Offset for pagination.
        limit (int): Number of epochs to retrieve.
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        List[LiquidityPoolEpoch]: A list of epoch entries for the specified pool.
    """
    with get_chain(chain_id) as chain:
        epochs = chain.get_pool_epochs(lp, offset, limit)
        return json.dumps([asdict(ep) for ep in epochs])


@mcp.tool()
async def get_quote(
        from_token: Literal["usdc", "velo", "eth"],
        to_token: Literal["usdc", "velo", "eth"],
        amount: float,
        chain_id: int = 10
):
    """
    Retrieve the best quote for swapping a given amount from one token to another.

    Args:
        from_token (Token): The token to swap from.
        to_token (Token): The token to swap to.
        amount (float): The amount to swap (in float, not uint256).
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)
        filter_quotes (Callable[[Quote], bool], optional): Optional filter to apply on the quotes.

    Returns:
        Optional[Quote]: The best available quote, or None if no valid quote was found.
    """
    from_token = getattr(OPChain, from_token, None)
    to_token = getattr(OPChain, to_token, None)
    if from_token is None or to_token is None:
        raise ValueError("Invalid token specified. Use 'usdc', 'velo', or 'eth'.")

    with get_chain(chain_id) as chain:
        quote = chain.get_quote(from_token, to_token, amount)
        return json.dumps(asdict(quote))


@mcp.tool()
async def swap(
        from_token: Literal["usdc", "velo", "eth"],
        to_token: Literal["usdc", "velo", "eth"],
        amount: float,
        slippage: Optional[float] = None,
        chain_id: int = 10
):
    """
    Execute a token swap transaction.

    Args:
        from_token (Token): The token being sold.
        to_token (Token): The token being bought.
        amount (float): The amount of `from_token` to swap.
        slippage (float, optional): Maximum acceptable slippage (default uses config value).
        chain_id (int): The chain ID to use (10 for OPChain, 8453 for BaseChain)

    Returns:
        TransactionReceipt: The transaction receipt from the swap execution.
    """
    from_token = getattr(OPChain, from_token, None)
    to_token = getattr(OPChain, to_token, None)
    if from_token is None or to_token is None:
        raise ValueError("Invalid token specified. Use 'usdc', 'velo', or 'eth'.")

    with get_chain(chain_id) as chain:
        tx_hash = chain.swap(from_token, to_token, amount, slippage)
        return tx_hash


def main():
    if not os.environ.get('SUGAR_PK'):
        raise ValueError("Environment variable SUGAR_PK is not set. Please set it to your private key.")
    print("Starting Sugar MCP server...")
    mcp.run(transport="sse")


if __name__ == "__main__":
    main()
