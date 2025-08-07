import re
import logging
from functools import wraps
from flask import request, jsonify

logger = logging.getLogger(__name__)

def validate_api_key(api_key):
    """Validate API key format"""
    if not api_key:
        return False
    
    # API keys should start with 'aya_' and be at least 36 characters
    if not api_key.startswith('aya_'):
        return False
    
    if len(api_key) < 36:
        return False
    
    # Check if the rest contains only valid characters
    key_part = api_key[4:]  # Remove 'aya_' prefix
    if not re.match(r'^[A-Za-z0-9_-]+$', key_part):
        return False
    
    return True

def validate_address(address, blockchain=None):
    """Validate blockchain address format"""
    if not address or not isinstance(address, str):
        return False
    
    if blockchain:
        if blockchain.lower() in ['ethereum', 'polygon']:
            return validate_ethereum_address(address)
        elif blockchain.lower() == 'solana':
            return validate_solana_address(address)
    
    # Try to detect blockchain from address format
    if validate_ethereum_address(address):
        return True
    elif validate_solana_address(address):
        return True
    
    return False

def validate_ethereum_address(address):
    """Validate Ethereum-style address"""
    if not address.startswith('0x'):
        return False
    
    if len(address) != 42:
        return False
    
    # Check if it's valid hex
    try:
        int(address[2:], 16)
        return True
    except ValueError:
        return False

def validate_solana_address(address):
    """Validate Solana address"""
    import base58
    
    try:
        # Solana addresses are base58 encoded and 32 bytes when decoded
        decoded = base58.b58decode(address)
        return len(decoded) == 32
    except Exception:
        return False

def validate_amount(amount):
    """Validate amount format"""
    if not amount:
        return False
    
    try:
        # Convert to float to check if it's a valid number
        float_amount = float(amount)
        
        # Must be positive
        if float_amount <= 0:
            return False
        
        # Check for reasonable decimal places (max 18)
        decimal_places = len(str(amount).split('.')[-1]) if '.' in str(amount) else 0
        if decimal_places > 18:
            return False
        
        return True
    
    except (ValueError, TypeError):
        return False

def validate_blockchain(blockchain):
    """Validate blockchain name"""
    supported_blockchains = ['ethereum', 'polygon', 'solana']
    return blockchain and blockchain.lower() in supported_blockchains

def validate_protocol(protocol, blockchain=None):
    """Validate protocol name"""
    supported_protocols = {
        'ethereum': ['uniswap', 'sushiswap', 'aave', 'compound'],
        'polygon': ['quickswap', 'sushiswap', 'aave'],
        'solana': ['raydium', 'orca', 'serum']
    }
    
    if not protocol:
        return False
    
    if blockchain:
        blockchain_protocols = supported_protocols.get(blockchain.lower(), [])
        return protocol.lower() in blockchain_protocols
    
    # Check if protocol exists in any blockchain
    all_protocols = set()
    for protocols in supported_protocols.values():
        all_protocols.update(protocols)
    
    return protocol.lower() in all_protocols

def validate_slippage(slippage):
    """Validate slippage percentage"""
    if slippage is None:
        return True  # Optional parameter
    
    try:
        slippage_float = float(slippage)
        # Slippage should be between 0 and 50%
        return 0 <= slippage_float <= 50
    except (ValueError, TypeError):
        return False

def validate_transaction_hash(tx_hash, blockchain=None):
    """Validate transaction hash format"""
    if not tx_hash or not isinstance(tx_hash, str):
        return False
    
    if blockchain:
        if blockchain.lower() in ['ethereum', 'polygon']:
            # Ethereum/Polygon tx hashes are 0x + 64 hex characters
            return (tx_hash.startswith('0x') and 
                   len(tx_hash) == 66 and 
                   all(c in '0123456789abcdefABCDEF' for c in tx_hash[2:]))
        elif blockchain.lower() == 'solana':
            # Solana tx signatures are base58 encoded
            try:
                import base58
                decoded = base58.b58decode(tx_hash)
                return len(decoded) == 64
            except Exception:
                return False
    
    # Try to detect format
    if tx_hash.startswith('0x') and len(tx_hash) == 66:
        return all(c in '0123456789abcdefABCDEF' for c in tx_hash[2:])
    
    # Try Solana format
    try:
        import base58
        decoded = base58.b58decode(tx_hash)
        return len(decoded) == 64
    except Exception:
        return False

