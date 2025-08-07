import os
import logging
from cryptography.fernet import Fernet
from eth_account import Account
from solders.keypair import Keypair
import base58
import secrets

logger = logging.getLogger(__name__)

class WalletManager:
    """Wallet management utilities"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.encryption_key = os.getenv("WALLET_ENCRYPTION_KEY")
        if not self.encryption_key:
            # In production, this should be securely stored
            self.encryption_key = Fernet.generate_key()
            logger.warning("No WALLET_ENCRYPTION_KEY found, using generated key")
        
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
        
        self.cipher = Fernet(self.encryption_key)
    
    def generate_ethereum_wallet(self):
        """Generate new Ethereum wallet"""
        try:
            # Generate random private key
            account = Account.create()
            
            return {
                "address": account.address,
                "private_key": account.key.hex(),
                "blockchain": "ethereum"
            }
        
        except Exception as e:
            logger.error(f"Failed to generate Ethereum wallet: {str(e)}")
            return None
    
    def generate_solana_wallet(self):
        """Generate new Solana wallet"""
        try:
            # Generate random keypair
            keypair = Keypair()
            
            return {
                "address": str(keypair.pubkey()),
                "private_key": base58.b58encode(keypair.secret()).decode(),
                "blockchain": "solana"
            }
        
        except Exception as e:
            logger.error(f"Failed to generate Solana wallet: {str(e)}")
            return None
    
    def encrypt_private_key(self, private_key):
        """Encrypt private key for storage"""
        try:
            if isinstance(private_key, str):
                private_key = private_key.encode()
            
            encrypted_key = self.cipher.encrypt(private_key)
            return encrypted_key.decode()
        
        except Exception as e:
            logger.error(f"Failed to encrypt private key: {str(e)}")
            return None
    
    def decrypt_private_key(self, encrypted_private_key):
        """Decrypt private key for use"""
        try:
            if isinstance(encrypted_private_key, str):
                encrypted_private_key = encrypted_private_key.encode()
            
            decrypted_key = self.cipher.decrypt(encrypted_private_key)
            return decrypted_key.decode()
        
        except Exception as e:
            logger.error(f"Failed to decrypt private key: {str(e)}")
            return None
    
    def validate_ethereum_address(self, address):
        """Validate Ethereum address format"""
        try:
            # Check if it's a valid hex string with 0x prefix
            if not address.startswith('0x'):
                return False
            
            if len(address) != 42:
                return False
            
            # Try to convert to checksum address
            checksum_address = Account.to_checksum_address(address)
            return checksum_address == address or address.lower() == address
        
        except Exception:
            return False
    
    def validate_solana_address(self, address):
        """Validate Solana address format"""
        try:
            # Solana addresses are base58 encoded and typically 32-44 characters
            if len(address) < 32 or len(address) > 44:
                return False
            
            # Try to decode as base58
            decoded = base58.b58decode(address)
            return len(decoded) == 32
        
        except Exception:
            return False
    
    def validate_private_key(self, private_key, blockchain):
        """Validate private key format"""
        try:
            if blockchain.lower() == 'ethereum' or blockchain.lower() == 'polygon':
                # Ethereum private keys are 64 hex characters (32 bytes)
                if private_key.startswith('0x'):
                    private_key = private_key[2:]
                
                if len(private_key) != 64:
                    return False
                
                # Try to create account from private key
                account = Account.from_key(private_key)
                return account is not None
            
            elif blockchain.lower() == 'solana':
                # Solana private keys are base58 encoded
                try:
                    decoded = base58.b58decode(private_key)
                    return len(decoded) == 64  # 64 bytes for Solana keypair
                except Exception:
                    return False
            
            return False
        
        except Exception as e:
            logger.error(f"Private key validation failed: {str(e)}")
            return False
    
    def get_wallet_balance_summary(self, wallet_address, blockchain):
        """Get wallet balance summary"""
        try:
            from blockchain.ethereum import EthereumClient
            from blockchain.polygon import PolygonClient
            from blockchain.solana import SolanaClient
            
            if blockchain.lower() == 'ethereum':
                client = EthereumClient()
                balance = client.get_balance(wallet_address)
                return {
                    "address": wallet_address,
                    "blockchain": "ethereum",
                    "native_balance": balance,
                    "native_symbol": "ETH"
                }
            
            elif blockchain.lower() == 'polygon':
                client = PolygonClient()
                balance = client.get_balance(wallet_address)
                return {
                    "address": wallet_address,
                    "blockchain": "polygon",
                    "native_balance": balance,
                    "native_symbol": "MATIC"
                }
            
            elif blockchain.lower() == 'solana':
                client = SolanaClient()
                balance = client.get_balance(wallet_address)
                return {
                    "address": wallet_address,
                    "blockchain": "solana",
                    "native_balance": balance,
                    "native_symbol": "SOL"
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to get wallet balance: {str(e)}")
            return None
    
    def generate_api_key(self):
        """Generate API key for user"""
        try:
            # Generate a secure random API key
            api_key = secrets.token_urlsafe(32)
            return f"aya_{api_key}"
        
        except Exception as e:
            logger.error(f"Failed to generate API key: {str(e)}")
            return None
    
    def import_wallet(self, private_key, blockchain):
        """Import existing wallet from private key"""
        try:
            if not self.validate_private_key(private_key, blockchain):
                return None
            
            if blockchain.lower() in ['ethereum', 'polygon']:
                # Handle 0x prefix
                if private_key.startswith('0x'):
                    private_key = private_key[2:]
                
                account = Account.from_key(private_key)
                return {
                    "address": account.address,
                    "private_key": private_key,
                    "blockchain": blockchain.lower()
                }
            
            elif blockchain.lower() == 'solana':
                # Decode base58 private key
                private_key_bytes = base58.b58decode(private_key)
                keypair = Keypair.from_bytes(private_key_bytes)
                
                return {
                    "address": str(keypair.pubkey()),
                    "private_key": private_key,
                    "blockchain": "solana"
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to import wallet: {str(e)}")
            return None
    
    def get_supported_blockchains(self):
        """Get list of supported blockchains"""
        return [
            {
                "name": "Ethereum",
                "id": "ethereum",
                "native_token": "ETH",
                "explorer": "https://etherscan.io"
            },
            {
                "name": "Polygon",
                "id": "polygon",
                "native_token": "MATIC",
                "explorer": "https://polygonscan.com"
            },
            {
                "name": "Solana",
                "id": "solana",
                "native_token": "SOL",
                "explorer": "https://solscan.io"
            }
        ]
