import os
import logging
import base64
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.instruction import Instruction
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from solana.rpc.commitment import Confirmed

logger = logging.getLogger(__name__)

class SolanaClient:
    """Solana blockchain client"""
    
    def __init__(self):
        # RPC endpoints
        self.rpc_url = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
        self.client = Client(self.rpc_url)
        
        # Test connection
        try:
            # Use get_slot() instead of get_health() for connection test
            slot_response = self.client.get_slot()
            if slot_response and slot_response.value is not None:
                logger.info("Connected to Solana network")
            else:
                logger.warning("Solana connection may be unstable")
        except Exception as e:
            logger.error(f"Failed to connect to Solana network: {str(e)}")
    
    def get_balance(self, address):
        """Get SOL balance for address"""
        try:
            pubkey = Pubkey.from_string(address)
            balance_response = self.client.get_balance(pubkey)
            
            if balance_response.value is not None:
                # Convert lamports to SOL (1 SOL = 1e9 lamports)
                balance_sol = balance_response.value / 1e9
                return str(balance_sol)
            else:
                return "0"
        
        except Exception as e:
            logger.error(f"Failed to get SOL balance for {address}: {str(e)}")
            return "0"
    
    def get_token_accounts(self, wallet_address):
        """Get SPL token accounts for wallet"""
        try:
            pubkey = Pubkey.from_string(wallet_address)
            
            # Get token accounts by owner
            response = self.client.get_token_accounts_by_owner(
                pubkey,
                {"programId": Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")}  # SPL Token Program
            )
            
            tokens = []
            if response.value:
                for account in response.value:
                    account_info = account.account
                    # Parse token account data
                    data = account_info.data
                    if len(data) >= 64:  # Basic validation
                        # Extract mint and amount from token account data
                        # This is a simplified parsing - in production, use proper SPL token parsing
                        mint = base64.b64encode(data[:32]).decode()
                        amount = int.from_bytes(data[64:72], byteorder='little')
                        
                        tokens.append({
                            "mint": mint,
                            "balance": str(amount),
                            "account": str(account.pubkey)
                        })
            
            return tokens
        
        except Exception as e:
            logger.error(f"Failed to get token accounts: {str(e)}")
            return []
    
    def send_transaction(self, wallet_address, transaction=None, instructions=None):
        """Send transaction on Solana"""
        try:
            # Get private key from environment
            private_key_b58 = os.getenv(f"SOLANA_PRIVATE_KEY_{wallet_address.upper()}")
            if not private_key_b58:
                logger.error(f"Private key not found for {wallet_address}")
                return None
            
            # Create keypair from private key
            keypair = Keypair.from_base58_string(private_key_b58)
            
            if transaction:
                # If transaction is provided as serialized data
                if isinstance(transaction, str):
                    # Deserialize transaction
                    tx_bytes = base64.b64decode(transaction)
                    tx = Transaction.from_bytes(tx_bytes)
                else:
                    tx = transaction
            elif instructions:
                # Build transaction from instructions
                recent_blockhash = self.client.get_latest_blockhash().value.blockhash
                tx = Transaction.new_with_payer(instructions, keypair.pubkey())
                tx.recent_blockhash = recent_blockhash
            else:
                logger.error("No transaction or instructions provided")
                return None
            
            # Sign transaction
            tx.sign([keypair])
            
            # Send transaction
            response = self.client.send_transaction(
                tx,
                opts=TxOpts(skip_confirmation=False, preflight_commitment=Confirmed)
            )
            
            if response.value:
                logger.info(f"Solana transaction sent: {response.value}")
                return str(response.value)
            else:
                logger.error("Failed to send Solana transaction")
                return None
        
        except Exception as e:
            logger.error(f"Solana transaction failed: {str(e)}")
            return None
    
    def get_transaction_status(self, tx_signature):
        """Get transaction status on Solana"""
        try:
            response = self.client.get_signature_status(tx_signature)
            
            if response.value:
                status = response.value
                if status.confirmation_status:
                    return {
                        "status": "confirmed",
                        "confirmation_status": status.confirmation_status,
                        "slot": status.slot,
                        "confirmations": status.confirmations or 0
                    }
                else:
                    return {"status": "pending", "confirmations": 0}
            else:
                return {"status": "not_found", "confirmations": 0}
        
        except Exception as e:
            logger.error(f"Failed to get transaction status: {str(e)}")
            return {"status": "unknown", "error": str(e)}
    
    def get_account_info(self, address):
        """Get account information"""
        try:
            pubkey = Pubkey.from_string(address)
            response = self.client.get_account_info(pubkey)
            
            if response.value:
                return {
                    "lamports": response.value.lamports,
                    "owner": str(response.value.owner),
                    "executable": response.value.executable,
                    "rent_epoch": response.value.rent_epoch
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"Failed to get account info: {str(e)}")
            return None
    
    def build_raydium_add_liquidity_instruction(self, wallet_address, pool_id, token_a, token_b, amount_a, amount_b):
        """Build Raydium add liquidity instruction"""
        try:
            # This is a simplified example - in production, use Raydium SDK
            # or proper instruction building with correct account keys and data
            
            # Raydium AMM program ID
            raydium_program_id = Pubkey.from_string("675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8")
            
            # Create instruction data (this would be properly encoded in production)
            instruction_data = b"add_liquidity_instruction_data"  # Placeholder
            
            # Account keys (these would be the actual required accounts for Raydium)
            accounts = [
                # User wallet
                {"pubkey": Pubkey.from_string(wallet_address), "is_signer": True, "is_writable": True},
                # Pool ID
                {"pubkey": Pubkey.from_string(pool_id), "is_signer": False, "is_writable": True},
                # Token accounts would be added here
            ]
            
            instruction = Instruction(
                program_id=raydium_program_id,
                accounts=accounts,
                data=instruction_data
            )
            
            return instruction
        
        except Exception as e:
            logger.error(f"Failed to build Raydium instruction: {str(e)}")
            return None
    
    def get_program_accounts(self, program_id):
        """Get accounts owned by a program"""
        try:
            pubkey = Pubkey.from_string(program_id)
            response = self.client.get_program_accounts(pubkey)
            
            accounts = []
            if response.value:
                for account in response.value:
                    accounts.append({
                        "pubkey": str(account.pubkey),
                        "account": {
                            "lamports": account.account.lamports,
                            "owner": str(account.account.owner),
                            "executable": account.account.executable,
                            "rent_epoch": account.account.rent_epoch
                        }
                    })
            
            return accounts
        
        except Exception as e:
            logger.error(f"Failed to get program accounts: {str(e)}")
            return []
    
    def get_current_slot(self):
        """Get current slot"""
        try:
            response = self.client.get_slot()
            return response.value if response.value else 0
        
        except Exception as e:
            logger.error(f"Failed to get current slot: {str(e)}")
            return 0
    
    def get_recent_blockhash(self):
        """Get recent blockhash"""
        try:
            response = self.client.get_latest_blockhash()
            return str(response.value.blockhash) if response.value else None
        
        except Exception as e:
            logger.error(f"Failed to get recent blockhash: {str(e)}")
            return None
    
    def simulate_transaction(self, transaction):
        """Simulate transaction"""
        try:
            response = self.client.simulate_transaction(transaction)
            
            if response.value:
                return {
                    "success": response.value.err is None,
                    "logs": response.value.logs,
                    "accounts": response.value.accounts,
                    "units_consumed": response.value.units_consumed
                }
            else:
                return {"success": False, "error": "Simulation failed"}
        
        except Exception as e:
            logger.error(f"Transaction simulation failed: {str(e)}")
            return {"success": False, "error": str(e)}
