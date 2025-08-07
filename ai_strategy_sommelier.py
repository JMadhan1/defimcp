
import logging
import openai
from typing import Dict, List, Any
import json
import re

logger = logging.getLogger(__name__)

class AIStrategySommelier:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
        # Predefined strategy templates
        self.strategy_templates = {
            "conservative": {
                "risk_level": "Low",
                "expected_apy": "4-6%",
                "allocation": {
                    "stable_lending": 60,
                    "liquid_staking": 30,
                    "yield_farming": 10
                },
                "personality": "Like a savings account that actually pays you"
            },
            "balanced": {
                "risk_level": "Medium",
                "expected_apy": "8-12%",
                "allocation": {
                    "stable_lending": 40,
                    "liquid_staking": 35,
                    "yield_farming": 25
                },
                "personality": "Perfect balance of safety and growth"
            },
            "aggressive": {
                "risk_level": "High",
                "expected_apy": "15-25%",
                "allocation": {
                    "stable_lending": 20,
                    "liquid_staking": 30,
                    "yield_farming": 50
                },
                "personality": "High octane fuel for maximum returns"
            }
        }
    
    def create_strategy(self, user_goals: str, portfolio_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create custom strategy based on user goals"""
        try:
            # Analyze user goals
            risk_profile = self._analyze_risk_profile(user_goals)
            strategy_type = self._determine_strategy_type(user_goals)
            
            # Get AI-enhanced strategy if available
            if self.openai_api_key:
                strategy = self._create_ai_strategy(user_goals, portfolio_data, risk_profile)
            else:
                strategy = self._create_template_strategy(strategy_type, user_goals)
            
            # Add implementation details
            strategy["implementation"] = self._generate_implementation_steps(strategy)
            strategy["risks"] = self._identify_risks(strategy)
            strategy["timeline"] = "2-4 weeks to full implementation"
            
            return strategy
            
        except Exception as e:
            logger.error(f"Strategy creation failed: {e}")
            return self._fallback_strategy()
    
    def _analyze_risk_profile(self, user_goals: str) -> str:
        """Analyze user's risk tolerance from their goals"""
        user_goals_lower = user_goals.lower()
        
        conservative_keywords = ["safe", "stable", "secure", "conservative", "scared", "losses", "retirement", "steady"]
        aggressive_keywords = ["growth", "aggressive", "maximum", "high", "risk", "moon", "gains", "fast"]
        
        conservative_score = sum(1 for keyword in conservative_keywords if keyword in user_goals_lower)
        aggressive_score = sum(1 for keyword in aggressive_keywords if keyword in user_goals_lower)
        
        if conservative_score > aggressive_score:
            return "conservative"
        elif aggressive_score > conservative_score:
            return "aggressive"
        else:
            return "balanced"
    
    def _determine_strategy_type(self, user_goals: str) -> str:
        """Determine strategy type from user goals"""
        return self._analyze_risk_profile(user_goals)
    
    def _create_ai_strategy(self, user_goals: str, portfolio_data: Dict[str, Any], risk_profile: str) -> Dict[str, Any]:
        """Create AI-enhanced strategy using OpenAI"""
        try:
            portfolio_context = ""
            if portfolio_data:
                portfolio_context = f"""
                Current Portfolio:
                - Total Value: ${portfolio_data.get('total_value_usd', 0):,.2f}
                - Assets: {len(portfolio_data.get('tokens', []))} tokens
                - Main Holdings: {', '.join([t.get('symbol', '') for t in portfolio_data.get('tokens', [])[:3]])}
                """
            
            prompt = f"""
            As an expert DeFi strategy sommelier, create a custom investment strategy for this user:
            
            User Goals: "{user_goals}"
            Risk Profile: {risk_profile}
            {portfolio_context}
            
            Return a JSON strategy with:
            1. strategy_name (creative, wine-themed name)
            2. risk_level (Low/Medium/High)
            3. expected_apy (realistic range)
            4. allocation (percentages for stable_lending, liquid_staking, yield_farming)
            5. personality (wine sommelier description with tasting notes)
            6. reasoning (why this strategy fits their goals)
            
            Make it sound like a wine sommelier describing a fine vintage!
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.8
            )
            
            # Parse AI response
            ai_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                strategy = json.loads(json_match.group())
                return strategy
            else:
                # Fallback to template with AI reasoning
                template = self.strategy_templates[risk_profile].copy()
                template["strategy_name"] = self._generate_strategy_name(user_goals, risk_profile)
                template["reasoning"] = ai_text
                return template
                
        except Exception as e:
            logger.warning(f"AI strategy creation failed: {e}")
            return self._create_template_strategy(risk_profile, user_goals)
    
    def _create_template_strategy(self, strategy_type: str, user_goals: str) -> Dict[str, Any]:
        """Create strategy from template"""
        strategy = self.strategy_templates[strategy_type].copy()
        strategy["strategy_name"] = self._generate_strategy_name(user_goals, strategy_type)
        strategy["reasoning"] = f"This {strategy_type} strategy aligns with your goals of: {user_goals[:100]}..."
        return strategy
    
    def _generate_strategy_name(self, user_goals: str, risk_profile: str) -> str:
        """Generate creative strategy names"""
        names = {
            "conservative": [
                "Steady Sipper Reserve",
                "Safe Harbor Blend",
                "Conservative Vintage",
                "Gentle Giant Portfolio"
            ],
            "balanced": [
                "Perfect Balance Bordeaux",
                "Harmony House Blend",
                "Golden Ratio Reserve",
                "Balanced Barrel Select"
            ],
            "aggressive": [
                "High Octane Vintage",
                "Maximum Yield Merlot",
                "Aggressive Growth Blend",
                "Rocket Fuel Reserve"
            ]
        }
        
        import random
        return random.choice(names.get(risk_profile, names["balanced"]))
    
    def _generate_implementation_steps(self, strategy: Dict[str, Any]) -> List[str]:
        """Generate implementation steps for the strategy"""
        allocation = strategy.get("allocation", {})
        steps = []
        
        if allocation.get("stable_lending", 0) > 0:
            steps.append(f"1. Lend {allocation['stable_lending']}% in USDC on Aave for stable returns")
        
        if allocation.get("liquid_staking", 0) > 0:
            steps.append(f"2. Stake {allocation['liquid_staking']}% in ETH liquid staking for network rewards")
        
        if allocation.get("yield_farming", 0) > 0:
            steps.append(f"3. Farm {allocation['yield_farming']}% in high-yield pools (diversified)")
        
        steps.append("4. Set up auto-compounding to maximize returns")
        steps.append("5. Monitor and rebalance monthly")
        
        return steps
    
    def _identify_risks(self, strategy: Dict[str, Any]) -> List[str]:
        """Identify strategy risks"""
        risk_level = strategy.get("risk_level", "Medium")
        allocation = strategy.get("allocation", {})
        
        risks = []
        
        if risk_level == "High":
            risks.append("High volatility in yield farming positions")
            risks.append("Smart contract risks in DeFi protocols")
        
        if allocation.get("yield_farming", 0) > 30:
            risks.append("Impermanent loss in liquidity pools")
        
        if allocation.get("stable_lending", 0) < 20:
            risks.append("Limited stable asset buffer during market downturns")
        
        risks.append("General DeFi protocol risks")
        risks.append("Market volatility affecting all crypto assets")
        
        return risks
    
    def _fallback_strategy(self) -> Dict[str, Any]:
        """Fallback strategy when creation fails"""
        return {
            "strategy_name": "Safe & Simple Starter",
            "risk_level": "Low",
            "expected_apy": "4-6%",
            "allocation": {
                "stable_lending": 70,
                "liquid_staking": 20,
                "yield_farming": 10
            },
            "personality": "A gentle introduction to DeFi, like training wheels for your portfolio",
            "reasoning": "Default safe strategy while we analyze your preferences",
            "implementation": [
                "1. Start with USDC lending on Aave",
                "2. Add small ETH staking position",
                "3. Gradually explore yield farming"
            ],
            "risks": ["Minimal risks with this conservative approach"],
            "timeline": "1-2 weeks to implement"
        }
