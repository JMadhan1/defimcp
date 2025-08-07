import os
import json
import logging
from flask import render_template, request, jsonify, session
from app import app, db
from models import User, Wallet, Transaction, Portfolio, ProtocolPosition
from utils.validation import validate_api_key, validate_address
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

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard for monitoring DeFi operations"""
    return render_template('dashboard.html')

@app.route('/api/docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

# API Routes with authentication
def require_api_key(f):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        user = User.query.filter_by(api_key=api_key, is_active=True).first()
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        
        request.current_user = user
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/api/v1/swap', methods=['POST'])
@require_api_key
def api_swap():
    """Execute DEX swap operation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'token_in', 'token_out', 'amount_in']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=data['wallet_address'],
            user_id=request.current_user.id,
            blockchain=data['blockchain']
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Execute swap
        result = dex_ops.execute_swap(
            blockchain=data['blockchain'],
            wallet_address=data['wallet_address'],
            token_in=data['token_in'],
            token_out=data['token_out'],
            amount_in=data['amount_in'],
            slippage=data.get('slippage', 0.5),
            protocol=data.get('protocol', 'uniswap')
        )
        
        if result['success']:
            # Save transaction to database
            tx = Transaction(
                user_id=request.current_user.id,
                wallet_id=wallet.id,
                tx_hash=result['tx_hash'],
                blockchain=data['blockchain'],
                operation_type='swap',
                protocol=data.get('protocol', 'uniswap'),
                amount=data['amount_in'],
                token_in=data['token_in'],
                token_out=data['token_out'],
                gas_used=result.get('gas_used'),
                status='pending',
                metadata=result.get('metadata', {})
            )
            db.session.add(tx)
            db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Swap operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/lend', methods=['POST'])
