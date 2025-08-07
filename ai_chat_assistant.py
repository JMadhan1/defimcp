
import logging
import openai
from typing import Dict, List, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class AIChatAssistant:
    def __init__(self, openai_api_key: str = None):
        self.openai_api_key = openai_api_key
        if openai_api_key:
            openai.api_key = openai_api_key
        
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
        """Get AI-powered response using OpenAI"""
        try:
            # Build context for AI
            context = self._build_context()
            
            # Create system prompt
            system_prompt = f"""
            You are an expert DeFi financial advisor AI with a friendly, knowledgeable personality.
            You explain complex DeFi concepts in simple terms and always provide actionable advice.
            
            User Context:
            {context}
            
            Guidelines:
            - Be conversational and helpful
            - Use emojis occasionally for friendliness
            - Explain DeFi terms simply
            - Always consider the user's portfolio when giving advice
            - If you can't do something, suggest alternatives
            - Be encouraging but honest about risks
            """
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add recent conversation history
            for conv in self.conversation_history[-3:]:
                messages.append({"role": "user", "content": conv["user"]})
                messages.append({"role": "assistant", "content": conv["ai"]})
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=300,
                temperature=0.7
            )
            
            ai_message = response.choices[0].message.content.strip()
            
            # Generate suggestions based on message
            suggestions = self._generate_suggestions(user_message, ai_message)
            
            return {
                "message": ai_message,
                "suggestions": suggestions,
                "type": "ai_response"
            }
            
        except Exception as e:
            logger.warning(f"OpenAI response failed: {e}")
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
        """Fallback response when AI is unavailable"""
        user_message_lower = user_message.lower()
        
        # Pattern matching for common queries
        if any(word in user_message_lower for word in ["why", "moved", "transaction"]):
            return {
                "message": "I can see you're asking about recent transactions! While I'd love to give you detailed AI insights, you can check your transaction history in the dashboard. Each transaction shows the protocol used and the reasoning behind automated moves. 📊",
                "suggestions": ["View transaction history", "Check portfolio health", "Get strategy advice"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["buy", "should", "recommend"]):
            return {
                "message": "Great question about investment decisions! Based on your portfolio, I'd recommend checking your current allocation first. Generally, maintaining 20-30% in stable assets is wise, with the rest in quality DeFi opportunities. Want me to analyze your portfolio health? 💡",
                "suggestions": ["Analyze portfolio health", "Create investment strategy", "Check yield opportunities"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["gas", "fees", "expensive"]):
            return {
                "message": "Ah, the eternal crypto struggle - gas fees! 😅 If you're on Ethereum and fees are high, consider moving some assets to Polygon or other L2s. You can save 90%+ on transaction costs while earning similar yields. Want me to show you how? ⛽",
                "suggestions": ["Compare network fees", "Move to Polygon", "Optimize gas usage"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["yield", "earn", "apy"]):
            return {
                "message": "Looking to boost those yields? Smart move! 📈 The best approach depends on your risk tolerance. Safe options include USDC lending on Aave (4-6% APY), while higher yields come from farming (10%+ but higher risk). What's your risk appetite?",
                "suggestions": ["Find yield opportunities", "Compare lending rates", "Explore yield farming"],
                "type": "fallback"
            }
        
        elif any(word in user_message_lower for word in ["help", "how", "what"]):
            return {
                "message": "I'm here to help with all your DeFi questions! 🤖 I can analyze your portfolio health, suggest investment strategies, explain transactions, and help optimize your yields. What would you like to explore first?",
                "suggestions": ["Analyze portfolio", "Create strategy", "Explain DeFi concepts", "Check opportunities"],
                "type": "fallback"
            }
        
        else:
            return {
                "message": "Thanks for chatting! I'm your DeFi assistant and I'm here to help optimize your portfolio. While I'm best with AI powers enabled, I can still help you navigate DeFi basics. What would you like to know? 🚀",
                "suggestions": ["Ask about DeFi", "Check portfolio", "Get strategy help", "Learn about yields"],
                "type": "fallback"
            }
    
    def _generate_suggestions(self, user_message: str, ai_response: str) -> List[str]:
        """Generate contextual suggestions"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["portfolio", "holdings"]):
            return ["Run portfolio health check", "Optimize allocation", "Find yield opportunities"]
        elif any(word in user_lower for word in ["transaction", "moved", "why"]):
            return ["View transaction details", "Check recent activity", "Explain strategy"]
        elif any(word in user_lower for word in ["strategy", "invest", "recommend"]):
            return ["Create custom strategy", "Check risk tolerance", "Compare options"]
        elif any(word in user_lower for word in ["yield", "earn", "apy"]):
            return ["Find best yields", "Compare protocols", "Calculate returns"]
        else:
            return ["Analyze portfolio", "Get recommendations", "Check opportunities", "Learn DeFi basics"]
    
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
