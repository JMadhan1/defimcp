import os
import logging
import requests
from blockchain.ethereum import EthereumClient
from blockchain.polygon import PolygonClient
from blockchain.solana import SolanaClient

logger = logging.getLogger(__name__)

class DEXOperations:
    """DEX trading operations across multiple blockchains"""
    
    def __init__(self):
        self.ethereum_client = EthereumClient()
        self.polygon_client = PolygonClient()
        self.solana_client = SolanaClient()
        self.one_inch_api_key = os.getenv("ONE_INCH_API_KEY", "demo-key")
    
    def execute_swap(self, blockchain, wallet_address, token_in, token_out, amount_in, slippage=0.5, protocol="uniswap"):
        """Execute a token swap on specified blockchain"""
        try:
            if blockchain.lower() == 'ethereum':
                return self._execute_ethereum_swap(wallet_address, token_in, token_out, amount_in, slippage, protocol)
            elif blockchain.lower() == 'polygon':
                return self._execute_polygon_swap(wallet_address, token_in, token_out, amount_in, slippage, protocol)
            elif blockchain.lower() == 'solana':
                return self._execute_solana_swap(wallet_address, token_in, token_out, amount_in, slippage, protocol)
            else:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
        
        except Exception as e:
            logger.error(f"Swap execution failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_ethereum_swap(self, wallet_address, token_in, token_out, amount_in, slippage, protocol):
        """Execute swap on Ethereum"""
        try:
            # Get swap quote from 1inch
            quote_url = f"https://api.1inch.dev/swap/v5.2/1/quote"
            quote_params = {
                "src": token_in,
                "dst": token_out,
                "amount": amount_in
            }
            
            headers = {"Authorization": f"Bearer {self.one_inch_api_key}"}
            quote_response = requests.get(quote_url, params=quote_params, headers=headers)
            
            if quote_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap quote"}
            
            quote_data = quote_response.json()
            
            # Get swap transaction data
            swap_url = f"https://api.1inch.dev/swap/v5.2/1/swap"
            swap_params = {
                "src": token_in,
                "dst": token_out,
                "amount": amount_in,
                "from": wallet_address,
                "slippage": slippage
            }
            
            swap_response = requests.get(swap_url, params=swap_params, headers=headers)
            
            if swap_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            swap_data = swap_response.json()
            
            # Execute transaction via Ethereum client
            tx_hash = self.ethereum_client.send_transaction(
                wallet_address=wallet_address,
                to_address=swap_data['tx']['to'],
                data=swap_data['tx']['data'],
                value=swap_data['tx']['value'],
                gas=swap_data['tx']['gas']
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount_out": quote_data.get('toAmount', '0'),
                    "gas_used": swap_data['tx']['gas'],
                    "protocol": "1inch",
                    "metadata": {
                        "quote": quote_data,
                        "swap": swap_data
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Ethereum swap failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_polygon_swap(self, wallet_address, token_in, token_out, amount_in, slippage, protocol):
        """Execute swap on Polygon"""
        try:
            # Similar to Ethereum but using Polygon chain ID (137)
            quote_url = f"https://api.1inch.dev/swap/v5.2/137/quote"
            quote_params = {
                "src": token_in,
                "dst": token_out,
                "amount": amount_in
            }
            
            headers = {"Authorization": f"Bearer {self.one_inch_api_key}"}
            quote_response = requests.get(quote_url, params=quote_params, headers=headers)
            
            if quote_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap quote"}
            
            quote_data = quote_response.json()
            
            # Get swap transaction data
            swap_url = f"https://api.1inch.dev/swap/v5.2/137/swap"
            swap_params = {
                "src": token_in,
                "dst": token_out,
                "amount": amount_in,
                "from": wallet_address,
                "slippage": slippage
            }
            
            swap_response = requests.get(swap_url, params=swap_params, headers=headers)
            
            if swap_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            swap_data = swap_response.json()
            
            # Execute transaction via Polygon client
            tx_hash = self.polygon_client.send_transaction(
                wallet_address=wallet_address,
                to_address=swap_data['tx']['to'],
                data=swap_data['tx']['data'],
                value=swap_data['tx']['value'],
                gas=swap_data['tx']['gas']
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount_out": quote_data.get('toAmount', '0'),
                    "gas_used": swap_data['tx']['gas'],
                    "protocol": "1inch",
                    "metadata": {
                        "quote": quote_data,
                        "swap": swap_data
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Polygon swap failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _execute_solana_swap(self, wallet_address, token_in, token_out, amount_in, slippage, protocol):
        """Execute swap on Solana"""
        try:
            # Use Jupiter API for Solana swaps
            quote_url = "https://quote-api.jup.ag/v6/quote"
            quote_params = {
                "inputMint": token_in,
                "outputMint": token_out,
                "amount": amount_in,
                "slippageBps": int(slippage * 100)  # Convert to basis points
            }
            
            quote_response = requests.get(quote_url, params=quote_params)
            
            if quote_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap quote"}
            
            quote_data = quote_response.json()
            
            # Get swap transaction
            swap_url = "https://quote-api.jup.ag/v6/swap"
            swap_payload = {
                "quoteResponse": quote_data,
                "userPublicKey": wallet_address
            }
            
            swap_response = requests.post(swap_url, json=swap_payload)
            
            if swap_response.status_code != 200:
                return {"success": False, "error": "Failed to get swap transaction"}
            
            swap_data = swap_response.json()
            
            # Execute transaction via Solana client
            tx_hash = self.solana_client.send_transaction(
                wallet_address=wallet_address,
                transaction=swap_data['swapTransaction']
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "amount_out": quote_data.get('outAmount', '0'),
                    "protocol": "jupiter",
                    "metadata": {
                        "quote": quote_data,
                        "swap": swap_data
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Solana swap failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_swap_quote(self, blockchain, token_in, token_out, amount_in):
        """Get swap quote without executing"""
        try:
            if blockchain.lower() == 'ethereum':
                chain_id = "1"
            elif blockchain.lower() == 'polygon':
                chain_id = "137"
            elif blockchain.lower() == 'solana':
                # Use Jupiter for Solana quotes
                quote_url = "https://quote-api.jup.ag/v6/quote"
                quote_params = {
                    "inputMint": token_in,
                    "outputMint": token_out,
                    "amount": amount_in
                }
                
                response = requests.get(quote_url, params=quote_params)
                if response.status_code == 200:
                    return {"success": True, "quote": response.json()}
                else:
                    return {"success": False, "error": "Failed to get quote"}
            else:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
            
            # For EVM chains, use 1inch
            quote_url = f"https://api.1inch.dev/swap/v5.2/{chain_id}/quote"
            quote_params = {
                "src": token_in,
                "dst": token_out,
                "amount": amount_in
            }
            
            headers = {"Authorization": f"Bearer {self.one_inch_api_key}"}
            response = requests.get(quote_url, params=quote_params, headers=headers)
            
            if response.status_code == 200:
                return {"success": True, "quote": response.json()}
            else:
                return {"success": False, "error": "Failed to get quote"}
        
        except Exception as e:
            logger.error(f"Quote fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
