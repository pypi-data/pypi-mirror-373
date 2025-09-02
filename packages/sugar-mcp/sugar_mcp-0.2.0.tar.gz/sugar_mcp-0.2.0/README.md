# Sugar MCP Server

This is an **MCP (Model Context Protocol)** server to interact with [Sugar](https://github.com/velodrome-finance/sugar-sdk)  
Sugar makes Velodrome and Aerodrome devs life sweeter 🍭




## Components

### Environment Variables
- `SUGAR_PK`: The public key for the SUGAR service.
- `SUGAR_RPC_URI_10`: The RPC URI for the SUGAR service.

### Tools

- get_all_tokens: Retrieve all tokens supported by the protocol.
- get_prices: Retrieve prices for a list of tokens in terms of the stable token.
- get_pools: Retrieve all liquidity pools or swap pools depending on the flag.
- get_pool_by_address: Retrieve detailed pool information by contract address.
- get_pools_for_swaps: Retrieve all pools suitable for swaps and path finding.
- get_latest_pool_epochs: Retrieve the latest epoch data for all pools.
- get_pool_epochs: Retrieve historical epoch data for a given liquidity pool.
- get_quote: Retrieve the best quote for swapping a given amount from one token to another.
- swap: Execute a token swap transaction.

### Usage
```json
{
  "mcpServers": {
    "sugar-mcp": {
      "env": {
        "SUGAR_PK": "xxx",
        "SUGAR_RPC_URI_10": "optionally, the RPC URI for the SUGAR service"
      },
      "command": "uvx",
      "args": [
        "sugar-mcp"
      ]
    }
  }
}
```


