import json
import requests
import logging
from typing import Dict, Any, Optional
import time
import random
import os

# New imports for AI features
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

from ai_portfolio_doctor import AIPortfolioDoctor
from ai_strategy_sommelier import AIStrategySommelier
from ai_chat_assistant import AIChatAssistant

logger = logging.getLogger(__name__)

class DeFiAIAgent:
    """AI Agent that can interact with DeFi MCP Server using Comput3 AI"""

    def __init__(self, mcp_server_url: str = "http://localhost:5000", api_key: str = None):
        self.mcp_server_url = mcp_server_url
        self.api_key = api_key
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({'X-API-Key': self.api_key})

        # Comput3 AI configuration
        self.openai_api_key = os.getenv('OPENAI_API_KEY', 'c3_api_key')
        self.openai_api_url = os.getenv('OPENAI_API_URL', 'https://api.comput3.ai/v1')
        self.small_model = os.getenv('SMALL_OPENAI_MODEL', 'llama3:70b')
        self.medium_model = os.getenv('MEDIUM_OPENAI_MODEL', 'llama3:70b')
        self.large_model = os.getenv('LARGE_OPENAI_MODEL', 'llama3:70b')

        # Initialize AI components
        self.portfolio_doctor = AIPortfolioDoctor(self.openai_api_key)
        self.strategy_sommelier = AIStrategySommelier(self.openai_api_key)
        self.chat_assistant = AIChatAssistant(self.openai_api_key)

        # AI decision-making parameters
        self.risk_tolerance = 0.3  # Low to medium risk
        self.max_position_size = 0.1  # Max 10% of portfolio per position
        self.target_apy = 0.05  # Target 5% APY minimum

        logger.info(f"DeFi AI Agent initialized with MCP server: {mcp_server_url}")
        logger.info(f"Using Comput3 AI endpoint: {self.openai_api_url}")

    def make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a JSON-RPC request to the MCP server"""
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": random.randint(1, 10000)
        }

        try:
            response = self.session.post(f"{self.mcp_server_url}/mcp", json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"MCP request failed: {e}")
            return {"error": str(e)}

    def ask_ai(self, prompt: str, model: str = None) -> str:
        """Ask Comput3 AI for intelligent decision-making"""
        if not model:
            model = self.medium_model

        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a DeFi expert AI assistant specializing in portfolio optimization, yield farming, and risk management. Provide concise, actionable advice based on market data and DeFi best practices."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }

        try:
            response = requests.post(
                f"{self.openai_api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            return data['choices'][0]['message']['content'].strip()

        except Exception as e:
            logger.error(f"AI request failed: {e}")
            return f"AI analysis unavailable: {str(e)}"

    def analyze_portfolio(self, wallet_address: str, blockchain: str = "ethereum") -> Dict[str, Any]:
        """Analyze portfolio and make AI-powered investment decisions"""
        logger.info(f"Analyzing portfolio for wallet: {wallet_address}")

        # Get current portfolio
        portfolio_response = self.make_mcp_request("defi.portfolio", {
            "wallet_address": wallet_address,
            "blockchain": blockchain
        })

        if "error" in portfolio_response:
            logger.error(f"Failed to get portfolio: {portfolio_response['error']}")
            return {"success": False, "error": portfolio_response["error"]}

        portfolio = portfolio_response.get("result", {})

        # Get current positions
        positions_response = self.make_mcp_request("defi.positions", {
            "wallet_address": wallet_address,
            "blockchain": blockchain
        })

        positions = positions_response.get("result", {}).get("positions", []) if "result" in positions_response else []

        # Basic analysis
        analysis = {
            "total_value": portfolio.get("total_value_usd", 0),
            "token_count": len(portfolio.get("tokens", [])),
            "position_count": len(positions),
            "diversification_score": self._calculate_diversification(portfolio),
            "yield_potential": self._analyze_yield_opportunities(positions),
            "recommendations": []
        }

        # Get AI insights using the Portfolio Doctor
        ai_prompt = f"""
        Analyze this DeFi portfolio:
        - Total Value: ${analysis['total_value']:,.2f}
        - Tokens: {analysis['token_count']}
        - Active Positions: {analysis['position_count']}
        - Diversification Score: {analysis['diversification_score']}
        - Average APY: {analysis['yield_potential']['average_apy']:.1%}

        Portfolio tokens: {[token.get('symbol', 'Unknown') + f" ({token.get('percentage', 0):.1f}%)" for token in portfolio.get('tokens', [])]}

        Provide 3 specific recommendations for optimization focusing on:
        1. Risk management
        2. Yield optimization  
        3. Diversification improvements

        Consider current DeFi market conditions and return brief, actionable advice.
        """

        ai_insights = self.portfolio_doctor.analyze_portfolio_health(portfolio, analysis) # Use Portfolio Doctor
        analysis["ai_insights"] = ai_insights # Store AI insights

        # Generate traditional recommendations
        analysis["recommendations"] = self._generate_recommendations(portfolio, positions, analysis)


        return {"success": True, "analysis": analysis}

    def execute_strategy(self, wallet_address: str, strategy: str = "ai_optimized", blockchain: str = "ethereum") -> Dict[str, Any]:
        """Execute an AI-powered DeFi strategy"""
        logger.info(f"Executing {strategy} strategy for wallet: {wallet_address}")

        # First analyze the portfolio
        analysis_result = self.analyze_portfolio(wallet_address, blockchain)
        if not analysis_result["success"]:
            return analysis_result

        analysis = analysis_result["analysis"]
        executed_actions = []

        # Get AI strategy recommendations using the Strategy Sommelier
        if strategy == "ai_optimized":
            actions = self.strategy_sommelier.get_strategy_actions(wallet_address, blockchain, analysis)
        elif strategy == "conservative_yield":
            actions = self._conservative_yield_strategy(wallet_address, blockchain, analysis)
        elif strategy == "aggressive_farming":
            actions = self._aggressive_farming_strategy(wallet_address, blockchain, analysis)
        elif strategy == "balanced_portfolio":
            actions = self._balanced_portfolio_strategy(wallet_address, blockchain, analysis)
        else:
            return {"success": False, "error": f"Unknown strategy: {strategy}"}

        # Execute each action
        for action in actions:
            try:
                result = self._execute_action(action)
                executed_actions.append({
                    "action": action,
                    "result": result,
                    "success": "error" not in result
                })

                # Wait between actions to avoid rate limits
                time.sleep(2)

            except Exception as e:
                logger.error(f"Failed to execute action {action}: {e}")
                executed_actions.append({
                    "action": action,
                    "result": {"error": str(e)},
                    "success": False
                })

        return {
            "success": True,
            "strategy": strategy,
            "analysis": analysis,
            "executed_actions": executed_actions,
            "summary": self._generate_execution_summary(executed_actions)
        }

    def _calculate_diversification(self, portfolio: Dict[str, Any]) -> float:
        """Calculate portfolio diversification score (0-1)"""
        tokens = portfolio.get("tokens", [])
        if not tokens:
            return 0.0

        # Simple diversification: more tokens = more diversified
        # In reality, this would consider correlations, sectors, etc.
        token_count = len(tokens)
        max_allocation = max([float(token.get("percentage", 0)) for token in tokens] + [0])

        # Penalize high concentration
        diversification = min(1.0, token_count / 10) * (1 - max_allocation / 100)
        return round(diversification, 2)

    def _analyze_yield_opportunities(self, positions: list) -> Dict[str, Any]:
        """Analyze current yield-generating positions"""
        total_yield = 0
        active_positions = 0

        for position in positions:
            if position.get("position_type") in ["lending", "farming"]:
                active_positions += 1
                apy = float(position.get("apy", 0))
                total_yield += apy

        avg_yield = total_yield / active_positions if active_positions > 0 else 0

        return {
            "active_positions": active_positions,
            "average_apy": round(avg_yield, 2),
            "total_estimated_yield": round(total_yield, 2),
            "yield_rating": "High" if avg_yield > 0.08 else "Medium" if avg_yield > 0.04 else "Low"
        }

    def _generate_recommendations(self, portfolio: Dict[str, Any], positions: list, analysis: Dict[str, Any]) -> list:
        """Generate AI-driven recommendations"""
        recommendations = []

        # Diversification recommendations
        if analysis["diversification_score"] < 0.3:
            recommendations.append({
                "type": "diversification",
                "priority": "high",
                "action": "Increase portfolio diversification by adding more tokens",
                "reason": f"Current diversification score: {analysis['diversification_score']}"
            })

        # Yield optimization
        if analysis["yield_potential"]["average_apy"] < self.target_apy:
            recommendations.append({
                "type": "yield_optimization",
                "priority": "medium",
                "action": "Consider lending assets to earn higher yields",
                "reason": f"Current average APY ({analysis['yield_potential']['average_apy']:.1%}) is below target ({self.target_apy:.1%})"
            })

        # Position sizing
        tokens = portfolio.get("tokens", [])
        for token in tokens:
            percentage = float(token.get("percentage", 0))
            if percentage > self.max_position_size * 100:
                recommendations.append({
                    "type": "risk_management",
                    "priority": "medium",
                    "action": f"Consider reducing {token.get('symbol', 'unknown')} position size",
                    "reason": f"Position size ({percentage:.1f}%) exceeds recommended maximum ({self.max_position_size*100:.1f}%)"
                })

        return recommendations

    def _ai_optimized_strategy(self, wallet_address: str, blockchain: str, analysis: Dict[str, Any]) -> list:
        """Generate AI-optimized actions based on portfolio analysis"""
        ai_prompt = f"""
        Based on this DeFi portfolio analysis, suggest 2-3 specific actions:

        Portfolio Summary:
        - Total Value: ${analysis['total_value']:,.2f}
        - Diversification Score: {analysis['diversification_score']}
        - Current Average APY: {analysis['yield_potential']['average_apy']:.1%}
        - Active Positions: {analysis['yield_potential']['active_positions']}

        Available actions:
        1. LEND - Lend tokens to protocols like Aave or Compound
        2. SWAP - Swap tokens for better diversification
        3. FARM - Add liquidity to yield farming pools
        4. WITHDRAW - Remove from underperforming positions

        Respond with a JSON array of actions, each with:
        - "action_type": "lend"|"swap"|"farm"|"withdraw"
        - "reasoning": "why this action"
        - "priority": "high"|"medium"|"low"
        - "risk_level": "low"|"medium"|"high"

        Focus on optimizing yield while managing risk. Consider current market conditions.
        """

        ai_response = self.ask_ai(ai_prompt, self.large_model)

        # Parse AI response and convert to executable actions
        actions = []
        try:
            # Try to extract JSON from AI response
            import re
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                ai_actions = json.loads(json_match.group())

                for ai_action in ai_actions[:3]:  # Limit to 3 actions
                    if ai_action.get("action_type") == "lend":
                        actions.append({
                            "type": "lend",
                            "method": "defi.lend",
                            "params": {
                                "wallet_address": wallet_address,
                                "blockchain": blockchain,
                                "protocol": "aave",
                                "token": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",  # USDC
                                "amount": "100"
                            },
                            "ai_reasoning": ai_action.get("reasoning", ""),
                            "priority": ai_action.get("priority", "medium")
                        })
                    elif ai_action.get("action_type") == "swap":
                        actions.append({
                            "type": "swap",
                            "method": "defi.swap",
                            "params": {
                                "wallet_address": wallet_address,
                                "blockchain": blockchain,
                                "token_in": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
                                "token_out": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",  # USDC
                                "amount_in": "0.1",
                                "protocol": "uniswap"
                            },
                            "ai_reasoning": ai_action.get("reasoning", ""),
                            "priority": ai_action.get("priority", "medium")
                        })

        except Exception as e:
            logger.warning(f"Could not parse AI strategy response: {e}")
            # Fallback to conservative strategy
            actions = self._conservative_yield_strategy(wallet_address, blockchain, analysis)

        if not actions:
            # Fallback if no AI actions generated
            actions = self._conservative_yield_strategy(wallet_address, blockchain, analysis)

        return actions

    def _conservative_yield_strategy(self, wallet_address: str, blockchain: str, analysis: Dict[str, Any]) -> list:
        """Generate actions for conservative yield strategy"""
        actions = []

        # Focus on stable lending with established protocols
        if analysis["yield_potential"]["active_positions"] < 2:
            actions.append({
                "type": "lend",
                "method": "defi.lend",
                "params": {
                    "wallet_address": wallet_address,
                    "blockchain": blockchain,
                    "protocol": "aave",
                    "token": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",  # USDC
                    "amount": "100"  # Demo amount
                }
            })

        return actions

    def _aggressive_farming_strategy(self, wallet_address: str, blockchain: str, analysis: Dict[str, Any]) -> list:
        """Generate actions for aggressive farming strategy"""
        actions = []

        # Add liquidity to high-yield pools
        actions.append({
            "type": "farm",
            "method": "defi.farm",
            "params": {
                "wallet_address": wallet_address,
                "blockchain": blockchain,
                "protocol": "uniswap",
                "pool_id": "USDC-ETH-0.3%",
                "token_a": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",  # USDC
                "token_b": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
                "amount_a": "50",
                "amount_b": "0.02"
            }
        })

        return actions

    def _balanced_portfolio_strategy(self, wallet_address: str, blockchain: str, analysis: Dict[str, Any]) -> list:
        """Generate actions for balanced portfolio strategy"""
        actions = []

        # Mix of swapping for diversification and yield farming
        if analysis["diversification_score"] < 0.5:
            actions.append({
                "type": "swap",
                "method": "defi.swap",
                "params": {
                    "wallet_address": wallet_address,
                    "blockchain": blockchain,
                    "token_in": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH
                    "token_out": "0xA0b86a33E6411D426C3d77A6CF0C0DFEcb7fD9A9",  # USDC
                    "amount_in": "0.1",
                    "protocol": "uniswap"
                }
            })

        return actions

    def _execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single DeFi action via MCP"""
        method = action.get("method")
        params = action.get("params", {})

        if not method:
            return {"error": "No method specified in action"}

        return self.make_mcp_request(method, params)

    def _generate_execution_summary(self, executed_actions: list) -> Dict[str, Any]:
        """Generate summary of executed actions"""
        successful = sum(1 for action in executed_actions if action["success"])
        failed = len(executed_actions) - successful

        return {
            "total_actions": len(executed_actions),
            "successful": successful,
            "failed": failed,
            "success_rate": round(successful / len(executed_actions) * 100, 1) if executed_actions else 0
        }

    def run_monitoring_loop(self, wallet_address: str, check_interval: int = 300):
        """Run continuous monitoring and optimization"""
        logger.info(f"Starting monitoring loop for wallet: {wallet_address}")
        logger.info(f"Check interval: {check_interval} seconds")

        while True:
            try:
                logger.info("Running portfolio analysis...")
                analysis = self.analyze_portfolio(wallet_address)

                if analysis["success"]:
                    recommendations = analysis["analysis"]["recommendations"]

                    if recommendations:
                        logger.info(f"Found {len(recommendations)} recommendations")
                        for rec in recommendations:
                            logger.info(f"- {rec['type']}: {rec['action']}")
                    else:
                        logger.info("No recommendations at this time")
                else:
                    logger.error(f"Analysis failed: {analysis.get('error', 'Unknown error')}")

                logger.info(f"Sleeping for {check_interval} seconds...")
                time.sleep(check_interval)

            except KeyboardInterrupt:
                logger.info("Monitoring loop stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait a minute before retrying

def main():
    """Demo function to show the AI agent in action"""
    print("🤖 ONEDeFi AI Agent Demo")
    print("=" * 50)

    # Initialize agent (you would need to provide a real API key)
    agent = DeFiAIAgent(
        mcp_server_url="http://localhost:5000",
        api_key="demo_key_123"  # This would be a real API key
    )

    # Demo wallet address (this would be a real wallet)
    demo_wallet = "0x742d35Cc6641C88c4f95bbCdB96a2b0f0f3f6b7f"

    print("\n📊 Analyzing Portfolio...")
    analysis_result = agent.analyze_portfolio(demo_wallet)

    if analysis_result["success"]:
        analysis = analysis_result["analysis"]
        print(f"Portfolio Value: ${analysis['total_value']:,.2f}")
        print(f"Diversification Score: {analysis['diversification_score']}")
        print(f"Active Positions: {analysis['yield_potential']['active_positions']}")
        print(f"Average APY: {analysis['yield_potential']['average_apy']:.1%}")

        if analysis["recommendations"]:
            print("\n💡 AI Recommendations:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"{i}. [{rec['priority'].upper()}] {rec['action']}")
                print(f"   Reason: {rec['reason']}")

    print("\n🚀 Executing Conservative Yield Strategy...")
    strategy_result = agent.execute_strategy(demo_wallet, "conservative_yield")

    if strategy_result["success"]:
        summary = strategy_result["summary"]
        print(f"Executed {summary['total_actions']} actions")
        print(f"Success rate: {summary['success_rate']}%")

    print("\n✅ Demo completed!")

if __name__ == "__main__":
    main()