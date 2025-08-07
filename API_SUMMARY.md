
# DeFi MCP Server - API Summary

## REST API Endpoints

### Web Interface
- `GET /` - Main application interface
- `GET /dashboard` - Portfolio management dashboard  
- `GET /api-docs` - Interactive API documentation
- `GET /ai-agent` - AI analysis interface

### Core API
- `POST /mcp` - MCP protocol endpoint (JSON-RPC 2.0)
- `GET /api/portfolio/{wallet_address}` - Portfolio data
- `POST /api/swap` - Token swap operations

## MCP Protocol Methods

1. **defi.chains** - Get supported blockchain information
2. **defi.protocols** - List available DeFi protocols
3. **defi.portfolio** - Analyze wallet portfolio
4. **defi.positions** - Get DeFi positions
5. **defi.swap** - Execute token swaps
6. **defi.lend** - Lending operations
7. **defi.farm** - Yield farming
8. **defi.transaction_status** - Monitor transactions

## Supported Protocols

### Ethereum
- Uniswap V2/V3, SushiSwap, 1inch
- Aave V3, Compound V3
- Lido Staking

### Polygon  
- QuickSwap, SushiSwap, 1inch
- Aave V3

### Solana
- Raydium, Orca, Jupiter
- Solend

## Integration Examples

```python
# MCP Client Integration
mcp_client = MCPClient("http://your-server:5000")
portfolio = mcp_client.call_method("defi.portfolio", {
    "wallet_address": "0x...",
    "blockchain": "ethereum"
})
```

```javascript
// REST API Integration
fetch('/api/portfolio/0x...', {
    method: 'GET',
    headers: {'Content-Type': 'application/json'}
})
.then(response => response.json())
.then(data => console.log(data));
```
