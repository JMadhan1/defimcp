from flask import render_template, request, jsonify
from app import app, db
from models import User, Wallet, Transaction, Portfolio, ProtocolPosition
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Import DeFi operations
try:
    from defi_tools.dex_operations import DEXOperations
    from defi_tools.lending import LendingOperations
    from defi_tools.yield_farming import YieldFarmingOperations
    from defi_tools.portfolio import PortfolioManager
    # Import AI Agent and Portfolio Analytics (assuming these exist in your project)
    from ai_agent import DeFiAIAgent
    from portfolio_analytics import PortfolioAnalytics

    dex_ops = DEXOperations()
    lending_ops = LendingOperations()
    farming_ops = YieldFarmingOperations()
    portfolio_mgr = PortfolioManager()
    # Initialize AI components
    ai_agent = DeFiAIAgent()
    portfolio_analyzer = PortfolioAnalytics()

except ImportError as e:
    logger.warning(f"Could not import necessary modules: {e}")
    dex_ops = None
    lending_ops = None
    farming_ops = None
    portfolio_mgr = None
    ai_agent = None
    portfolio_analyzer = None

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')

@app.route('/api-docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

@app.route('/ai-agent')
def ai_agent_ui(): # Renamed to avoid conflict with imported ai_agent
    """AI Agent interface page"""
    return render_template('ai_agent.html')

@app.route('/ai-features')
def ai_features():
    """AI Features showcase page"""
    return render_template('ai_features.html')

# API Routes

@app.route('/api/v1/swap', methods=['POST'])
def api_swap():
    """Execute DEX swap operation"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'token_in', 'token_out', 'amount_in']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # For demo purposes, return success response
        # In production, this would execute actual swap
        if dex_ops:
            try:
                result = dex_ops.execute_swap(
                    blockchain=data['blockchain'],
                    wallet_address=data['wallet_address'],
                    token_in=data['token_in'],
                    token_out=data['token_out'],
                    amount_in=data['amount_in'],
                    slippage=data.get('slippage', 0.5),
                    protocol=data.get('protocol', 'uniswap')
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"Swap execution failed: {e}")
                return jsonify({
                    "success": False,
                    "error": "Swap execution failed",
                    "details": str(e)
                }), 500
        else:
            return jsonify({
                "success": True,
                "message": "Demo mode: Swap would be executed",
                "tx_hash": f"0x{''.join(['0'] * 64)}",
                "blockchain": data['blockchain'],
                "protocol": data.get('protocol', 'uniswap')
            })

    except Exception as e:
        logger.error(f"Swap operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/lend', methods=['POST'])
def api_lend():
    """Execute lending operation"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'protocol', 'token', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # For demo purposes, return success response
        if lending_ops:
            try:
                result = lending_ops.lend(
                    blockchain=data['blockchain'],
                    protocol=data['protocol'],
                    wallet_address=data['wallet_address'],
                    token=data['token'],
                    amount=data['amount']
                )
                return jsonify(result)
            except Exception as e:
                logger.error(f"Lending execution failed: {e}")
                return jsonify({
                    "success": False,
                    "error": "Lending execution failed",
                    "details": str(e)
                }), 500
        else:
            return jsonify({
                "success": True,
                "message": "Demo mode: Lending would be executed",
                "tx_hash": f"0x{''.join(['0'] * 64)}",
                "blockchain": data['blockchain'],
                "protocol": data['protocol']
            })

    except Exception as e:
        logger.error(f"Lending operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/farm', methods=['POST'])
def farm_tokens():
    """Farm tokens for yield"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'pool_address', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        wallet_address = data['wallet_address']
        blockchain = data['blockchain']
        pool_address = data['pool_address']
        amount = data['amount']

        logger.info(f"Farming request: {wallet_address} on {blockchain}")

        # Here you would implement actual farming logic
        # For now, return a mock response

        response = {
            "success": True,
            "tx_hash": f"0xfarm{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            "message": f"Successfully farmed {amount} tokens in pool {pool_address}",
            "pool_info": {
                "address": pool_address,
                "apy": "12.5%",
                "tvl": "$2.5M",
                "rewards": ["COMP", "SUSHI"]
            }
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Farming operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/portfolio/<wallet_address>', methods=['GET'])
def api_portfolio(wallet_address):
    """Get portfolio information"""
    try:
        if portfolio_mgr:
            try:
                portfolio = portfolio_mgr.get_portfolio(wallet_address)
                return jsonify({"portfolio": portfolio})
            except Exception as e:
                logger.error(f"Portfolio fetch failed: {e}")
                return jsonify({
                    "portfolio": None,
                    "error": "Failed to fetch portfolio",
                    "details": str(e)
                }), 500
        else:
            # Mock data if DeFi operations are not available
            return jsonify({
                "portfolio": {
                    "wallet_address": wallet_address,
                    "total_value_usd": 15000.75,
                    "tokens": [
                        {"symbol": "ETH", "amount": 5.2, "value_usd": 10000.50},
                        {"symbol": "USDC", "amount": 10000, "value_usd": 10000.25}
                    ],
                    "last_updated": "2025-01-01T00:00:00Z"
                }
            })

    except Exception as e:
        logger.error(f"Portfolio operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/positions/<wallet_address>', methods=['GET'])
def api_positions(wallet_address):
    """Get DeFi positions"""
    try:
        # Placeholder for fetching actual positions
        # For now, return mock data
        mock_positions = [
            {"protocol": "Aave", "type": "Lending", "token": "USDC", "amount": "10000", "apy": "3.5%"},
            {"protocol": "Uniswap", "type": "LP", "token": "ETH-USDC", "amount": "5", "apy": "8.2%"}
        ]
        return jsonify({"positions": mock_positions})

    except Exception as e:
        logger.error(f"Positions operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/transactions/<wallet_address>', methods=['GET'])
def api_transactions(wallet_address):
    """Get transaction history"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 50, type=int), 100)

        # Placeholder for fetching actual transactions
        # For now, return mock data
        mock_transactions = [
            {"tx_hash": "0x123...", "type": "Swap", "from_token": "ETH", "to_token": "USDC", "amount": "1.5", "timestamp": "2024-01-15T10:00:00Z"},
            {"tx_hash": "0x456...", "type": "Lend", "token": "USDC", "amount": "5000", "timestamp": "2024-01-14T11:30:00Z"}
        ]
        return jsonify({
            "transactions": mock_transactions,
            "page": page,
            "per_page": per_page,
            "total": len(mock_transactions) # Mock total
        })

    except Exception as e:
        logger.error(f"Transactions operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# AI Features Endpoints

@app.route('/api/v1/ai/portfolio-health', methods=['POST'])
def ai_portfolio_health():
    """Get AI portfolio health diagnosis"""
    try:
        data = request.get_json()
        wallet_address = data.get('wallet_address')
        blockchain = data.get('blockchain', 'ethereum')

        if not wallet_address:
            return jsonify({"error": "wallet_address is required"}), 400

        # Get portfolio data using PortfolioAnalytics
        if portfolio_analyzer:
            portfolio_result = portfolio_analyzer.get_portfolio(wallet_address, blockchain)
            if not portfolio_result or not portfolio_result.get("success"):
                return jsonify({"error": "Failed to fetch portfolio data"}), 400

            portfolio_data = portfolio_result.get("portfolio", {})
        else:
            # Mock portfolio data if PortfolioAnalytics is not available
            portfolio_data = {
                "wallet_address": wallet_address,
                "total_value_usd": 15000.75,
                "tokens": [
                    {"symbol": "ETH", "amount": 5.2, "value_usd": 10000.50},
                    {"symbol": "USDC", "amount": 10000, "value_usd": 10000.25}
                ],
                "last_updated": "2025-01-01T00:00:00Z"
            }
            logger.warn("PortfolioAnalytics not available, using mock data for portfolio health.")


        # Get AI diagnosis using AIAgent
        if ai_agent:
            diagnosis = ai_agent.portfolio_doctor.diagnose_portfolio(portfolio_data)
            return jsonify({
                "success": True,
                "diagnosis": diagnosis
            })
        else:
            return jsonify({"error": "AI Agent not available"}), 500

    except Exception as e:
        logger.error(f"Portfolio health check failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/ai/create-strategy', methods=['POST'])
def ai_create_strategy():
    """Create AI-powered investment strategy"""
    try:
        data = request.get_json()
        user_goals = data.get('goals', '')
        wallet_address = data.get('wallet_address')
        blockchain = data.get('blockchain', 'ethereum')

        if not user_goals:
            return jsonify({"error": "User goals are required"}), 400

        # Get portfolio data if wallet provided
        portfolio_data = None
        if wallet_address:
            if portfolio_analyzer:
                portfolio_result = portfolio_analyzer.get_portfolio(wallet_address, blockchain)
                if portfolio_result and portfolio_result.get("success"):
                    portfolio_data = portfolio_result.get("portfolio", {})
            else:
                # Mock portfolio data if PortfolioAnalytics is not available
                portfolio_data = {
                    "wallet_address": wallet_address,
                    "total_value_usd": 15000.75,
                    "tokens": [
                        {"symbol": "ETH", "amount": 5.2, "value_usd": 10000.50},
                        {"symbol": "USDC", "amount": 10000, "value_usd": 10000.25}
                    ],
                    "last_updated": "2025-01-01T00:00:00Z"
                }
                logger.warn("PortfolioAnalytics not available, using mock data for strategy creation.")


        # Create strategy using AIAgent
        if ai_agent:
            strategy = ai_agent.strategy_sommelier.create_strategy(user_goals, portfolio_data)
            return jsonify({
                "success": True,
                "strategy": strategy
            })
        else:
            return jsonify({"error": "AI Agent not available"}), 500

    except Exception as e:
        logger.error(f"Strategy creation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/ai/chat', methods=['POST'])
def ai_chat():
    """Chat with AI assistant"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        wallet_address = data.get('wallet_address')
        blockchain = data.get('blockchain', 'ethereum')

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # Get context data if wallet provided
        portfolio_data = None
        transaction_history = None

        if wallet_address:
            # Get portfolio
            if portfolio_analyzer:
                portfolio_result = portfolio_analyzer.get_portfolio(wallet_address, blockchain)
                if portfolio_result and portfolio_result.get("success"):
                    portfolio_data = portfolio_result.get("portfolio", {})
            else:
                # Mock portfolio data if PortfolioAnalytics is not available
                portfolio_data = {
                    "wallet_address": wallet_address,
                    "total_value_usd": 15000.75,
                    "tokens": [
                        {"symbol": "ETH", "amount": 5.2, "value_usd": 10000.50},
                        {"symbol": "USDC", "amount": 10000, "value_usd": 10000.25}
                    ],
                    "last_updated": "2025-01-01T00:00:00Z"
                }
                logger.warn("PortfolioAnalytics not available, using mock data for chat.")

            # Get recent transactions (mock for now)
            transaction_history = [
                {"type": "swap", "amount": "100 USDC", "timestamp": "2024-01-01"},
                {"type": "lend", "amount": "500 USDC", "timestamp": "2024-01-02"}
            ]

        # Get AI response using AIAgent
        if ai_agent:
            response = ai_agent.chat_assistant.chat(message, portfolio_data, transaction_history)
            return jsonify({
                "success": True,
                "response": response
            })
        else:
            return jsonify({"error": "AI Agent not available"}), 500

    except Exception as e:
        logger.error(f"AI chat failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# MCP Server endpoint
@app.route('/mcp', methods=['POST'])
def mcp_endpoint():
    """MCP JSON-RPC endpoint"""
    try:
        request_data = request.get_json()

        # Basic MCP response structure
        response = {
            "jsonrpc": "2.0",
            "id": request_data.get("id"),
            "result": {
                "success": True,
                "message": "MCP endpoint available",
                "method": request_data.get("method"),
                "params": request_data.get("params")
            }
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"MCP operation failed: {str(e)}")
        return jsonify({
            "jsonrpc": "2.0",
            "id": request_data.get("id") if 'request_data' in locals() else None,
            "error": {
                "code": -32603,
                "message": "Internal error",
                "data": str(e)
            }
        }), 500

if __name__ == '__main__':
    app.run(debug=True)