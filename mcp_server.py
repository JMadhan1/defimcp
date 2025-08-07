import json
import logging
from flask import request, jsonify
from app import app
from routes import require_api_key
from defi_tools.dex_operations import DexOperations
from defi_tools.lending import LendingOperations
from defi_tools.yield_farming import YieldFarmingOperations
from defi_tools.portfolio import PortfolioManager

logger = logging.getLogger(__name__)

# Initialize DeFi tools
dex_ops = DexOperations()
lending_ops = LendingOperations()
yield_ops = YieldFarmingOperations()
portfolio_mgr = PortfolioManager()

class MCPServer:
    """Model Context Protocol Server for DeFi operations"""
    
    def __init__(self):
        self.methods = {
            'defi.swap': self.handle_swap,
            'defi.lend': self.handle_lend,
            'defi.farm': self.handle_farm,
            'defi.portfolio': self.handle_portfolio,
            'defi.positions': self.handle_positions,
            'defi.transaction_status': self.handle_transaction_status,
            'defi.protocols': self.handle_protocols,
            'defi.chains': self.handle_chains
        }
    
    def handle_request(self, data):
        """Handle JSON-RPC 2.0 request"""
        try:
            method = data.get('method')
            params = data.get('params', {})
            request_id = data.get('id')
            
            if method not in self.methods:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": "Method not found"
                    },
                    "id": request_id
                }
            
            result = self.methods[method](params)
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
        
        except Exception as e:
            logger.error(f"MCP request failed: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                },
                "id": data.get('id')
            }
    
    def handle_swap(self, params):
        """Handle DEX swap operation"""
        return dex_ops.execute_swap(
            blockchain=params['blockchain'],
            wallet_address=params['wallet_address'],
            token_in=params['token_in'],
            token_out=params['token_out'],
            amount_in=params['amount_in'],
            slippage=params.get('slippage', 0.5),
            protocol=params.get('protocol', 'uniswap')
        )
    
    def handle_lend(self, params):
        """Handle lending operation"""
        return lending_ops.lend_asset(
            blockchain=params['blockchain'],
            protocol=params['protocol'],
            wallet_address=params['wallet_address'],
            token=params['token'],
            amount=params['amount']
        )
    
    def handle_farm(self, params):
        """Handle yield farming operation"""
        return yield_ops.add_liquidity(
            blockchain=params['blockchain'],
            protocol=params['protocol'],
            wallet_address=params['wallet_address'],
            pool_id=params['pool_id'],
            token_a=params['token_a'],
            token_b=params['token_b'],
            amount_a=params['amount_a'],
            amount_b=params['amount_b']
        )
    
    def handle_portfolio(self, params):
        """Handle portfolio query"""
        return portfolio_mgr.get_portfolio(
            params['wallet_address'],
            params['blockchain']
        )
    
    def handle_positions(self, params):
        """Handle positions query"""
        return portfolio_mgr.get_positions(
            params['wallet_address'],
            params['blockchain']
        )
    
    def handle_transaction_status(self, params):
        """Handle transaction status query"""
        return {
            "tx_hash": params['tx_hash'],
            "status": "confirmed",  # This would check actual blockchain status
            "block_number": 12345678,
            "gas_used": "21000"
        }
    
    def handle_protocols(self, params):
        """Handle supported protocols query"""
        return {
            "protocols": {
                "ethereum": ["uniswap", "compound", "aave"],
                "polygon": ["quickswap", "aave"],
                "solana": ["raydium", "orca"]
            }
        }
    
    def handle_chains(self, params):
        """Handle supported chains query"""
        return {
            "chains": ["ethereum", "polygon", "solana"],
            "default_chain": "ethereum"
        }

# Initialize MCP server
mcp_server = MCPServer()

@app.route('/mcp', methods=['POST'])
@require_api_key
def mcp_endpoint():
    """MCP JSON-RPC endpoint"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }), 400
        
        # Handle batch requests
        if isinstance(data, list):
            results = []
            for req in data:
                result = mcp_server.handle_request(req)
                results.append(result)
            return jsonify(results)
        else:
            result = mcp_server.handle_request(data)
            return jsonify(result)
    
    except Exception as e:
        logger.error(f"MCP endpoint error: {str(e)}")
        return jsonify({
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Internal error"
            },
            "id": None
        }), 500
