# Payment System

The Robutler payment system enables microtransactions for agent usage, skill monetization, and platform services.

## Overview

The payment system provides:
- **Microtransactions** - Pay-per-use pricing for agent queries
- **Credit System** - Prepaid credits for seamless usage
- **Automatic Billing** - Transparent charging for services
- **Revenue Sharing** - Monetize your agents and skills

## Basic Usage

### Payment Skill Integration

```python
from robutler.agents import BaseAgent
from robutler.agents.skills import PaymentSkill

# Add payment capability to your agent
agent = BaseAgent(
    name="premium-assistant",
    instructions="You are a premium assistant with paid features",
    model="openai/gpt-4o",
    skills={
        "payment": PaymentSkill({
            "api_key": "your-robutler-key",
            "default_amount": 0.01,  # $0.01 per query
            "currency": "USD"
        })
    }
)
```

### Charging for Services

```python
from robutler.agents.skills import Skill
from robutler.agents.tools.decorators import tool

class PremiumAnalysisSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["payment"])
    
    @tool
    async def premium_analysis(self, data: str) -> Dict:
        """Perform premium analysis (charged service)"""
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        # Charge user for premium service
        charge_result = await payment.charge_user(
            user_id=context.peer_user_id,
            amount=0.05,  # $0.05 for premium analysis
            description="Premium data analysis",
            metadata={
                "service": "premium_analysis",
                "data_size": len(data)
            }
        )
        
        if not charge_result.get("success"):
            return {
                "error": "Payment required for premium analysis",
                "payment_url": charge_result.get("payment_url"),
                "required_amount": 0.05
            }
        
        # Perform premium analysis
        analysis_result = await self._perform_premium_analysis(data)
        
        return {
            "analysis": analysis_result,
            "transaction_id": charge_result.get("transaction_id"),
            "charged": 0.05
        }
```

## Pricing Decorators

### Tool-Level Pricing

```python
from robutler.agents.tools.decorators import tool, pricing

class PaidToolsSkill(Skill):
    @tool
    @pricing(cost=0.02, currency="USD")
    def expensive_calculation(self, input_data: str) -> str:
        """Expensive calculation with automatic billing"""
        # Tool execution automatically charges user
        return self.perform_calculation(input_data)
    
    @tool
    @pricing(cost=0.01, per="request", description="Web search query")
    def web_search(self, query: str) -> List[Dict]:
        """Web search with per-request pricing"""
        return self.search_web(query)
    
    @tool
    @pricing(cost=0.001, per="token", max_cost=0.10)
    def text_processing(self, text: str) -> str:
        """Text processing with token-based pricing"""
        # Automatically calculates cost based on input tokens
        return self.process_text(text)
```

### Dynamic Pricing

```python
class DynamicPricingSkill(Skill):
    @tool
    async def smart_analysis(self, data: str, complexity: str = "medium") -> Dict:
        """Analysis with dynamic pricing based on complexity"""
        
        # Calculate price based on complexity
        pricing_tiers = {
            "basic": 0.01,
            "medium": 0.03,
            "advanced": 0.08
        }
        
        cost = pricing_tiers.get(complexity, 0.03)
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        # Charge based on complexity
        charge_result = await payment.charge_user(
            user_id=context.peer_user_id,
            amount=cost,
            description=f"Smart analysis ({complexity} complexity)",
            metadata={
                "complexity": complexity,
                "data_size": len(data)
            }
        )
        
        if not charge_result.get("success"):
            return {"error": "Payment failed", "required_amount": cost}
        
        # Perform analysis based on complexity
        if complexity == "basic":
            result = self._basic_analysis(data)
        elif complexity == "advanced":
            result = self._advanced_analysis(data)
        else:
            result = self._medium_analysis(data)
        
        return {
            "analysis": result,
            "complexity": complexity,
            "cost": cost,
            "transaction_id": charge_result.get("transaction_id")
        }
```

## Credit Management

### User Credits

```python
class CreditManagerSkill(Skill):
    def __init__(self, config=None):
        super().__init__(config, dependencies=["payment"])
    
    @tool
    async def check_balance(self) -> Dict:
        """Check user's credit balance"""
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        balance = await payment.get_user_balance(context.peer_user_id)
        
        return {
            "credits": balance.get("credits", 0),
            "usd_value": balance.get("usd_value", 0),
            "last_updated": balance.get("last_updated"),
            "pending_charges": balance.get("pending_charges", [])
        }
    
    @tool
    async def purchase_credits(self, amount: float) -> Dict:
        """Purchase credits for user"""
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        purchase_result = await payment.initiate_credit_purchase(
            user_id=context.peer_user_id,
            usd_amount=amount
        )
        
        return {
            "success": purchase_result.get("success"),
            "payment_url": purchase_result.get("payment_url"),
            "expected_credits": purchase_result.get("expected_credits"),
            "transaction_id": purchase_result.get("transaction_id")
        }
    
    @tool
    async def usage_history(self, days: int = 30) -> List[Dict]:
        """Get user's usage history"""
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        history = await payment.get_usage_history(
            user_id=context.peer_user_id,
            days=days
        )
        
        return [
            {
                "date": transaction["date"],
                "service": transaction["description"],
                "amount": transaction["amount"],
                "agent": transaction.get("agent_name"),
                "transaction_id": transaction["transaction_id"]
            }
            for transaction in history
        ]
```