@require_api_key
def api_lend():
    """Execute lending operation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'protocol', 'token', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=data['wallet_address'],
            user_id=request.current_user.id,
            blockchain=data['blockchain']
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Execute lending operation
        result = lending_ops.lend_asset(
            blockchain=data['blockchain'],
            protocol=data['protocol'],
            wallet_address=data['wallet_address'],
            token=data['token'],
            amount=data['amount']
        )
        
        if result['success']:
            # Save transaction and position
            tx = Transaction(
                user_id=request.current_user.id,
                wallet_id=wallet.id,
                tx_hash=result['tx_hash'],
                blockchain=data['blockchain'],
                operation_type='lend',
                protocol=data['protocol'],
                amount=data['amount'],
                token_in=data['token'],
                gas_used=result.get('gas_used'),
                status='pending',
                metadata=result.get('metadata', {})
            )
            db.session.add(tx)
            
            # Create or update position
            position = ProtocolPosition.query.filter_by(
                user_id=request.current_user.id,
                wallet_id=wallet.id,
                protocol=data['protocol'],
                position_type='lending',
                token_address=data['token']
            ).first()
            
            if position:
                # Update existing position
                current_amount = float(position.amount)
                new_amount = current_amount + float(data['amount'])
                position.amount = str(new_amount)
            else:
                # Create new position
                position = ProtocolPosition(
                    user_id=request.current_user.id,
                    wallet_id=wallet.id,
                    protocol=data['protocol'],
                    position_type='lending',
                    token_address=data['token'],
                    token_symbol=result.get('token_symbol', ''),
                    amount=data['amount'],
                    blockchain=data['blockchain'],
                    metadata=result.get('metadata', {})
                )
                db.session.add(position)
            
            db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Lending operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/farm', methods=['POST'])
@require_api_key
def api_farm():
    """Execute yield farming operation"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['wallet_address', 'blockchain', 'protocol', 'pool_id', 'token_a', 'token_b', 'amount_a', 'amount_b']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=data['wallet_address'],
            user_id=request.current_user.id,
            blockchain=data['blockchain']
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Execute yield farming operation
        result = yield_ops.add_liquidity(
            blockchain=data['blockchain'],
            protocol=data['protocol'],
            wallet_address=data['wallet_address'],
            pool_id=data['pool_id'],
            token_a=data['token_a'],
            token_b=data['token_b'],
            amount_a=data['amount_a'],
            amount_b=data['amount_b']
        )
        
        if result['success']:
            # Save transaction and position
            tx = Transaction(
                user_id=request.current_user.id,
                wallet_id=wallet.id,
                tx_hash=result['tx_hash'],
                blockchain=data['blockchain'],
                operation_type='farm',
                protocol=data['protocol'],
                amount=f"{data['amount_a']},{data['amount_b']}",
                token_in=f"{data['token_a']},{data['token_b']}",
                gas_used=result.get('gas_used'),
                status='pending',
                metadata=result.get('metadata', {})
            )
            db.session.add(tx)
            
            # Create farming position
            position = ProtocolPosition(
                user_id=request.current_user.id,
                wallet_id=wallet.id,
                protocol=data['protocol'],
                position_type='farming',
                token_address=data['pool_id'],
                token_symbol=f"{result.get('token_a_symbol', '')}-{result.get('token_b_symbol', '')}",
                amount=result.get('lp_tokens', '0'),
                blockchain=data['blockchain'],
                metadata={
                    'pool_id': data['pool_id'],
                    'token_a': data['token_a'],
                    'token_b': data['token_b'],
                    'amount_a': data['amount_a'],
                    'amount_b': data['amount_b']
                }
            )
            db.session.add(position)
            db.session.commit()
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Yield farming operation failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/portfolio/<wallet_address>')
@require_api_key
def api_portfolio(wallet_address):
    """Get portfolio information for a wallet"""
    try:
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=wallet_address,
            user_id=request.current_user.id
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Get portfolio data
        portfolio_data = portfolio_mgr.get_portfolio(wallet_address, wallet.blockchain)
        
        return jsonify(portfolio_data)
    
    except Exception as e:
        logger.error(f"Portfolio fetch failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/positions/<wallet_address>')
@require_api_key
def api_positions(wallet_address):
    """Get DeFi positions for a wallet"""
    try:
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=wallet_address,
            user_id=request.current_user.id
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Get positions from database
        positions = ProtocolPosition.query.filter_by(wallet_id=wallet.id).all()
        
        positions_data = []
        for pos in positions:
            positions_data.append({
                'id': pos.id,
                'protocol': pos.protocol,
                'position_type': pos.position_type,
                'token_symbol': pos.token_symbol,
                'amount': pos.amount,
                'apy': pos.apy,
                'rewards_earned': pos.rewards_earned,
                'blockchain': pos.blockchain,
                'created_at': pos.created_at.isoformat(),
                'metadata': pos.metadata
            })
        
        return jsonify({
            "wallet_address": wallet_address,
            "positions": positions_data,
            "total_positions": len(positions_data)
        })
    
    except Exception as e:
        logger.error(f"Positions fetch failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/api/v1/transactions/<wallet_address>')
@require_api_key
def api_transactions(wallet_address):
    """Get transaction history for a wallet"""
    try:
        # Validate wallet ownership
        wallet = Wallet.query.filter_by(
            address=wallet_address,
            user_id=request.current_user.id
        ).first()
        
        if not wallet:
            return jsonify({"error": "Wallet not found or not owned by user"}), 404
        
        # Get transactions
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        transactions = Transaction.query.filter_by(wallet_id=wallet.id)\
            .order_by(Transaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        tx_data = []
        for tx in transactions.items:
            tx_data.append({
                'id': tx.id,
                'tx_hash': tx.tx_hash,
                'blockchain': tx.blockchain,
                'operation_type': tx.operation_type,
                'protocol': tx.protocol,
                'amount': tx.amount,
                'token_in': tx.token_in,
                'token_out': tx.token_out,
                'gas_used': tx.gas_used,
                'status': tx.status,
                'created_at': tx.created_at.isoformat(),
                'confirmed_at': tx.confirmed_at.isoformat() if tx.confirmed_at else None,
                'metadata': tx.metadata
            })
        
        return jsonify({
            "wallet_address": wallet_address,
            "transactions": tx_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": transactions.total,
                "pages": transactions.pages
            }
        })
    
    except Exception as e:
        logger.error(f"Transactions fetch failed: {str(e)}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
