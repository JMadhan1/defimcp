
import logging
from typing import Dict, List, Any
from datetime import datetime
import json
import os
import requests

logger = logging.getLogger(__name__)

class AIChatAssistant:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY', 'c3_api_key')
        self.openai_api_url = os.getenv('OPENAI_API_URL', 'https://api.comput3.ai/v1')
        self.model = os.getenv('OPENAI_MODEL', 'llama3:70b')
        
        # Conversation context
        self.conversation_history = []
        self.user_context = {}
    
    def chat(self, user_message: str, portfolio_data: Dict[str, Any] = None, 
             transaction_history: List[Dict] = None) -> Dict[str, Any]:
        """Handle chat conversation with context"""
        try:
            # Update context
            if portfolio_data:
                self.user_context["portfolio"] = portfolio_data
            if transaction_history:
                self.user_context["transactions"] = transaction_history[-5:]  # Last 5 transactions
            
            # Get AI response
            if self.openai_api_key:
                response = self._get_ai_response(user_message)
            else:
                response = self._get_fallback_response(user_message)
            
            # Store conversation
            self.conversation_history.append({
                "user": user_message,
                "ai": response["message"],
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Chat failed: {e}")
            return {
                "message": "Sorry, I'm having trouble understanding right now. Please try again!",
                "suggestions": ["Check portfolio", "Show transactions", "Get strategy advice"],
                "type": "error"
            }
    
    def _get_ai_response(self, user_message: str) -> Dict[str, Any]:
        """Get AI-powered response using modern OpenAI API with full NLP"""
        try:
            # Build context for AI
            context = self._build_context()
            
            # Create comprehensive system prompt for true NLP understanding
            system_prompt = f"""You are an expert DeFi financial advisor AI with deep knowledge of:
- Decentralized Finance (DeFi) protocols, yields, and strategies
- Blockchain networks (Ethereum, Polygon, Solana)
- Portfolio management and risk assessment
- Trading, lending, yield farming, and staking
- Market analysis and investment advice
- Technical analysis and on-chain data

User Portfolio Context: {context}

Personality & Communication:
- Friendly, conversational, and helpful
- Explain complex DeFi concepts in simple, everyday language  
- Use emojis occasionally (📈, 💰, 🚀, ⚠️, 🤔)
- Always provide actionable, specific advice
- Be encouraging but honest about risks
- Answer ANY question about finance, DeFi, crypto, or investment strategies

Capabilities:
- Analyze portfolio allocations and suggest improvements
- Explain why transactions happened and their benefits
- Recommend investment strategies based on risk tolerance
- Compare DeFi protocols and their yields/risks
- Help with yield farming, lending, and staking decisions
- Provide market insights and trend analysis
- Answer educational questions about blockchain and DeFi

Always give detailed, helpful responses regardless of the question complexity."""

            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }

            # Build conversation messages
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history for context
            for conv in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": conv["user"]})
                messages.append({"role": "assistant", "content": conv["ai"]})
            
            # Add current message
            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": self.model,
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0.7,
                "top_p": 0.9
            }

            # Make API request
            response = requests.post(
                f"{self.openai_api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_message = data['choices'][0]['message']['content'].strip()
                
                # Generate contextual suggestions based on the AI response
                suggestions = self._generate_smart_suggestions(user_message, ai_message)
                
                return {
                    "message": ai_message,
                    "suggestions": suggestions,
                    "type": "ai_response"
                }
            else:
                logger.warning(f"AI API returned status {response.status_code}: {response.text}")
                return self._get_fallback_response(user_message)
            
        except Exception as e:
            logger.warning(f"AI response failed: {e}")
            return self._get_fallback_response(user_message)
    
    def _build_context(self) -> str:
        """Build context string for AI"""
        context_parts = []
        
        if "portfolio" in self.user_context:
            portfolio = self.user_context["portfolio"]
            context_parts.append(f"Portfolio Value: ${portfolio.get('total_value_usd', 0):,.2f}")
            
            tokens = portfolio.get("tokens", [])
            if tokens:
                top_holdings = [f"{t.get('symbol', '')} ({t.get('percentage', 0):.1f}%)" 
                               for t in tokens[:3]]
                context_parts.append(f"Top Holdings: {', '.join(top_holdings)}")
        
        if "transactions" in self.user_context:
            recent_txs = len(self.user_context["transactions"])
            context_parts.append(f"Recent Transactions: {recent_txs}")
        
        return " | ".join(context_parts) if context_parts else "No portfolio data available"
    
    def _get_fallback_response(self, user_message: str) -> Dict[str, Any]:
        """Enhanced fallback response with better NLP understanding"""
        user_message_lower = user_message.lower()
        
        # More sophisticated pattern matching
        if any(word in user_message_lower for word in ["why", "moved", "transaction", "transfer", "swap"]):
            return {
                "message": "I can see you're asking about recent transactions! 📊 While my AI brain is temporarily offline, I can still help explain common transaction patterns. Most moves are typically for yield optimization, gas cost reduction, or portfolio rebalancing. Check your dashboard for detailed transaction history with reasoning.",
                "suggestions": ["View transaction details", "Check portfolio health", "Explain strategy logic"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["buy", "sell", "should", "recommend", "invest"]):
            return {
                "message": "Great investment question! 💡 While my full AI analysis isn't available right now, I can share some general wisdom: diversification across 3-5 quality protocols, keeping 20-30% in stablecoins, and focusing on established DeFi blue chips (Aave, Uniswap, Compound) tends to work well. What's your risk tolerance?",
                "suggestions": ["Analyze portfolio allocation", "Find safe yield opportunities", "Learn risk management"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["gas", "fees", "expensive", "cost", "ethereum"]):
            return {
                "message": "Ah, gas fees - the eternal crypto challenge! ⛽ Here's the deal: Ethereum mainnet can be pricey ($10-100+ per transaction), but Layer 2s like Polygon offer 90%+ savings. Consider batching transactions, using L2s for smaller amounts, or timing transactions during low-usage periods (weekends, early morning UTC).",
                "suggestions": ["Compare network costs", "Learn about Layer 2", "Optimize transaction timing"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["yield", "earn", "apy", "interest", "return", "profit"]):
            return {
                "message": "Yield hunting - my favorite topic! 📈 Current DeFi landscape offers: Stablecoin lending (3-8% APY, low risk), LP farming (5-20%+ but impermanent loss risk), and staking (4-12%, varies by protocol). Higher yields = higher risks. Want specific protocol recommendations?",
                "suggestions": ["Compare yield rates", "Learn about farming risks", "Find stable earnings"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["risk", "safe", "dangerous", "loss", "secure"]):
            return {
                "message": "Smart to ask about risks! ⚠️ DeFi risks include: smart contract bugs, impermanent loss (LP farming), liquidation (borrowing), and protocol governance risks. Mitigation strategies: diversify across protocols, start small, use established platforms, and never invest more than you can afford to lose.",
                "suggestions": ["Assess portfolio risks", "Learn risk mitigation", "Check protocol safety scores"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["defi", "what", "how", "explain", "learn", "understand"]):
            return {
                "message": "Love the curiosity! 🤓 DeFi (Decentralized Finance) lets you do traditional banking without banks - lending, borrowing, trading, earning interest. Key concepts: smart contracts (automated agreements), liquidity pools (shared funds for trading), and composability (protocols working together like Lego blocks).",
                "suggestions": ["Learn DeFi basics", "Explore protocols", "Understand smart contracts"],
                "type": "fallback"
            }
        
        else:
            # Intelligent response based on any financial terms
            if any(word in user_message_lower for word in ["portfolio", "balance", "holdings", "assets"]):
                message = "I see you're asking about portfolio management! 💼 Even without my full AI capabilities, I can suggest checking your asset allocation, diversification across different DeFi sectors, and monitoring for opportunities to optimize yields while managing risk."
                suggestions = ["Check portfolio health", "Optimize allocation", "Find rebalancing opportunities"]
            else:
                message = f"Thanks for the question! 🤖 While my AI is temporarily limited, I'm still here to help with DeFi strategy, yield optimization, risk assessment, and general crypto guidance. I can discuss any aspect of decentralized finance you're curious about!"
                suggestions = ["Ask about specific protocols", "Get strategy advice", "Learn DeFi concepts", "Check market opportunities"]
            
            return {
                "message": message,
                "suggestions": suggestions,
                "type": "fallback"
            }
    
    def _generate_smart_suggestions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate intelligent contextual suggestions based on conversation"""
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        suggestions = []
        
        # Portfolio-related suggestions
        if any(word in user_lower for word in ["portfolio", "holding", "balance", "allocation"]):
            suggestions.extend(["Show portfolio breakdown", "Check risk score", "Find rebalancing opportunities"])
        
        # Yield and earning suggestions
        if any(word in user_lower + [response_lower] for word in ["yield", "apy", "earn", "stake", "farm"]):
            suggestions.extend(["Compare yield rates", "Show farming opportunities", "Calculate potential returns"])
        
        # Transaction and strategy suggestions
        if any(word in user_lower for word in ["transaction", "move", "swap", "trade"]):
            suggestions.extend(["Explain transaction logic", "Show gas optimization", "View trading history"])
        
        # Learning and education suggestions
        if any(word in user_lower for word in ["what", "how", "explain", "learn", "understand"]):
            suggestions.extend(["Learn more DeFi basics", "Explore advanced strategies", "Get market insights"])
        
        # Protocol and platform suggestions
        if any(word in user_lower + [response_lower] for word in ["aave", "uniswap", "compound", "curve"]):
            suggestions.extend(["Compare protocols", "Check protocol risks", "View protocol analytics"])
        
        # Risk and safety suggestions
        if any(word in user_lower + [response_lower] for word in ["risk", "safe", "secure", "loss"]):
            suggestions.extend(["Assess portfolio risk", "Learn risk management", "Set up alerts"])
        
        # Market and price suggestions
        if any(word in user_lower for word in ["price", "market", "trend", "bull", "bear"]):
            suggestions.extend(["Get market analysis", "Check price trends", "Set price alerts"])
        
        # Default helpful suggestions if none match
        if not suggestions:
            suggestions = [
                "Analyze my portfolio health",
                "Find the best yields available", 
                "Explain current DeFi trends",
                "Help optimize my strategy"
            ]
        
        # Return up to 3 most relevant suggestions
        return suggestions[:3]
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "recent_topics": self._extract_topics(),
            "user_context": self.user_context.keys(),
            "last_interaction": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def _extract_topics(self) -> List[str]:
        """Extract main topics from conversation"""
        topics = []
        for conv in self.conversation_history:
            message = conv["user"].lower()
            if any(word in message for word in ["portfolio", "holding"]):
                topics.append("Portfolio Analysis")
            elif any(word in message for word in ["yield", "earn", "apy"]):
                topics.append("Yield Optimization")
            elif any(word in message for word in ["strategy", "invest"]):
                topics.append("Investment Strategy")
            elif any(word in message for word in ["transaction", "moved"]):
                topics.append("Transaction History")
        
        return list(set(topics))
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.user_context = {}