### Credit Monitoring

```python
class CreditMonitoringSkill(Skill):
    """Monitor and alert on credit usage"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["payment"])
        self.low_balance_threshold = config.get("low_balance_threshold", 1.0)  # $1.00
    
    @hook("after_toolcall")
    async def monitor_credit_usage(self, context):
        """Monitor credits after each charged operation"""
        
        # Check if tool had pricing
        tool_name = context["tool_call"]["function"]["name"]
        if hasattr(self, f"_{tool_name}_pricing"):
            payment = self.agent.skills.get("payment")
            user_balance = await payment.get_user_balance(context.peer_user_id)
            
            # Alert if balance is low
            if user_balance.get("usd_value", 0) < self.low_balance_threshold:
                context["low_balance_warning"] = {
                    "current_balance": user_balance.get("usd_value"),
                    "threshold": self.low_balance_threshold,
                    "purchase_url": await payment.get_purchase_url(context.peer_user_id)
                }
        
        return context
    
    @hook("finalize_connection")
    async def send_usage_summary(self, context):
        """Send usage summary at end of session"""
        
        if context.get("session_charges"):
            payment = self.agent.skills.get("payment")
            
            summary = {
                "total_charges": sum(context["session_charges"]),
                "charge_count": len(context["session_charges"]),
                "services_used": context.get("charged_services", [])
            }
            
            await payment.send_usage_summary(
                user_id=context.peer_user_id,
                summary=summary
            )
        
        return context
```

## Revenue Sharing

### Agent Monetization

```python
class MonetizedAgentSkill(Skill):
    """Enable revenue generation for agent owners"""
    
    def __init__(self, config=None):
        super().__init__(config, dependencies=["payment"])
        self.revenue_share = config.get("revenue_share", 0.70)  # 70% to agent owner
    
    @tool
    @pricing(cost=0.10, revenue_share=0.70) 
    async def expert_consultation(self, question: str) -> str:
        """Expert consultation with revenue sharing"""
        
        # Detailed expert analysis
        analysis = await self._expert_analysis(question)
        
        # Revenue automatically split:
        # - 70% to agent owner
        # - 30% to platform
        
        return analysis
    
    @tool
    async def get_revenue_stats(self) -> Dict:
        """Get revenue statistics for agent owner"""
        
        payment = self.agent.skills.get("payment")
        context = self.get_context()
        
        # Only show to agent owner
        if not self._is_agent_owner(context.peer_user_id):
            return {"error": "Access denied - owner only"}
        
        stats = await payment.get_revenue_stats(
            agent_name=context.agent_name,
            period="last_30_days"
        )
        
        return {
            "total_revenue": stats["total_revenue"],
            "transaction_count": stats["transaction_count"],
            "top_services": stats["top_revenue_services"],
            "growth_rate": stats["month_over_month_growth"]
        }
```

### Skill Marketplace

```python
class MarketplaceSkill(Skill):
    """Monetize skills in the marketplace"""
    
    @tool
    @pricing(cost=0.05, category="data_analysis")
    async def premium_data_analysis(self, dataset: str) -> Dict:
        """Premium data analysis available in marketplace"""
        
        # Advanced analysis worth the premium price
        analysis = await self._advanced_analysis(dataset)
        
        return {
            "analysis": analysis,
            "service": "premium_data_analysis",
            "marketplace_listing": True
        }
    
    @tool
    async def publish_to_marketplace(self, skill_config: Dict) -> Dict:
        """Publish skill to Robutler marketplace"""
        
        payment = self.agent.skills.get("payment")
        
        listing = await payment.create_marketplace_listing({
            "skill_name": skill_config["name"],
            "description": skill_config["description"],
            "price_per_use": skill_config["price"],
            "category": skill_config["category"],
            "agent_endpoint": skill_config["endpoint"]
        })
        
        return {
            "listing_id": listing["id"],
            "status": "published",
            "expected_revenue_share": 0.70,
            "marketplace_url": listing["url"]
        }
```

## Payment Webhooks

### Webhook Handling

