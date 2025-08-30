"""
Robutler API Client - Robutler V2.0

HTTP client for integrating with Robutler Platform services.
Provides authentication, user management, payment, and other platform APIs.
"""

import os
import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from decimal import Decimal

from .types import (
    User, ApiKey, Integration, CreditTransaction,
    AuthResponse, ApiResponse,
    UserRole, SubscriptionStatus, TransactionType
)


class RobutlerAPIError(Exception):
    """Raised when Robutler API returns an error"""
    def __init__(self, message: str, status_code: int = 400, response_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class Agent:
    """Agent model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        # Handle nested agent data structure: {'agent': {...}} or flat {...}
        if 'agent' in data:
            agent_data = data['agent']
            self._raw_data = data  # Keep full response structure
        else:
            agent_data = data
            self._raw_data = data
        
        # Extract all agent properties from the agent_data
        self.id: str = agent_data.get("id", "") or agent_data.get("agentId", "")
        self.name: str = agent_data.get("name", "")
        self.instructions: str = agent_data.get("instructions", "")
        self.model: str = agent_data.get("model", "gpt-4o-mini")
        self.intents: List[str] = agent_data.get("intents", [])
        self.can_use_other_agents: bool = agent_data.get("canTalkToOtherAgents", False)
        self.other_agents_can_talk: bool = agent_data.get("otherAgentsCanTalk", False)
        self.credits_per_token: Optional[float] = self._parse_float(agent_data.get("creditsPerToken"))
        self.minimum_balance: Optional[float] = self._parse_float(agent_data.get("minimumBalance"))
        self.agent_pricing_percent: Optional[float] = self._parse_float(agent_data.get("agentPricingPercent"))
        self.is_public: bool = agent_data.get("isPublic", False)
        self.description: str = agent_data.get("description", "")
        self.avatar_url: Optional[str] = agent_data.get("avatarUrl")
        self.greeting_message: Optional[str] = agent_data.get("greetingMessage")
        self.suggested_actions: List[str] = agent_data.get("suggestedActions", [])
        self.greeting_image_mobile: Optional[str] = agent_data.get("greetingImageMobile")
        self.greeting_image_desktop: Optional[str] = agent_data.get("greetingImageDesktop")
        self.skills: Optional[Dict[str, Any]] = agent_data.get("skills")
        self.api_key_encrypted: Optional[str] = agent_data.get("apiKey")  # This is encrypted
    
    def _parse_float(self, value) -> Optional[float]:
        """Parse float value from string or number"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format - returns the agent data only"""
        if 'agent' in self._raw_data:
            return self._raw_data['agent']
        return self._raw_data
    
    def get_full_data(self) -> Dict[str, Any]:
        """Get the full raw data structure"""
        return self._raw_data
    
    def __repr__(self) -> str:
        return f"Agent(id='{self.id}', name='{self.name}', model='{self.model}')"


class ContentFile:
    """Content file model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("originalFileName", "")
        self.size: int = data.get("size", 0)
        self.url: str = data.get("url", "")
        self.visibility: str = data.get("visibility", "private")
        self._raw_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format"""
        return self._raw_data
    
    @property
    def size_formatted(self) -> str:
        """Get formatted file size"""
        if self.size > 1024 * 1024:  # MB
            return f"{self.size / (1024 * 1024):.1f}MB"
        elif self.size > 1024:  # KB
            return f"{self.size // 1024}KB"
        else:  # Bytes
            return f"{self.size}B"
    
    def __repr__(self) -> str:
        return f"ContentFile(name='{self.name}', size='{self.size_formatted}')"


class UserProfile:
    """User profile model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.email: str = data.get("email", "")
        self.role: str = data.get("role", "user")
        self.plan_name: str = data.get("planName", "")
        self.total_credits: Decimal = Decimal(str(data.get("totalCredits", "0")))
        self.used_credits: Decimal = Decimal(str(data.get("usedCredits", "0")))
        self.available_credits: Decimal = self.total_credits - self.used_credits
        self.referral_code: str = data.get("referralCode", "")
        self._raw_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format"""
        return self._raw_data
    
    def __repr__(self) -> str:
        return f"UserProfile(name='{self.name}', email='{self.email}', plan='{self.plan_name}')"


class ApiKeyInfo:
    """API Key info model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.name: str = data.get("name", "")
        self.key: str = data.get("key", "")
        self.created_at: str = data.get("createdAt", "")
        self.last_used: Optional[str] = data.get("lastUsed")
        self.permissions: Dict[str, Any] = data.get("permissions", {})
        self._raw_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format"""
        return self._raw_data
    
    def __repr__(self) -> str:
        return f"ApiKeyInfo(name='{self.name}', id='{self.id}')"


class TransactionInfo:
    """Transaction info model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.type: str = data.get("type", "")
        self.amount: Decimal = Decimal(str(data.get("amount", "0")))
        self.description: str = data.get("description", "")
        self.created_at: str = data.get("createdAt", "")
        self.status: str = data.get("status", "")
        self._raw_data = data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format"""
        return self._raw_data
    
    def __repr__(self) -> str:
        return f"TransactionInfo(type='{self.type}', amount={self.amount}, status='{self.status}')"


class ChatCompletionResult:
    """Chat completion result model with attributes for clean access"""
    
    def __init__(self, data: Dict[str, Any]):
        self.id: str = data.get("id", "")
        self.choices: List[Dict[str, Any]] = data.get("choices", [])
        self.usage: Dict[str, Any] = data.get("usage", {})
        self.model: str = data.get("model", "")
        self._raw_data = data
    
    @property
    def content(self) -> str:
        """Get the main response content"""
        if self.choices:
            return self.choices[0].get("message", {}).get("content", "")
        return ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert back to dictionary format"""
        return self._raw_data
    
    def __repr__(self) -> str:
        return f"ChatCompletionResult(model='{self.model}', choices={len(self.choices)})"


class AgentsResource:
    """Agents resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def list(self) -> List[Agent]:
        """List user's agents - returns list of Agent objects"""
        response = await self._client._make_request('GET', '/agents')
        if not response.success:
            raise RobutlerAPIError(f"Failed to list agents: {response.status_code}", response.status_code, response.data)
        
        agents_data = response.data.get("agents", [])
        return [Agent(agent_data) for agent_data in agents_data]
    
    async def get_by_name(self, name: str) -> Agent:
        """Get agent by name - returns Agent object"""
        response = await self._client._make_request('GET', f'/agents/by-name/{name}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get agent by name '{name}': {response.status_code}", response.status_code, response.data)
        return Agent(response.data)
    
    async def get_by_id(self, agent_id: str) -> Agent:
        """Get agent by ID - returns Agent object"""
        response = await self._client._make_request('GET', f'/agents/{agent_id}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get agent by ID '{agent_id}': {response.status_code}", response.status_code, response.data)
        return Agent(response.data)
    
    async def get(self, agent_id: str) -> 'AgentResource':
        """Get agent resource by ID"""
        return AgentResource(self._client, agent_id)
    
    async def create(self, agent_data: Dict[str, Any]) -> Agent:
        """Create a new agent - returns created Agent object"""
        response = await self._client._make_request('POST', '/agents', data=agent_data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to create agent: {response.status_code}", response.status_code, response.data)
        return Agent(response.data)
    
    async def update(self, agent_id: str, agent_data: Dict[str, Any]) -> Agent:
        """Update an existing agent - returns updated Agent object"""
        response = await self._client._make_request('PUT', f'/agents/{agent_id}', data=agent_data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to update agent {agent_id}: {response.status_code}", response.status_code, response.data)
        return Agent(response.data)
    
    async def delete(self, agent_id: str) -> bool:
        """Delete an agent - returns True if successful"""
        response = await self._client._make_request('DELETE', f'/agents/{agent_id}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to delete agent {agent_id}: {response.status_code}", response.status_code, response.data)
        return True
    
    async def search(self, query: str, max_results: int = 10, mode: str = 'semantic', min_similarity: float = 0.7) -> List[Dict[str, Any]]:
        """Search for agents - returns list of agent results"""
        search_data = {
            'query': query,
            'fields': ['name', 'description', 'intents']
        }
        
        response = await self._client._make_request('POST', '/agents/search', data=search_data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to search agents: {response.message}", response.status_code, response.data)
        
        return response.data.get('agents', [])
    
    async def discover(self, capabilities: List[str], max_results: int = 10) -> List[Dict[str, Any]]:
        """Discover agents by capabilities - returns list of agent results"""
        discovery_params = {
            'capabilities': capabilities,
            'limit': max_results
        }
        
        response = await self._client._make_request('GET', '/agents/discover', params=discovery_params)
        if not response.success:
            raise RobutlerAPIError(f"Failed to discover agents: {response.message}", response.status_code, response.data)
        
        return response.data.get('agents', [])
    
    async def find_similar(self, agent_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Find similar agents - returns list of agent results"""
        response = await self._client._make_request('GET', f'/agents/{agent_id}/similar', params={'limit': max_results})
        if not response.success:
            raise RobutlerAPIError(f"Failed to find similar agents: {response.message}", response.status_code, response.data)
        
        return response.data.get('agents', [])


class AgentResource:
    """Individual agent resource"""
    
    def __init__(self, client, agent_id: str):
        self._client = client
        self.agent_id = agent_id
    
    async def get(self) -> Agent:
        """Get agent details - returns Agent object"""
        response = await self._client._make_request('GET', f'/agents/{self.agent_id}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get agent {self.agent_id}: {response.status_code}", response.status_code, response.data)
        return Agent(response.data)
    
    async def api_key(self) -> str:
        """Get API key for this agent - returns the API key string"""
        response = await self._client._make_request('GET', f'/agents/{self.agent_id}/api-key')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get API key for agent {self.agent_id}: {response.status_code}", response.status_code, response.data)
        
        api_key = response.data.get("apiKey")
        if not api_key:
            raise RobutlerAPIError(f"No API key found for agent {self.agent_id}")
        return api_key
    
    async def chat_completion(self, data: Dict[str, Any]) -> ChatCompletionResult:
        """Send chat completion request to this agent - returns ChatCompletionResult"""
        response = await self._client._make_request('POST', f'/agents/{self.agent_id}/chat/completions', data=data)
        if not response.success:
            raise RobutlerAPIError(f"Chat completion failed for agent {self.agent_id}: {response.status_code}", response.status_code, response.data)
        return ChatCompletionResult(response.data)
    
    async def get_intents(self) -> List[Dict[str, Any]]:
        """Get published intents for this agent - returns list of intent objects"""
        response = await self._client._make_request('GET', f'/agents/{self.agent_id}/intents')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get intents for agent {self.agent_id}: {response.message}", response.status_code, response.data)
        
        return response.data.get('intents', [])


class IntentsResource:
    """Intents resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def publish(self, intents_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Publish intents - returns list of publish results"""
        data = {'intents': intents_data}
        response = await self._client._make_request('POST', '/intents/publish', data=data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to publish intents: {response.message}", response.status_code, response.data)
        
        return response.data.get('results', [])


class ContentResource:
    """Content resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def agent_access(self, visibility: str = 'public') -> List[ContentFile]:
        """Get agent-accessible content - returns list of ContentFile objects
        
        Agent ID is automatically inferred from the API key used for authentication.
        """
        params = {'visibility': visibility}
        
        # Debug logging
        api_key_prefix = self._client.api_key[:20] + "..." if self._client.api_key and len(self._client.api_key) > 20 else self._client.api_key
        print(f"🌐 API Request: GET /content/agent-access?visibility={visibility}")
        print(f"🔑 Using API key: {api_key_prefix}")
        print(f"🏢 Base URL: {self._client.base_url}")
        
        response = await self._client._make_request('GET', '/content/agent-access', params=params)
        
        print(f"📡 Response: status={response.status_code}, success={response.success}")
        if response.data:
            files_count = len(response.data.get('files', []))
            print(f"📁 Files in response: {files_count}")
            
            # Debug: show first few files if any
            files_data = response.data.get('files', [])
            for i, file_data in enumerate(files_data[:3]):  # Show first 3 files
                print(f"  File {i+1}: {file_data.get('originalFileName', 'unknown')} - tags: {file_data.get('tags', [])}")
        else:
            print(f"📁 No data in response")
        
        if not response.success:
            print(f"❌ Error: {response.message}")
            raise RobutlerAPIError(f"Failed to get agent content: {response.status_code}", response.status_code, response.data)
        
        files_data = response.data.get('files', [])
        # Rewrite URLs for public serving via chat
        for file_data in files_data:
            if isinstance(file_data, dict) and 'url' in file_data:
                file_data['url'] = self._client._rewrite_public_url(file_data.get('url'))
        return [ContentFile(file_data) for file_data in files_data]
    
    async def list(self, 
                  visibility: Optional[str] = None,
                  tags: Optional[str] = None,
                  limit: Optional[int] = None,
                  offset: Optional[int] = None) -> List[ContentFile]:
        """List user's content files - returns list of ContentFile objects"""
        params = {}
        if visibility:
            params['visibility'] = visibility
        if tags:
            params['tags'] = tags
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        
        response = await self._client._make_request('GET', '/content', params=params)
        if not response.success:
            raise RobutlerAPIError(f"Failed to list content: {response.status_code}", response.status_code, response.data)
        
        files_data = response.data.get('files', [])
        for file_data in files_data:
            if isinstance(file_data, dict) and 'url' in file_data:
                file_data['url'] = self._client._rewrite_public_url(file_data.get('url'))
        return [ContentFile(file_data) for file_data in files_data]
    
    async def upload(self, file_data: bytes, filename: str, visibility: str = 'private') -> ContentFile:
        """Upload content file - returns ContentFile object"""
        data = {
            'file': file_data,
            'filename': filename,
            'visibility': visibility
        }
        response = await self._client._make_request('POST', '/content', data=data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to upload file: {response.status_code}", response.status_code, response.data)
        return ContentFile(response.data)
    
    async def delete(self, file_id: str) -> bool:
        """Delete content file - returns True if successful"""
        response = await self._client._make_request('DELETE', f'/content/{file_id}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to delete file {file_id}: {response.status_code}", response.status_code, response.data)
        return True


class UserResource:
    """User resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def get(self) -> UserProfile:
        """Get current user profile - returns UserProfile object"""
        response = await self._client._make_request('GET', '/user')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get user: {response.status_code}", response.status_code, response.data)
        # API returns shape { user: { ... } }
        user_data = response.data.get('user', response.data or {})
        return UserProfile(user_data)
    
    async def credits(self) -> Decimal:
        """Get user's available credits - returns Decimal"""
        response = await self._client._make_request('GET', '/user/credits')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get credits: {response.status_code}", response.status_code, response.data)
        
        # Prefer server-computed availableCredits (includes plan_credits if server supports it)
        if isinstance(response.data, dict) and 'availableCredits' in response.data:
            try:
                return Decimal(str(response.data.get('availableCredits', '0')))
            except Exception:
                pass
        
        # Fallback to local calculation if server didn't provide it
        total_credits = Decimal(str(response.data.get('totalCredits', '0'))) if isinstance(response.data, dict) else Decimal('0')
        used_credits = Decimal(str(response.data.get('usedCredits', '0'))) if isinstance(response.data, dict) else Decimal('0')
        return total_credits - used_credits
    
    async def transactions(self, limit: int = 50) -> List[TransactionInfo]:
        """Get user's transaction history - returns list of TransactionInfo objects"""
        response = await self._client._make_request('GET', f'/user/transactions?limit={limit}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to get transactions: {response.status_code}", response.status_code, response.data)
        
        transactions_data = response.data.get('transactions', [])
        return [TransactionInfo(transaction_data) for transaction_data in transactions_data]


class ApiKeysResource:
    """API Keys resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def list(self) -> List[ApiKeyInfo]:
        """List user's API keys - returns list of ApiKeyInfo objects"""
        response = await self._client._make_request('GET', '/api-keys')
        if not response.success:
            raise RobutlerAPIError(f"Failed to list API keys: {response.status_code}", response.status_code, response.data)
        
        keys_data = response.data.get('keys', [])
        return [ApiKeyInfo(key_data) for key_data in keys_data]
    
    async def create(self, name: str, permissions: Optional[Dict[str, Any]] = None) -> ApiKeyInfo:
        """Create new API key - returns ApiKeyInfo object"""
        data = {'name': name}
        if permissions:
            data['permissions'] = permissions
        
        response = await self._client._make_request('POST', '/api-keys', data=data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to create API key: {response.status_code}", response.status_code, response.data)
        return ApiKeyInfo(response.data)
    
    async def delete(self, key_id: str) -> bool:
        """Delete API key - returns True if successful"""
        response = await self._client._make_request('DELETE', f'/api-keys/{key_id}')
        if not response.success:
            raise RobutlerAPIError(f"Failed to delete API key {key_id}: {response.status_code}", response.status_code, response.data)
        return True


class TokensResource:
    """Payment tokens resource for hierarchical API access"""
    
    def __init__(self, client):
        self._client = client
    
    async def validate(self, token: str) -> bool:
        """Validate payment token - returns True if valid"""
        response = await self._client._make_request('GET', '/tokens/validate', params={'token': token})
        if not response.success:
            return False
        return response.data.get('valid', False)
    
    async def get_balance(self, token: str) -> float:
        """Get payment token balance - returns balance as float"""
        # Use validate endpoint; it returns availableAmount
        response = await self._client._make_request('GET', '/tokens/validate', params={'token': token})
        if not response.success:
            raise RobutlerAPIError(
                f"Failed to get token balance: {response.message}",
                response.status_code,
                response.data,
            )
        amount_value = response.data.get('availableAmount', response.data.get('balance', 0.0))
        try:
            return float(amount_value)
        except (TypeError, ValueError):
            return 0.0
    
    async def validate_with_balance(self, token: str) -> Dict[str, Any]:
        """Validate token and get balance - returns dict with valid and balance"""
        response = await self._client._make_request('GET', '/tokens/validate', params={'token': token})
        if not response.success:
            error_msg = response.message or 'Validation failed'
            return {'valid': False, 'error': error_msg, 'balance': 0.0}
        valid = response.data.get('valid', False)
        amount_value = response.data.get('availableAmount', response.data.get('balance', 0.0))
        try:
            balance = float(amount_value)
        except (TypeError, ValueError):
            balance = 0.0
        return {'valid': valid, 'balance': balance}
    
    async def redeem(self, token: str, amount: Union[str, float], api_key_id: Optional[str] = None) -> bool:
        """Redeem/charge payment token - returns True if successful"""
        data = {
            'token': token,
            'amount': str(amount)
        }
        if api_key_id:
            data['apiKeyId'] = api_key_id
        response = await self._client._make_request('PUT', '/tokens/redeem', data=data)
        if not response.success:
            raise RobutlerAPIError(f"Failed to redeem token: {response.message}", response.status_code, response.data)
        return response.success


class RobutlerClient:
    """
    Robutler Platform API Client
    
    Provides hierarchical access to:
    - client.agents.list() - Agent management
    - client.content.agent_access() - Content access
    - client.user.get() - User management
    - client.api_keys.list() - API key management
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        """
        Initialize Robutler API client
        
        Args:
            api_key: Robutler API key (or set ROBUTLER_API_KEY env var)
            base_url: Base URL for Robutler API (or set ROBUTLER_API_URL env var)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.api_key = api_key or os.getenv('ROBUTLER_API_KEY')
        # Prefer internal cluster URL in production, then public URL, then hosted default, then localhost
        resolved_base = (
            base_url
            or os.getenv('ROBUTLER_INTERNAL_API_URL')
            or os.getenv('ROBUTLER_API_URL')
            or 'https://robutler.ai'
            or 'http://localhost:3000'
        )
        self.base_url = resolved_base.rstrip('/')
        # Public content base URL used by chat frontend (e.g., http://localhost:3001)
        self.public_base_url = (os.getenv('ROBUTLER_CHAT_URL') or 'http://localhost:3001').rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError("Robutler API key is required. Set ROBUTLER_API_KEY environment variable or provide api_key parameter.")
        
        # Session for connection pooling
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Initialize hierarchical resources
        self.agents = AgentsResource(self)
        self.content = ContentResource(self)
        self.user = UserResource(self)
        self.api_keys = ApiKeysResource(self)
        self.tokens = TokensResource(self)
        self.intents = IntentsResource(self)

    def _rewrite_public_url(self, url: Optional[str]) -> Optional[str]:
        """Rewrite portal public content URLs to the chat public base URL.
        - http(s)://<portal>/api/content/public/... -> http(s)://<chat>/api/content/public/...
        - /api/content/public/... -> <chat>/api/content/public/...
        """
        if not url:
            return url
        try:
            if url.startswith('/api/content/public'):
                return f"{self.public_base_url}{url}"
            portal_prefix = f"{self.base_url}/api/content/public"
            if url.startswith(portal_prefix):
                return url.replace(self.base_url, self.public_base_url, 1)
        except Exception:
            return url
        return url

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session
    
    async def close(self):
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    def _get_headers(self, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Get request headers with authentication"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Key': self.api_key,
            'User-Agent': 'Robutler-V2-Client/1.0'
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def _make_request(self, 
                           method: str, 
                           endpoint: str, 
                           data: Optional[Dict[str, Any]] = None,
                           params: Optional[Dict[str, Any]] = None,
                           headers: Optional[Dict[str, str]] = None) -> ApiResponse:
        """
        Make HTTP request to Robutler API with retries and error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            headers: Additional headers
            
        Returns:
            ApiResponse with success/error information
        """
        url = f"{self.base_url}/api{endpoint}"
        request_headers = self._get_headers(headers)

        session = await self._get_session()
        
        for attempt in range(self.max_retries + 1):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    json=data if data else None,
                    params=params,
                    headers=request_headers
                ) as response:
                    
                    # Get response text
                    response_text = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        response_data = json.loads(response_text) if response_text else {}
                    except json.JSONDecodeError:
                        response_data = {'message': response_text}
                    
                    # Handle different status codes
                    if response.status == 200:
                        return ApiResponse(
                            success=True,
                            data=response_data,
                            status_code=response.status
                        )
                    elif response.status == 401:
                        return ApiResponse(
                            success=False,
                            error='Authentication failed',
                            message=response_data.get('message', 'Invalid API key or token'),
                            status_code=response.status
                        )
                    elif response.status == 403:
                        return ApiResponse(
                            success=False,
                            error='Authorization failed',
                            message=response_data.get('message', 'Insufficient permissions'),
                            status_code=response.status
                        )
                    elif response.status == 404:
                        return ApiResponse(
                            success=False,
                            error='Not found',
                            message=response_data.get('message', 'Resource not found'),
                            status_code=response.status
                        )
                    elif response.status >= 500:
                        # Server error - retry
                        if attempt < self.max_retries:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        
                        return ApiResponse(
                            success=False,
                            error='Server error',
                            message=response_data.get('message', 'Internal server error'),
                            status_code=response.status
                        )
                    else:
                        return ApiResponse(
                            success=False,
                            error='Request failed',
                            message=response_data.get('message', f'HTTP {response.status}'),
                            status_code=response.status
                        )
                        
            except aiohttp.ClientError as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(2 ** attempt)
                    continue
                
                return ApiResponse(
                    success=False,
                    error='Network error',
                    message=str(e),
                    status_code=0
                )
            except Exception as e:
                return ApiResponse(
                    success=False,
                    error='Unexpected error',
                    message=str(e),
                    status_code=0
                )
        
        return ApiResponse(
            success=False,
            error='Max retries exceeded',
            message=f'Failed after {self.max_retries + 1} attempts',
            status_code=0
        )
    
    # ===== USER MANAGEMENT METHODS =====
    
    async def get_user(self) -> AuthResponse:
        """Get current user information"""
        try:
            response = await self._make_request('GET', '/user')
            
            if not response.success:
                return AuthResponse(
                    success=False,
                    error=response.error,
                    message=response.message
                )
            
            user_data = response.data.get('user', {}) if response.data else {}
            
            # Convert to User object
            user = User(
                id=user_data.get('id', ''),
                name=user_data.get('name'),
                email=user_data.get('email', ''),
                role=UserRole(user_data.get('role', 'user')),
                google_id=user_data.get('googleId'),
                avatar_url=user_data.get('avatarUrl'),
                stripe_customer_id=user_data.get('stripeCustomerId'),
                stripe_subscription_id=user_data.get('stripeSubscriptionId'),
                plan_name=user_data.get('planName'),
                total_credits=Decimal(user_data.get('totalCredits', '0')),
                used_credits=Decimal(user_data.get('usedCredits', '0')),
                referral_code=user_data.get('referralCode'),
                referred_by=user_data.get('referredBy'),
                referral_count=user_data.get('referralCount', 0)
            )
            
            return AuthResponse(success=True, user=user)
            
        except Exception as e:
            return AuthResponse(
                success=False,
                error='Failed to get user',
                message=str(e)
            )
    
    async def validate_api_key(self, api_key: str) -> AuthResponse:
        """Validate API key and get associated user"""
        try:
            # Create temporary client with the API key to test
            temp_headers = {
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key
            }
            
            response = await self._make_request('GET', '/user', headers=temp_headers)
            
            if not response.success:
                return AuthResponse(
                    success=False,
                    error='Invalid API key',
                    message=response.message
                )
            
            user_data = response.data.get('user', {}) if response.data else {}
            
            # Convert to User object  
            user = User(
                id=user_data.get('id', ''),
                name=user_data.get('name'),
                email=user_data.get('email', ''),
                role=UserRole(user_data.get('role', 'user'))
            )
            
            return AuthResponse(success=True, user=user)
            
        except Exception as e:
            return AuthResponse(
                success=False,
                error='API key validation failed',
                message=str(e)
            )
    
    async def get_user_credits(self) -> ApiResponse:
        """Get user credit information"""
        return await self._make_request('GET', '/user/credits')
    
    async def get_user_transactions(self, limit: int = 50, offset: int = 0) -> ApiResponse:
        """Get user transaction history"""
        params = {'limit': limit, 'offset': offset}
        return await self._make_request('GET', '/user/transactions', params=params)
    
    # ===== API KEY MANAGEMENT METHODS =====
    
    async def list_api_keys(self) -> ApiResponse:
        """List user's API keys"""
        return await self._make_request('GET', '/api-keys')
    
    async def create_api_key(self, name: str, permissions: Optional[Dict[str, Any]] = None) -> ApiResponse:
        """Create a new API key"""
        data = {
            'name': name,
            'permissions': permissions or {}
        }
        return await self._make_request('POST', '/api-keys', data=data)
    
    async def delete_api_key(self, api_key_id: str) -> ApiResponse:
        """Delete an API key"""
        return await self._make_request('DELETE', f'/api-keys/{api_key_id}')
    
    # ===== INTEGRATION METHODS =====
    
    async def list_integrations(self) -> ApiResponse:
        """List user's integrations"""
        return await self._make_request('GET', '/user/integrations')
    
    async def create_integration(self, 
                               name: str, 
                               integration_type: str = "api",
                               protocol: str = "http") -> ApiResponse:
        """Create a new integration"""
        data = {
            'name': name,
            'type': integration_type,
            'protocol': protocol
        }
        return await self._make_request('POST', '/user/integrations', data=data)
    
    # ===== CREDIT/PAYMENT METHODS =====
    
    async def track_usage(self, 
                         amount: Union[str, Decimal, float],
                         description: str = "API usage",
                         source: str = "api_usage",
                         integration_id: Optional[str] = None) -> ApiResponse:
        """Track credit usage"""
        data = {
            'amount': str(amount),
            'type': 'usage',
            'description': description,
            'source': source
        }
        if integration_id:
            data['integration_id'] = integration_id
            
        return await self._make_request('POST', '/user/transactions', data=data)
    
    # ===== HEALTH/STATUS METHODS =====
    
    async def health_check(self) -> ApiResponse:
        """Check API health status"""
        return await self._make_request('GET', '/health')
    
    async def get_config(self) -> ApiResponse:
        """Get API configuration"""
        return await self._make_request('GET', '/config')
    
    # ===== UTILITY METHODS =====
    
    def _parse_user_data(self, user_data: Dict[str, Any]) -> User:
        """Parse user data from API response into User object"""
        return User(
            id=user_data.get('id', ''),
            name=user_data.get('name'),
            email=user_data.get('email', ''),
            role=UserRole(user_data.get('role', 'user')),
            google_id=user_data.get('googleId'),
            avatar_url=user_data.get('avatarUrl'),
            created_at=self._parse_datetime(user_data.get('createdAt')),
            updated_at=self._parse_datetime(user_data.get('updatedAt')),
            stripe_customer_id=user_data.get('stripeCustomerId'),
            stripe_subscription_id=user_data.get('stripeSubscriptionId'),
            stripe_product_id=user_data.get('stripeProductId'),
            plan_name=user_data.get('planName'),
            total_credits=Decimal(user_data.get('totalCredits', '0')),
            used_credits=Decimal(user_data.get('usedCredits', '0')),
            referral_code=user_data.get('referralCode'),
            referred_by=user_data.get('referredBy'),
            referral_count=user_data.get('referralCount', 0)
        )
    
    def _parse_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string from API response"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except ValueError:
            return None
    
    # ===== AGENT MANAGEMENT METHODS =====
    
    # Legacy methods for backward compatibility - these wrap the new hierarchical methods
    async def list_agents(self) -> List[Agent]:
        """List user's agents (legacy - use client.agents.list())"""
        return await self.agents.list()
    
    async def get_agent_api_key(self, agent_id: str) -> str:
        """Get API key for an agent (legacy - use client.agents.get(id).api_key())"""
        agent_resource = await self.agents.get(agent_id)
        return await agent_resource.api_key()
    
    async def get_agent_content(self, visibility: str = 'public') -> List[ContentFile]:
        """Get agent-accessible content (legacy - use client.content.agent_access())"""
        return await self.content.agent_access(visibility)

    # ===== CONTENT STORAGE METHODS =====
    
    async def list_content(self, 
                          visibility: Optional[str] = None,
                          tags: Optional[str] = None,
                          limit: Optional[int] = None,
                          offset: Optional[int] = None) -> ApiResponse:
        """List user's content files"""
        params = {}
        if visibility:
            params['visibility'] = visibility
        if tags:
            params['tags'] = tags
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
            
        response = await self._make_request('GET', '/content', params=params)
        if not response.success:
            raise RobutlerAPIError(f"Failed to list content: {response.status_code}", response.status_code, response.data)
        
        files_data = response.data.get('files', [])
        for file_data in files_data:
            if isinstance(file_data, dict) and 'url' in file_data:
                file_data['url'] = self._rewrite_public_url(file_data.get('url'))
        return [ContentFile(file_data) for file_data in files_data]
    
    async def upload_content(self,
                           filename: str,
                           content_data: bytes,
                           content_type: str = 'application/json',
                           visibility: str = 'private',
                           description: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> ApiResponse:
        """Upload content to user's storage area"""
        session = await self._get_session()
        url = f"{self.base_url}/api/content"
        
        # Prepare form data
        form_data = aiohttp.FormData()
        form_data.add_field('file', content_data, filename=filename, content_type=content_type)
        form_data.add_field('visibility', visibility)
        
        if description:
            form_data.add_field('description', description)
        if tags:
            form_data.add_field('tags', json.dumps(tags))
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'X-API-Key': self.api_key,
            'User-Agent': 'Robutler-V2-Client/1.0'
        }
        
        try:
            async with session.post(url, data=form_data, headers=headers) as response:
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    response_data = {'message': response_text}
                
                if response.status == 200:
                    # Rewrite returned URL if present
                    if isinstance(response_data, dict) and 'url' in response_data:
                        response_data['url'] = self._rewrite_public_url(response_data.get('url'))
                    return ApiResponse(
                        success=True,
                        data=response_data,
                        status_code=response.status
                    )
                else:
                    return ApiResponse(
                        success=False,
                        error='Upload failed',
                        message=response_data.get('error', f'HTTP {response.status}'),
                        status_code=response.status
                    )
                    
        except Exception as e:
            return ApiResponse(
                success=False,
                error='Upload error',
                message=str(e),
                status_code=0
            )
    
    async def get_content(self, filename: str) -> ApiResponse:
        """Get content file by filename"""
        # First list content to find the file
        list_response = await self.list_content(visibility='private')
        if not list_response.success:
            return list_response
        
        files = list_response.data.get('files', []) if list_response.data else []
        target_file = None
        
        for file_info in files:
            if file_info.get('fileName') == filename or file_info.get('originalFileName') == filename:
                target_file = file_info
                break
        
        if not target_file:
            return ApiResponse(
                success=False,
                error='File not found',
                message=f"File '{filename}' not found",
                status_code=404
            )
        
        # Get the file content from the URL
        file_url = target_file.get('url')
        if not file_url:
            return ApiResponse(
                success=False,
                error='File URL not available',
                message=f"No URL available for file '{filename}'",
                status_code=404
            )
        
        session = await self._get_session()
        headers = self._get_headers()
        
        try:
            async with session.get(file_url, headers=headers) as response:
                if response.status == 200:
                    content_text = await response.text()
                    
                    # Try to parse as JSON
                    try:
                        content_data = json.loads(content_text)
                    except json.JSONDecodeError:
                        content_data = content_text
                    
                    return ApiResponse(
                        success=True,
                        data={
                            'filename': target_file.get('fileName'),
                            'content': content_data,
                            'metadata': {
                                'size': target_file.get('size'),
                                'uploadedAt': target_file.get('uploadedAt'),
                                'description': target_file.get('description'),
                                'tags': target_file.get('tags', [])
                            }
                        },
                        status_code=response.status
                    )
                else:
                    return ApiResponse(
                        success=False,
                        error='Failed to retrieve content',
                        message=f'HTTP {response.status}',
                        status_code=response.status
                    )
                    
        except Exception as e:
            return ApiResponse(
                success=False,
                error='Content retrieval error',
                message=str(e),
                status_code=0
            )
    
    async def delete_content(self, filename: str) -> ApiResponse:
        """Delete content file by filename"""
        params = {'fileName': filename}
        return await self._make_request('DELETE', '/content', params=params)
    
    async def update_content(self,
                           filename: str,
                           content_data: bytes,
                           content_type: str = 'application/json',
                           description: Optional[str] = None,
                           tags: Optional[List[str]] = None) -> ApiResponse:
        """Update existing content file"""
        # Delete old version first
        delete_result = await self.delete_content(filename)
        # Continue even if delete fails (file might not exist)
        
        # Upload new version
        return await self.upload_content(
            filename=filename,
            content_data=content_data,
            content_type=content_type,
            visibility='private',
            description=description,
            tags=tags
        )
    
    def __repr__(self) -> str:
        """String representation of the client"""
        return f"RobutlerClient(base_url='{self.base_url}', api_key='***{self.api_key[-4:] if self.api_key else None}')"


# ===== CONVENIENCE FUNCTIONS =====

async def create_client(api_key: Optional[str] = None, base_url: Optional[str] = None) -> RobutlerClient:
    """Create and return a Robutler API client"""
    return RobutlerClient(api_key=api_key, base_url=base_url)


async def validate_api_key(api_key: str, base_url: Optional[str] = None) -> AuthResponse:
    """Validate API key using a temporary client"""
    async with RobutlerClient(api_key=api_key, base_url=base_url) as client:
        return await client.get_user() 