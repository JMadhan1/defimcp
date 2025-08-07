import os
import logging
import requests
from blockchain.ethereum import EthereumClient
from blockchain.polygon import PolygonClient
from blockchain.solana import SolanaClient

logger = logging.getLogger(__name__)

class PortfolioManager:
    """Portfolio management and tracking"""
    
    def __init__(self):
        self.ethereum_client = EthereumClient()
        self.polygon_client = PolygonClient()
        self.solana_client = SolanaClient()
        
        # Price APIs
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY", "demo-key")
        self.moralis_api_key = os.getenv("MORALIS_API_KEY", "demo-key")
    
    def get_portfolio(self, wallet_address, blockchain):
        """Get complete portfolio for a wallet"""
        try:
            if blockchain.lower() == 'ethereum':
                return self._get_ethereum_portfolio(wallet_address)
            elif blockchain.lower() == 'polygon':
                return self._get_polygon_portfolio(wallet_address)
            elif blockchain.lower() == 'solana':
                return self._get_solana_portfolio(wallet_address)
            else:
                return {"success": False, "error": f"Unsupported blockchain: {blockchain}"}
        
        except Exception as e:
            logger.error(f"Portfolio fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_ethereum_portfolio(self, wallet_address):
        """Get Ethereum portfolio"""
        try:
            # Get token balances using Moralis API
            url = f"https://deep-index.moralis.io/api/v2/{wallet_address}/erc20"
            headers = {"X-API-Key": self.moralis_api_key}
            params = {"chain": "eth"}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch token balances"}
            
            tokens_data = response.json()
            
            # Get ETH balance
            eth_balance = self.ethereum_client.get_balance(wallet_address)
            
            # Calculate portfolio value
            portfolio = {
                "wallet_address": wallet_address,
                "blockchain": "ethereum",
                "tokens": [],
                "total_value_usd": 0.0,
                "last_updated": self._get_current_timestamp()
            }
            
            # Add ETH
            eth_price = self._get_token_price("ethereum")
            eth_value = float(eth_balance) * eth_price
            
            portfolio["tokens"].append({
                "symbol": "ETH",
                "name": "Ethereum",
                "address": "0x0000000000000000000000000000000000000000",
                "balance": eth_balance,
                "price_usd": eth_price,
                "value_usd": eth_value,
                "decimals": 18
            })
            
            portfolio["total_value_usd"] += eth_value
            
            # Add ERC20 tokens
            for token in tokens_data:
                if float(token.get('balance', 0)) > 0:
                    token_price = self._get_token_price_by_address(token['token_address'])
                    token_balance_formatted = float(token['balance']) / (10 ** int(token.get('decimals', 18)))
                    token_value = token_balance_formatted * token_price
                    
                    portfolio["tokens"].append({
                        "symbol": token.get('symbol', 'UNKNOWN'),
                        "name": token.get('name', 'Unknown Token'),
                        "address": token['token_address'],
                        "balance": str(token_balance_formatted),
                        "price_usd": token_price,
                        "value_usd": token_value,
                        "decimals": int(token.get('decimals', 18))
                    })
                    
                    portfolio["total_value_usd"] += token_value
            
            return {"success": True, "portfolio": portfolio}
        
        except Exception as e:
            logger.error(f"Ethereum portfolio fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_polygon_portfolio(self, wallet_address):
        """Get Polygon portfolio"""
        try:
            # Similar to Ethereum but using Polygon chain
            url = f"https://deep-index.moralis.io/api/v2/{wallet_address}/erc20"
            headers = {"X-API-Key": self.moralis_api_key}
            params = {"chain": "polygon"}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code != 200:
                return {"success": False, "error": "Failed to fetch token balances"}
            
            tokens_data = response.json()
            
            # Get MATIC balance
            matic_balance = self.polygon_client.get_balance(wallet_address)
            
            portfolio = {
                "wallet_address": wallet_address,
                "blockchain": "polygon",
                "tokens": [],
                "total_value_usd": 0.0,
                "last_updated": self._get_current_timestamp()
            }
            
            # Add MATIC
            matic_price = self._get_token_price("matic-network")
            matic_value = float(matic_balance) * matic_price
            
            portfolio["tokens"].append({
                "symbol": "MATIC",
                "name": "Polygon",
                "address": "0x0000000000000000000000000000000000000000",
                "balance": matic_balance,
                "price_usd": matic_price,
                "value_usd": matic_value,
                "decimals": 18
            })
            
            portfolio["total_value_usd"] += matic_value
            
            # Add ERC20 tokens on Polygon
            for token in tokens_data:
                if float(token.get('balance', 0)) > 0:
                    token_price = self._get_token_price_by_address(token['token_address'], "polygon")
                    token_balance_formatted = float(token['balance']) / (10 ** int(token.get('decimals', 18)))
                    token_value = token_balance_formatted * token_price
                    
                    portfolio["tokens"].append({
                        "symbol": token.get('symbol', 'UNKNOWN'),
                        "name": token.get('name', 'Unknown Token'),
                        "address": token['token_address'],
                        "balance": str(token_balance_formatted),
                        "price_usd": token_price,
                        "value_usd": token_value,
                        "decimals": int(token.get('decimals', 18))
                    })
                    
                    portfolio["total_value_usd"] += token_value
            
            return {"success": True, "portfolio": portfolio}
        
        except Exception as e:
            logger.error(f"Polygon portfolio fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_solana_portfolio(self, wallet_address):
        """Get Solana portfolio"""
        try:
            # Get SOL balance
            sol_balance = self.solana_client.get_balance(wallet_address)
            
            # Get SPL token balances
            spl_tokens = self.solana_client.get_token_accounts(wallet_address)
            
            portfolio = {
                "wallet_address": wallet_address,
                "blockchain": "solana",
                "tokens": [],
                "total_value_usd": 0.0,
                "last_updated": self._get_current_timestamp()
            }
            
            # Add SOL
            sol_price = self._get_token_price("solana")
            sol_value = float(sol_balance) * sol_price
            
            portfolio["tokens"].append({
                "symbol": "SOL",
                "name": "Solana",
                "address": "So11111111111111111111111111111111111111112",
                "balance": sol_balance,
                "price_usd": sol_price,
                "value_usd": sol_value,
                "decimals": 9
            })
            
            portfolio["total_value_usd"] += sol_value
            
            # Add SPL tokens
            for token in spl_tokens:
                if float(token.get('balance', 0)) > 0:
                    token_info = self._get_solana_token_info(token['mint'])
                    token_price = self._get_token_price_by_address(token['mint'], "solana")
                    token_balance_formatted = float(token['balance']) / (10 ** token_info.get('decimals', 9))
                    token_value = token_balance_formatted * token_price
                    
                    portfolio["tokens"].append({
                        "symbol": token_info.get('symbol', 'UNKNOWN'),
                        "name": token_info.get('name', 'Unknown Token'),
                        "address": token['mint'],
                        "balance": str(token_balance_formatted),
                        "price_usd": token_price,
                        "value_usd": token_value,
                        "decimals": token_info.get('decimals', 9)
                    })
                    
                    portfolio["total_value_usd"] += token_value
            
            return {"success": True, "portfolio": portfolio}
        
        except Exception as e:
            logger.error(f"Solana portfolio fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_positions(self, wallet_address, blockchain):
        """Get DeFi positions for a wallet"""
        try:
            positions = {
                "wallet_address": wallet_address,
                "blockchain": blockchain,
                "lending_positions": [],
                "farming_positions": [],
                "staking_positions": [],
                "total_value_locked": 0.0,
                "last_updated": self._get_current_timestamp()
            }
            
            if blockchain.lower() == 'ethereum':
                # Get Aave positions
                aave_positions = self._get_aave_positions(wallet_address, "ethereum")
                positions["lending_positions"].extend(aave_positions)
                
                # Get Compound positions
                compound_positions = self._get_compound_positions(wallet_address)
                positions["lending_positions"].extend(compound_positions)
                
                # Get Uniswap LP positions
                uniswap_positions = self._get_uniswap_positions(wallet_address)
                positions["farming_positions"].extend(uniswap_positions)
            
            elif blockchain.lower() == 'polygon':
                # Get Aave positions on Polygon
                aave_positions = self._get_aave_positions(wallet_address, "polygon")
                positions["lending_positions"].extend(aave_positions)
                
                # Get QuickSwap LP positions
                quickswap_positions = self._get_quickswap_positions(wallet_address)
                positions["farming_positions"].extend(quickswap_positions)
            
            elif blockchain.lower() == 'solana':
                # Get Solana DeFi positions
                raydium_positions = self._get_raydium_positions(wallet_address)
                positions["farming_positions"].extend(raydium_positions)
            
            # Calculate total value locked
            for pos_list in [positions["lending_positions"], positions["farming_positions"], positions["staking_positions"]]:
                for pos in pos_list:
                    positions["total_value_locked"] += pos.get("value_usd", 0.0)
            
            return {"success": True, "positions": positions}
        
        except Exception as e:
            logger.error(f"Positions fetch failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_portfolio_analytics(self, wallet_address, blockchain, timeframe="7d"):
        """Get portfolio analytics and performance"""
        try:
            analytics = {
                "wallet_address": wallet_address,
                "blockchain": blockchain,
                "timeframe": timeframe,
                "performance": {
                    "total_return": 0.0,
                    "total_return_percentage": 0.0,
                    "best_performing_asset": None,
                    "worst_performing_asset": None
                },
                "allocation": [],
                "risk_metrics": {
                    "volatility": 0.0,
                    "sharpe_ratio": 0.0,
                    "max_drawdown": 0.0
                },
                "yield_earned": {
                    "total_yield_usd": 0.0,
                    "average_apy": 0.0,
                    "yield_sources": []
                }
            }
            
            # Get current portfolio
            portfolio_result = self.get_portfolio(wallet_address, blockchain)
            if not portfolio_result["success"]:
                return portfolio_result
            
            portfolio = portfolio_result["portfolio"]
            
            # Calculate allocation
            total_value = portfolio["total_value_usd"]
            for token in portfolio["tokens"]:
                if total_value > 0:
                    allocation_percentage = (token["value_usd"] / total_value) * 100
                    analytics["allocation"].append({
                        "symbol": token["symbol"],
                        "name": token["name"],
                        "value_usd": token["value_usd"],
                        "percentage": allocation_percentage
                    })
            
            # Get DeFi positions for yield calculation
            positions_result = self.get_positions(wallet_address, blockchain)
            if positions_result["success"]:
                positions = positions_result["positions"]
                
                # Calculate yield from lending
                for lending_pos in positions["lending_positions"]:
                    if "apy" in lending_pos and "value_usd" in lending_pos:
                        annual_yield = lending_pos["value_usd"] * (lending_pos["apy"] / 100)
                        analytics["yield_earned"]["total_yield_usd"] += annual_yield
                        analytics["yield_earned"]["yield_sources"].append({
                            "protocol": lending_pos["protocol"],
                            "type": "lending",
                            "annual_yield_usd": annual_yield,
                            "apy": lending_pos["apy"]
                        })
                
                # Calculate yield from farming
                for farming_pos in positions["farming_positions"]:
                    if "apy" in farming_pos and "value_usd" in farming_pos:
                        annual_yield = farming_pos["value_usd"] * (farming_pos["apy"] / 100)
                        analytics["yield_earned"]["total_yield_usd"] += annual_yield
                        analytics["yield_earned"]["yield_sources"].append({
                            "protocol": farming_pos["protocol"],
                            "type": "farming",
                            "annual_yield_usd": annual_yield,
                            "apy": farming_pos["apy"]
                        })
            
            # Calculate average APY
            total_yield_value = sum([source["annual_yield_usd"] for source in analytics["yield_earned"]["yield_sources"]])
            if total_value > 0:
                analytics["yield_earned"]["average_apy"] = (total_yield_value / total_value) * 100
            
            return {"success": True, "analytics": analytics}
        
        except Exception as e:
            logger.error(f"Portfolio analytics failed: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _get_token_price(self, token_id):
        """Get token price from CoinGecko"""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {
                "ids": token_id,
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get(token_id, {}).get("usd", 0.0)
            else:
                return 0.0
        
        except Exception as e:
            logger.error(f"Price fetch failed for {token_id}: {str(e)}")
            return 0.0
    
    def _get_token_price_by_address(self, token_address, chain="ethereum"):
        """Get token price by contract address"""
        try:
            # Map chain names to CoinGecko platform IDs
            platform_mapping = {
                "ethereum": "ethereum",
                "polygon": "polygon-pos",
                "solana": "solana"
            }
            
            platform = platform_mapping.get(chain, "ethereum")
            
            url = f"https://api.coingecko.com/api/v3/simple/token_price/{platform}"
            params = {
                "contract_addresses": token_address,
                "vs_currencies": "usd"
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get(token_address.lower(), {}).get("usd", 0.0)
            else:
                return 0.0
        
        except Exception as e:
            logger.error(f"Price fetch failed for {token_address}: {str(e)}")
            return 0.0
    
    def _get_solana_token_info(self, mint_address):
        """Get Solana token information"""
        # This would use Solana token registry or Jupiter API
        return {
            "symbol": "UNKNOWN",
            "name": "Unknown Token",
            "decimals": 9
        }
    
    def _get_aave_positions(self, wallet_address, blockchain):
        """Get Aave positions"""
        # This would query Aave's data provider contracts
        return []
    
    def _get_compound_positions(self, wallet_address):
        """Get Compound positions"""
        # This would query Compound's contracts
        return []
    
    def _get_uniswap_positions(self, wallet_address):
        """Get Uniswap LP positions"""
        # This would query Uniswap subgraph
        return []
    
    def _get_quickswap_positions(self, wallet_address):
        """Get QuickSwap LP positions"""
        # This would query QuickSwap subgraph
        return []
    
    def _get_raydium_positions(self, wallet_address):
        """Get Raydium positions"""
        # This would query Raydium API
        return []
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()