```python
from flask import Flask, request
import hmac
import hashlib

class PaymentWebhookHandler:
    """Handle payment webhooks from Robutler platform"""
    
    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
        self.app = Flask(__name__)
        self.setup_routes()
    
    def setup_routes(self):
        @self.app.route('/webhooks/payment', methods=['POST'])
        def handle_payment_webhook():
            return self.process_webhook(request)
    
    def process_webhook(self, request):
        # Verify webhook signature
        signature = request.headers.get('X-Robutler-Signature')
        payload = request.get_data()
        
        expected = hmac.new(
            self.webhook_secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected):
            return 'Invalid signature', 401
        
        event = request.json
        
        # Handle different payment events
        if event['type'] == 'payment.completed':
            self.handle_payment_completed(event['data'])
        elif event['type'] == 'payment.failed':
            self.handle_payment_failed(event['data'])
        elif event['type'] == 'credit.purchased':
            self.handle_credit_purchase(event['data'])
        elif event['type'] == 'revenue.payout':
            self.handle_revenue_payout(event['data'])
        
        return 'OK', 200
    
    def handle_payment_completed(self, data):
        """Handle successful payment"""
        user_id = data['user_id']
        amount = data['amount']
        service = data['service']
        
        print(f"Payment completed: {user_id} paid ${amount} for {service}")
        
        # Update user credits, send confirmation, etc.
    
    def handle_payment_failed(self, data):
        """Handle failed payment"""
        user_id = data['user_id']
        amount = data['amount']
        reason = data['failure_reason']
        
        print(f"Payment failed: {user_id} - ${amount} - {reason}")
        
        # Handle payment failure (notify user, retry, etc.)
    
    def handle_credit_purchase(self, data):
        """Handle credit purchase"""
        user_id = data['user_id']
        credits_purchased = data['credits']
        amount_paid = data['amount_usd']
        
        print(f"Credits purchased: {user_id} bought {credits_purchased} credits for ${amount_paid}")
    
    def handle_revenue_payout(self, data):
        """Handle revenue payout to agent owner"""
        owner_id = data['owner_id']
        amount = data['amount']
        period = data['period']
        
        print(f"Revenue payout: ${amount} to {owner_id} for {period}")
```

## Testing Payments

### Mock Payment Integration

```python
class MockPaymentSkill(Skill):
    """Mock payment skill for testing"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.mock_balance = config.get("mock_balance", 10.0)
        self.charges = []
    
    async def charge_user(self, user_id: str, amount: float, **kwargs) -> Dict:
        """Mock charging user"""
        
        if amount > self.mock_balance:
            return {
                "success": False,
                "error": "insufficient_credits",
                "required_amount": amount,
                "available_balance": self.mock_balance
            }
        
        # Simulate successful charge
        self.mock_balance -= amount
        charge_record = {
            "transaction_id": f"mock_txn_{len(self.charges)}",
            "user_id": user_id,
            "amount": amount,
            "timestamp": time.time(),
            **kwargs
        }
        self.charges.append(charge_record)
        
        return {
            "success": True,
            "transaction_id": charge_record["transaction_id"],
            "remaining_balance": self.mock_balance
        }
    
    async def get_user_balance(self, user_id: str) -> Dict:
        """Mock getting user balance"""
        return {
            "credits": self.mock_balance * 100,  # Assuming 1 USD = 100 credits
            "usd_value": self.mock_balance,
            "last_updated": time.time()
        }

# Use in tests
@pytest.fixture
def agent_with_mock_payment():
    return BaseAgent(
        name="test-agent",
        model="openai/gpt-4o",
        skills={
            "payment": MockPaymentSkill({"mock_balance": 5.0})
        }
    )
```

## Configuration

### Payment Settings

```python
# Payment skill configuration
payment_config = {
    "api_key": "your-robutler-key",
    "base_url": "https://api.robutler.ai",
    "default_currency": "USD",
    "auto_charge": True,          # Automatically charge for @pricing decorated tools
    "insufficient_funds_action": "prompt",  # "prompt", "deny", or "defer"
    "revenue_share": 0.70,        # Revenue share for agent owners
    "webhook_secret": "webhook-secret",
    "sandbox_mode": False,        # Use sandbox for testing
    "rate_limits": {
        "charges_per_hour": 100,
        "max_charge_amount": 1.00
    }
}

payment_skill = PaymentSkill(payment_config)
```

### Environment Variables

```bash
# Payment system environment variables
export ROBUTLER_API_KEY="your-api-key"
export ROBUTLER_PAYMENT_WEBHOOK_SECRET="your-webhook-secret"
export ROBUTLER_SANDBOX_MODE="true"  # For testing
export ROBUTLER_DEFAULT_CURRENCY="USD"
export ROBUTLER_REVENUE_SHARE="0.70"
```

The payment system enables seamless monetization of AI agents and skills while providing transparent pricing for users. 