import os
import logging
import time
from web3 import Web3
from eth_account import Account
from web3.exceptions import TransactionNotFound

logger = logging.getLogger(__name__)

class EthereumClient:
    """Ethereum blockchain client"""
    
    def __init__(self):
        # RPC endpoints
        self.rpc_url = os.getenv("ETHEREUM_RPC_URL", "https://cloudflare-eth.com")
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Verify connection
        if not self.w3.is_connected():
            logger.error("Failed to connect to Ethereum network")
        else:
            logger.info("Connected to Ethereum network")
    
    def get_balance(self, address):
        """Get ETH balance for address"""
        try:
            balance_wei = self.w3.eth.get_balance(address)
            balance_eth = self.w3.from_wei(balance_wei, 'ether')
            return str(balance_eth)
        
        except Exception as e:
            logger.error(f"Failed to get balance for {address}: {str(e)}")
            return "0"
    
    def get_token_balance(self, wallet_address, token_address):
        """Get ERC20 token balance"""
        try:
            # ERC20 balanceOf ABI
            erc20_abi = [{
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }, {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "type": "function"
            }]
            
            contract = self.w3.eth.contract(address=token_address, abi=erc20_abi)
            balance = contract.functions.balanceOf(wallet_address).call()
            decimals = contract.functions.decimals().call()
            
            formatted_balance = balance / (10 ** decimals)
            return str(formatted_balance)
        
        except Exception as e:
            logger.error(f"Failed to get token balance: {str(e)}")
            return "0"
    
    def send_transaction(self, wallet_address, to_address, data="0x", value="0", gas=None):
        """Send transaction"""
        try:
            # Get private key from environment (in production, use secure key management)
            private_key = os.getenv(f"PRIVATE_KEY_{wallet_address.upper()}")
            if not private_key:
                logger.error(f"Private key not found for {wallet_address}")
                return None
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(wallet_address)
            
            # Get gas price
            gas_price = self.w3.eth.gas_price
            
            # Estimate gas if not provided
            if gas is None:
                try:
                    gas = self.w3.eth.estimate_gas({
                        'from': wallet_address,
                        'to': to_address,
                        'data': data,
                        'value': int(value) if isinstance(value, str) else value
                    })
                except Exception as e:
                    logger.warning(f"Gas estimation failed: {str(e)}, using default")
                    gas = 200000  # Default gas limit
            
            # Build transaction
            transaction = {
                'nonce': nonce,
                'to': to_address,
                'value': int(value) if isinstance(value, str) else value,
                'gas': gas,
                'gasPrice': gas_price,
                'data': data,
                'chainId': 1  # Mainnet
            }
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(transaction, private_key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            logger.info(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
        
        except Exception as e:
            logger.error(f"Transaction failed: {str(e)}")
            return None
    
    def wait_for_transaction_receipt(self, tx_hash, timeout=300):
        """Wait for transaction confirmation"""
        try:
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return {
                "status": receipt.status,
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "transaction_hash": receipt.transactionHash.hex()
            }
        
        except Exception as e:
            logger.error(f"Failed to get transaction receipt: {str(e)}")
            return None
    
    def get_transaction_status(self, tx_hash):
        """Get transaction status"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return {
                "status": "confirmed" if receipt.status == 1 else "failed",
                "block_number": receipt.blockNumber,
                "gas_used": receipt.gasUsed,
                "confirmations": self.w3.eth.block_number - receipt.blockNumber
            }
        
        except TransactionNotFound:
            return {"status": "pending", "confirmations": 0}
        except Exception as e:
            logger.error(f"Failed to get transaction status: {str(e)}")
            return {"status": "unknown", "error": str(e)}
    
    def encode_function_call(self, abi, args):
        """Encode function call data"""
        try:
            # Create a temporary contract to encode the function call
            contract = self.w3.eth.contract(abi=[abi])
            function = getattr(contract.functions, abi['name'])
            encoded_data = function(*args)._encode_transaction_data()
            return encoded_data
        
        except Exception as e:
            logger.error(f"Failed to encode function call: {str(e)}")
            return "0x"
    
    def get_current_timestamp(self):
        """Get current blockchain timestamp"""
        try:
            latest_block = self.w3.eth.get_block('latest')
            return latest_block.timestamp
        
        except Exception as e:
            logger.error(f"Failed to get current timestamp: {str(e)}")
            return int(time.time())
    
    def get_gas_price(self):
        """Get current gas price"""
        try:
            return self.w3.eth.gas_price
        
        except Exception as e:
            logger.error(f"Failed to get gas price: {str(e)}")
            return 20000000000  # 20 gwei default
    
    def estimate_gas(self, transaction):
        """Estimate gas for transaction"""
        try:
            return self.w3.eth.estimate_gas(transaction)
        
        except Exception as e:
            logger.error(f"Gas estimation failed: {str(e)}")
            return 200000  # Default gas limit
    
    def call_contract_function(self, contract_address, abi, function_name, args=None):
        """Call a read-only contract function"""
        try:
            contract = self.w3.eth.contract(address=contract_address, abi=abi)
            function = getattr(contract.functions, function_name)
            
            if args:
                result = function(*args).call()
            else:
                result = function().call()
            
            return result
        
        except Exception as e:
            logger.error(f"Contract call failed: {str(e)}")
            return None
    
    def get_block_number(self):
        """Get current block number"""
        try:
            return self.w3.eth.block_number
        
        except Exception as e:
            logger.error(f"Failed to get block number: {str(e)}")
            return 0
    
    def get_transaction(self, tx_hash):
        """Get transaction details"""
        try:
            return self.w3.eth.get_transaction(tx_hash)
        
        except Exception as e:
            logger.error(f"Failed to get transaction: {str(e)}")
            return None