def validate_json_request(required_fields=None, optional_fields=None):
    """Decorator to validate JSON request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data:
                        missing_fields.append(field)
                
                if missing_fields:
                    return jsonify({
                        "error": "Missing required fields",
                        "missing_fields": missing_fields
                    }), 400
            
            # Validate field formats
            errors = []
            
            # Address validation
            if 'wallet_address' in data:
                blockchain = data.get('blockchain')
                if not validate_address(data['wallet_address'], blockchain):
                    errors.append("Invalid wallet address format")
            
            # Blockchain validation
            if 'blockchain' in data:
                if not validate_blockchain(data['blockchain']):
                    errors.append("Unsupported blockchain")
            
            # Protocol validation
            if 'protocol' in data:
                blockchain = data.get('blockchain')
                if not validate_protocol(data['protocol'], blockchain):
                    errors.append("Unsupported protocol for this blockchain")
            
            # Amount validation
            amount_fields = ['amount', 'amount_in', 'amount_a', 'amount_b']
            for field in amount_fields:
                if field in data:
                    if not validate_amount(data[field]):
                        errors.append(f"Invalid {field} format")
            
            # Token address validation
            token_fields = ['token', 'token_in', 'token_out', 'token_a', 'token_b']
            for field in token_fields:
                if field in data:
                    blockchain = data.get('blockchain')
                    if not validate_address(data[field], blockchain):
                        errors.append(f"Invalid {field} address format")
            
            # Slippage validation
            if 'slippage' in data:
                if not validate_slippage(data['slippage']):
                    errors.append("Invalid slippage value (must be between 0 and 50)")
            
            if errors:
                return jsonify({
                    "error": "Validation failed",
                    "validation_errors": errors
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def sanitize_input(input_string, max_length=None):
    """Sanitize user input"""
    if not input_string:
        return ""
    
    # Convert to string and strip whitespace
    sanitized = str(input_string).strip()
    
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in ['\n', '\r', '\t'])
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized

def validate_pagination_params(page, per_page, max_per_page=100):
    """Validate pagination parameters"""
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 50
        
        # Ensure positive values
        page = max(1, page)
        per_page = max(1, min(per_page, max_per_page))
        
        return page, per_page
    
    except (ValueError, TypeError):
        return 1, 50

class ValidationError(Exception):
    """Custom validation error"""
    
    def __init__(self, message, field=None, code=None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(self.message)

def validate_portfolio_request(data):
    """Validate portfolio request data"""
    errors = []
    
    if 'wallet_address' not in data:
        errors.append("wallet_address is required")
    elif not validate_address(data['wallet_address']):
        errors.append("Invalid wallet_address format")
    
    if 'blockchain' in data:
        if not validate_blockchain(data['blockchain']):
            errors.append("Unsupported blockchain")
    
    if errors:
        raise ValidationError("Validation failed", code="VALIDATION_ERROR")
    
    return True

def validate_swap_request(data):
    """Validate swap request data"""
    required_fields = ['wallet_address', 'blockchain', 'token_in', 'token_out', 'amount_in']
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"{field} is required")
    
    if 'wallet_address' in data and not validate_address(data['wallet_address']):
        errors.append("Invalid wallet_address format")
    
    if 'blockchain' in data and not validate_blockchain(data['blockchain']):
        errors.append("Unsupported blockchain")
    
    if 'token_in' in data and not validate_address(data['token_in']):
        errors.append("Invalid token_in address")
    
    if 'token_out' in data and not validate_address(data['token_out']):
        errors.append("Invalid token_out address")
    
    if 'amount_in' in data and not validate_amount(data['amount_in']):
        errors.append("Invalid amount_in format")
    
    if 'slippage' in data and not validate_slippage(data['slippage']):
        errors.append("Invalid slippage value")
    
    if errors:
        raise ValidationError("Swap validation failed", code="SWAP_VALIDATION_ERROR")
    
    return True
