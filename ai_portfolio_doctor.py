import logging
import openai
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AIPortfolioDoctor:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key

    def diagnose_portfolio(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze portfolio and return health diagnosis"""
        try:
            # Calculate health metrics
            health_score = self._calculate_health_score(portfolio_data)
            symptoms = self._identify_symptoms(portfolio_data)
            treatment_plan = self._generate_treatment_plan(portfolio_data, symptoms)

            # Get AI insights if OpenAI is available
            ai_diagnosis = self._get_ai_diagnosis(portfolio_data, health_score, symptoms)

            return {
                "health_score": health_score,
                "diagnosis": self._get_diagnosis_text(health_score),
                "symptoms": symptoms,
                "treatment_plan": treatment_plan,
                "ai_insights": ai_diagnosis,
                "visual_indicator": self._get_health_color(health_score),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Portfolio diagnosis failed: {e}")
            return self._fallback_diagnosis()

    def _calculate_health_score(self, portfolio_data: Dict[str, Any]) -> int:
        """Calculate portfolio health score (0-100)"""
        score = 100
        tokens = portfolio_data.get("tokens", [])
        total_value = portfolio_data.get("total_value_usd", 0)

        if not tokens or total_value == 0:
            return 20

        # Diversification check
        if len(tokens) < 3:
            score -= 20  # Poor diversification
        elif len(tokens) > 10:
            score -= 10  # Over-diversification

        # Concentration risk
        for token in tokens:
            percentage = token.get("percentage", 0)
            if percentage > 50:
                score -= 30  # High concentration risk
            elif percentage > 30:
                score -= 15

        # Stable coin allocation
        stable_coins = ["USDC", "USDT", "DAI", "BUSD"]
        stable_percentage = sum(
            token.get("percentage", 0) 
            for token in tokens 
            if token.get("symbol", "").upper() in stable_coins
        )

        if stable_percentage < 10:
            score -= 15  # Too volatile
        elif stable_percentage > 70:
            score -= 10  # Too conservative

        # Yield opportunities
        yield_earning = any(
            token.get("yield_apy", 0) > 0 
            for token in tokens
        )
        if not yield_earning:
            score -= 15  # Missing yield opportunities

        return max(0, min(100, score))

    def _identify_symptoms(self, portfolio_data: Dict[str, Any]) -> List[str]:
        """Identify portfolio health symptoms"""
        symptoms = []
        tokens = portfolio_data.get("tokens", [])
        total_value = portfolio_data.get("total_value_usd", 0)

        # Check concentration
        for token in tokens:
            percentage = token.get("percentage", 0)
            if percentage > 40:
                symptoms.append(f"{percentage:.0f}% concentrated in {token.get('symbol', 'unknown')} - high risk!")

        # Check diversification
        if len(tokens) < 3:
            symptoms.append("Poor diversification - only holding a few assets")

        # Check stable coin allocation
        stable_coins = ["USDC", "USDT", "DAI", "BUSD"]
        stable_percentage = sum(
            token.get("percentage", 0) 
            for token in tokens 
            if token.get("symbol", "").upper() in stable_coins
        )

        if stable_percentage < 10:
            symptoms.append("Missing stable assets for risk management")
        elif stable_percentage > 70:
            symptoms.append("Too conservative - missing growth opportunities")

        # Check yield opportunities
        yield_earning = any(
            token.get("yield_apy", 0) > 0 
            for token in tokens
        )
        if not yield_earning:
            symptoms.append("Missing yield opportunities - money sitting idle")

        # Gas fee analysis (simulated)
        if any(token.get("blockchain") == "ethereum" for token in tokens):
            symptoms.append("High gas fees on Ethereum - consider L2 alternatives")

        return symptoms

    def _generate_treatment_plan(self, portfolio_data: Dict[str, Any], symptoms: List[str]) -> List[str]:
        """Generate treatment recommendations"""
        treatments = []
        tokens = portfolio_data.get("tokens", [])

        # Diversification treatments
        if len(tokens) < 3:
            treatments.append("Add 2-3 more quality assets to improve diversification")

        # Concentration treatments
        for token in tokens:
            percentage = token.get("percentage", 0)
            if percentage > 40:
                treatments.append(f"Reduce {token.get('symbol')} position to under 30%")

        # Stable coin treatments
        stable_coins = ["USDC", "USDT", "DAI", "BUSD"]
        stable_percentage = sum(
            token.get("percentage", 0) 
            for token in tokens 
            if token.get("symbol", "").upper() in stable_coins
        )

        if stable_percentage < 10:
            treatments.append("Allocate 20-30% to stable assets (USDC/DAI)")
        elif stable_percentage > 70:
            treatments.append("Increase growth allocation - add ETH or quality DeFi tokens")

        # Yield treatments
        yield_earning = any(
            token.get("yield_apy", 0) > 0 
            for token in tokens
        )
        if not yield_earning:
            treatments.append("Start earning yield - lend USDC on Aave for 4-6% APY")

        # Gas optimization
        if any(token.get("blockchain") == "ethereum" for token in tokens):
            treatments.append("Move some assets to Polygon for 99% lower fees")

        return treatments

    def _get_ai_diagnosis(self, portfolio_data: Dict[str, Any], health_score: int, symptoms: List[str]) -> str:
        """Get AI-powered diagnosis using OpenAI"""
        if not self.openai_api_key or openai is None:
            return "Connect OpenAI for AI-powered insights"

        try:
            # Use modern OpenAI client (v1.0+)
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key, base_url="https://api.comput3.ai/v1")

            response = client.chat.completions.create(
                model="llama3:70b",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI diagnosis failed: {e}")
            return self._fallback_ai_diagnosis(health_score)

    def _fallback_ai_diagnosis(self, health_score: int) -> str:
        """Fallback AI diagnosis when OpenAI is unavailable"""
        if health_score >= 80:
            return "Your portfolio is in excellent health! Just like a well-balanced diet, you're diversified and earning steady returns. Keep up the great work! 💪"
        elif health_score >= 60:
            return "Your portfolio has moderate health. Think of it like having slightly high cholesterol - not dangerous, but some lifestyle changes could really help optimize your returns! 📈"
        elif health_score >= 40:
            return "Your portfolio needs attention. Like visiting a doctor for chest pains, these concentration risks could cause problems. Time for some portfolio medicine! 🏥"
        else:
            return "Your portfolio is in critical condition! Just like emergency surgery, immediate action needed to reduce risks and start earning proper returns. Don't panic - we can fix this! 🚨"

    def _get_diagnosis_text(self, health_score: int) -> str:
        """Get diagnosis category text"""
        if health_score >= 80:
            return "Excellent Health"
        elif health_score >= 60:
            return "Good Health"
        elif health_score >= 40:
            return "Moderate Risk"
        else:
            return "High Risk - Needs Attention"

    def _get_health_color(self, health_score: int) -> str:
        """Get color for health indicator"""
        if health_score >= 80:
            return "success"  # Green
        elif health_score >= 60:
            return "warning"  # Yellow
        else:
            return "danger"   # Red

    def _fallback_diagnosis(self) -> Dict[str, Any]:
        """Fallback diagnosis when analysis fails"""
        return {
            "health_score": 50,
            "diagnosis": "Analysis Unavailable",
            "symptoms": ["Unable to analyze portfolio data"],
            "treatment_plan": ["Check wallet connection and try again"],
            "ai_insights": "Portfolio analysis service temporarily unavailable",
            "visual_indicator": "warning",
            "timestamp": datetime.utcnow().isoformat()
        }