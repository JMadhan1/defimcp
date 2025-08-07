
import os
import logging
import requests
from utils.wallet import WalletManager

logger = logging.getLogger(__name__)

class TestnetHelper:
    """Helper functions for testnet operations"""
    
    def __init__(self):
        self.wallet_manager = WalletManager()
        self.use_testnet = os.getenv("USE_TESTNET", "false").lower() == "true"
    
    def get_testnet_faucet_urls(self):
        """Get faucet URLs for getting free testnet tokens"""
        return {
            "ethereum_sepolia": {
                "faucet": "https://sepoliafaucet.com",
                "alternative": "https://faucets.chain.link/sepolia",
                "instructions": "Connect wallet and request 0.5 ETH per day"
            },
            "polygon_mumbai": {
                "faucet": "https://faucet.polygon.technology",
                "alternative": "https://mumbai-faucet.com",
                "instructions": "Connect wallet and request MATIC tokens"
            },
            "solana_devnet": {
                "faucet": "https://faucet.solana.com",
                "cli_command": "solana airdrop 2 <your_address> --url devnet",
                "instructions": "Request up to 2 SOL per day"
            }
        }
    
    def generate_testnet_wallet_guide(self):
        """Generate step-by-step guide for testnet wallet setup"""
        return {
            "steps": [
                {
                    "step": 1,
                    "title": "Generate Test Wallet",
                    "description": "Create a new wallet specifically for testing",
                    "action": "Use the wallet generation feature in the dashboard"
                },
                {
                    "step": 2,
                    "title": "Switch to Testnet Mode",
                    "description": "Configure your app to use testnet networks",
                    "action": "Set USE_TESTNET=true in environment variables"
                },
                {
                    "step": 3,
                    "title": "Get Test Tokens",
                    "description": "Request free tokens from faucets",
                    "action": "Visit faucet websites and request tokens"
                },
                {
                    "step": 4,
                    "title": "Start Testing",
                    "description": "Test DeFi operations with your testnet wallet",
                    "action": "Use swap, lending, and other DeFi features safely"
                }
            ],
            "warnings": [
                "Never use testnet private keys on mainnet",
                "Testnet tokens have no real value",
                "Some testnet networks may be unstable"
            ]
        }
    
    def validate_testnet_address(self, address, network):
        """Validate if address is appropriate for testnet"""
        if network == "ethereum_sepolia":
            return self.wallet_manager.validate_ethereum_address(address)
        elif network == "polygon_mumbai":
            return self.wallet_manager.validate_ethereum_address(address)
        elif network == "solana_devnet":
            return self.wallet_manager.validate_solana_address(address)
        return False
    
    def get_testnet_token_contracts(self):
        """Get common testnet token contract addresses"""
        return {
            "ethereum_sepolia": {
                "USDC": "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8",
                "DAI": "0xFF34B3d4Aee8ddCd6F9AFFFB6Fe49bD371b8a357",
                "LINK": "0x779877A7B0D9E8603169DdbD7836e478b4624789"
            },
            "polygon_mumbai": {
                "USDC": "0x2058A9D7613eEE744279e3856Ef0eAda5FCbaA7e",
                "DAI": "0x001B3B4d0F3714Ca98ba10F6042DaEbF0B1B7b6F",
                "WMATIC": "0x9c3C9283D3e44854697Cd22D3Faa240Cfb032889"
            },
            "solana_devnet": {
                "USDC": "Gh9ZwEmdLJ8DscKNTkTqPbNwLNNBjuSzaG9Vp2KGtKJr",
                "SOL": "So11111111111111111111111111111111111111112"
            }
        }
    
    def check_testnet_balance(self, wallet_address, network):
        """Check testnet balance for given wallet"""
        try:
            balance_info = self.wallet_manager.get_wallet_balance_summary(
                wallet_address, 
                network.split('_')[0]  # Extract base network name
            )
            
            if balance_info:
                return {
                    "network": network,
                    "address": wallet_address,
                    "balance": balance_info["native_balance"],
                    "symbol": balance_info["native_symbol"],
                    "is_testnet": True
                }
            
            return None
        
        except Exception as e:
            logger.error(f"Failed to check testnet balance: {str(e)}")
            return None
    
    def get_recommended_test_amounts(self):
        """Get recommended amounts for testing different operations"""
        return {
            "ethereum_sepolia": {
                "swap_test": "0.01 ETH",
                "lending_test": "0.1 ETH",
                "liquidity_test": "0.05 ETH"
            },
            "polygon_mumbai": {
                "swap_test": "1 MATIC",
                "lending_test": "10 MATIC", 
                "liquidity_test": "5 MATIC"
            },
            "solana_devnet": {
                "swap_test": "0.1 SOL",
                "lending_test": "1 SOL",
                "liquidity_test": "0.5 SOL"
            }
        }
