import os
import logging
from blockchain.ethereum import EthereumClient
from blockchain.polygon import PolygonClient

logger = logging.getLogger(__name__)

class LendingOperations:
    """Lending protocol operations"""
    
    def __init__(self):
        self.ethereum_client = EthereumClient()
        self.polygon_client = PolygonClient()
        
        # Protocol contract addresses
        self.protocols = {
            'ethereum': {
                'aave': '0x7d2768dE32b0b80b7a3454c06BdAc94A69DDc7A9',
                'compound': '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B'
            },
            'polygon': {
                'aave': '0x8dFf5E27EA6b7AC08EbFdf9eB090F32ee9a30fcf'
            }
        }
    
    def lend_asset(self, blockchain, protocol, wallet_address, token, amount):
        """Lend asset to a protocol"""
        try:
            if blockchain.lower() == 'ethereum':
                return self._lend_ethereum(protocol, wallet_address, token, amount)
            elif blockchain.lower() == 'polygon':
                return self._lend_polygon(protocol, wallet_address, token, amount)
            else:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
        
        except Exception as e:
            logger.error(f"Lending operation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _lend_ethereum(self, protocol, wallet_address, token, amount):
        """Lend on Ethereum"""
        try:
            if protocol.lower() == 'aave':
                return self._lend_aave_ethereum(wallet_address, token, amount)
            elif protocol.lower() == 'compound':
                return self._lend_compound_ethereum(wallet_address, token, amount)
            else:
                return {"success": False, "error": f"Unsupported protocol: {protocol}"}
        
        except Exception as e:
            logger.error(f"Ethereum lending failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _lend_aave_ethereum(self, wallet_address, token, amount):
        """Lend to Aave on Ethereum"""
        try:
            # Aave lending pool contract address
            lending_pool = self.protocols['ethereum']['aave']
            
            # ABI for deposit function
            deposit_abi = [{
                "inputs": [
                    {"name": "asset", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "onBehalfOf", "type": "address"},
                    {"name": "referralCode", "type": "uint16"}
                ],
                "name": "deposit",
                "type": "function"
            }]
            
            # Encode function call
            function_data = self.ethereum_client.encode_function_call(
                abi=deposit_abi[0],
                args=[token, int(amount), wallet_address, 0]
            )
            
            # Execute transaction
            tx_hash = self.ethereum_client.send_transaction(
                wallet_address=wallet_address,
                to_address=lending_pool,
                data=function_data,
                value="0"
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "protocol": "aave",
                    "operation": "deposit",
                    "amount": amount,
                    "token": token,
                    "aToken": self._get_atoken_address(token),  # Address of aToken received
                    "metadata": {
                        "lending_pool": lending_pool,
                        "estimated_apy": self._get_aave_apy(token)
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Aave lending failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _lend_compound_ethereum(self, wallet_address, token, amount):
        """Lend to Compound on Ethereum"""
        try:
            # Get cToken address for the underlying token
            ctoken_address = self._get_ctoken_address(token)
            
            if not ctoken_address:
                return {"success": False, "error": f"Unsupported token for Compound: {token}"}
            
            # ABI for mint function
            mint_abi = [{
                "inputs": [{"name": "mintAmount", "type": "uint256"}],
                "name": "mint",
                "type": "function"
            }]
            
            # Encode function call
            function_data = self.ethereum_client.encode_function_call(
                abi=mint_abi[0],
                args=[int(amount)]
            )
            
            # Execute transaction
            tx_hash = self.ethereum_client.send_transaction(
                wallet_address=wallet_address,
                to_address=ctoken_address,
                data=function_data,
                value="0"
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "protocol": "compound",
                    "operation": "mint",
                    "amount": amount,
                    "token": token,
                    "cToken": ctoken_address,
                    "metadata": {
                        "ctoken_address": ctoken_address,
                        "estimated_apy": self._get_compound_apy(ctoken_address)
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Compound lending failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _lend_polygon(self, protocol, wallet_address, token, amount):
        """Lend on Polygon"""
        try:
            if protocol.lower() == 'aave':
                return self._lend_aave_polygon(wallet_address, token, amount)
            else:
                return {"success": False, "error": f"Unsupported protocol: {protocol}"}
        
        except Exception as e:
            logger.error(f"Polygon lending failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _lend_aave_polygon(self, wallet_address, token, amount):
        """Lend to Aave on Polygon"""
        try:
            # Aave lending pool contract address on Polygon
            lending_pool = self.protocols['polygon']['aave']
            
            # ABI for deposit function (same as Ethereum)
            deposit_abi = [{
                "inputs": [
                    {"name": "asset", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "onBehalfOf", "type": "address"},
                    {"name": "referralCode", "type": "uint16"}
                ],
                "name": "deposit",
                "type": "function"
            }]
            
            # Encode function call
            function_data = self.polygon_client.encode_function_call(
                abi=deposit_abi[0],
                args=[token, int(amount), wallet_address, 0]
            )
            
            # Execute transaction
            tx_hash = self.polygon_client.send_transaction(
                wallet_address=wallet_address,
                to_address=lending_pool,
                data=function_data,
                value="0"
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "protocol": "aave",
                    "operation": "deposit",
                    "amount": amount,
                    "token": token,
                    "metadata": {
                        "lending_pool": lending_pool,
                        "blockchain": "polygon"
                    }
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Aave Polygon lending failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def withdraw_asset(self, blockchain, protocol, wallet_address, token, amount):
        """Withdraw lent asset from protocol"""
        try:
            if blockchain.lower() == 'ethereum':
                return self._withdraw_ethereum(protocol, wallet_address, token, amount)
            elif blockchain.lower() == 'polygon':
                return self._withdraw_polygon(protocol, wallet_address, token, amount)
            else:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
        
        except Exception as e:
            logger.error(f"Withdrawal operation failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _withdraw_ethereum(self, protocol, wallet_address, token, amount):
        """Withdraw from Ethereum protocols"""
        try:
            if protocol.lower() == 'aave':
                return self._withdraw_aave_ethereum(wallet_address, token, amount)
            elif protocol.lower() == 'compound':
                return self._withdraw_compound_ethereum(wallet_address, token, amount)
            else:
                return {"success": False, "error": f"Unsupported protocol: {protocol}"}
        
        except Exception as e:
            logger.error(f"Ethereum withdrawal failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _withdraw_aave_ethereum(self, wallet_address, token, amount):
        """Withdraw from Aave on Ethereum"""
        try:
            lending_pool = self.protocols['ethereum']['aave']
            
            withdraw_abi = [{
                "inputs": [
                    {"name": "asset", "type": "address"},
                    {"name": "amount", "type": "uint256"},
                    {"name": "to", "type": "address"}
                ],
                "name": "withdraw",
                "type": "function"
            }]
            
            # Use max uint256 for full withdrawal if amount is "max"
            withdraw_amount = 2**256 - 1 if amount == "max" else int(amount)
            
            function_data = self.ethereum_client.encode_function_call(
                abi=withdraw_abi[0],
                args=[token, withdraw_amount, wallet_address]
            )
            
            tx_hash = self.ethereum_client.send_transaction(
                wallet_address=wallet_address,
                to_address=lending_pool,
                data=function_data,
                value="0"
            )
            
            if tx_hash:
                return {
                    "success": True,
                    "tx_hash": tx_hash,
                    "protocol": "aave",
                    "operation": "withdraw",
                    "amount": amount,
                    "token": token
                }
            else:
                return {"success": False, "error": "Transaction failed"}
        
        except Exception as e:
            logger.error(f"Aave withdrawal failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_lending_positions(self, blockchain, wallet_address):
        """Get lending positions for a wallet"""
        try:
            positions = []
            
            if blockchain.lower() == 'ethereum':
                # Get Aave positions
                aave_positions = self._get_aave_positions_ethereum(wallet_address)
                positions.extend(aave_positions)
                
                # Get Compound positions
                compound_positions = self._get_compound_positions_ethereum(wallet_address)
                positions.extend(compound_positions)
            
            elif blockchain.lower() == 'polygon':
                # Get Aave positions on Polygon
                aave_positions = self._get_aave_positions_polygon(wallet_address)
                positions.extend(aave_positions)
            
            return {"success": True, "positions": positions}
        
        except Exception as e:
            logger.error(f"Failed to get lending positions: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_atoken_address(self, token):
        """Get aToken address for underlying token"""
        # This would be fetched from Aave's protocol data provider
        atoken_mapping = {
            "0xA0b86a33E6411D40Ecaa6C4A6E5d75d8b3c7FD68": "0x028171bCA77440897B824Ca71D1c56caC55b68A3",  # USDC -> aUSDC
            "0x6B175474E89094C44Da98b954EedeAC495271d0F": "0x030bA81f1c18d280636F32af80b9AAd02Cf0854e"   # DAI -> aDAI
        }
        return atoken_mapping.get(token, token)
    
    def _get_ctoken_address(self, token):
        """Get cToken address for underlying token"""
        ctoken_mapping = {
            "0xA0b86a33E6411D40Ecaa6C4A6E5d75d8b3c7FD68": "0x39AA39c021dfbaE8faC545936693aC917d5E7563",  # USDC -> cUSDC
            "0x6B175474E89094C44Da98b954EedeAC495271d0F": "0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643"   # DAI -> cDAI
        }
        return ctoken_mapping.get(token)
    
    def _get_aave_apy(self, token):
        """Get current Aave APY for token"""
        # This would fetch real APY data from Aave API
        return 3.5  # Placeholder APY
    
    def _get_compound_apy(self, ctoken_address):
        """Get current Compound APY for cToken"""
        # This would fetch real APY data from Compound API
        return 2.8  # Placeholder APY
    
    def _get_aave_positions_ethereum(self, wallet_address):
        """Get Aave positions on Ethereum"""
        # This would query Aave's data provider contract
        return []
    
    def _get_compound_positions_ethereum(self, wallet_address):
        """Get Compound positions on Ethereum"""
        # This would query Compound's contracts
        return []
    
    def _get_aave_positions_polygon(self, wallet_address):
        """Get Aave positions on Polygon"""
        # This would query Aave's data provider contract on Polygon
        return []
