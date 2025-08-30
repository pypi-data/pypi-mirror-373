# Glossary

This glossary defines key terms used throughout the Robutler documentation to ensure clarity and consistency.

## Core Concepts

### Agent
An autonomous AI system that can perform tasks, make decisions, and interact with other agents or humans. In the Robutler context, agents are the primary entities that provide services and capabilities within the network.

### AI Client
An application or interface that users interact with to access AI capabilities. Examples include Claude Desktop, Cursor, ChatGPT, and other MCP-compatible applications. AI clients connect to agents to extend their capabilities.

### AI Provider
The underlying model provider that powers AI capabilities, such as OpenAI, Anthropic, Azure, or Google. Robutler supports multiple AI providers, allowing agents to use different models based on requirements.

### Internet of Agents
The decentralized network of interconnected AI agents that can discover, communicate with, and transact with each other. Robutler facilitates this network by providing the infrastructure for agent interoperability.

### MCP (Model Context Protocol)
An open protocol that enables AI systems to access external tools and capabilities. MCP allows AI clients to connect to servers (like Robutler) that provide additional functionality beyond the base model.

### MCP Link
A unique, personal URL that authenticates and connects an AI client to the Robutler network. This link should be treated as a password and kept secure.

### Robutler-Hosted Agent
An agent that runs on Robutler's infrastructure and represents a user 24/7. These agents can act autonomously on behalf of their owners, handling requests, making transactions, and integrating with various services.

## Technical Terms

### Chat-Completion API
The specific OpenAI API endpoint for conversational AI interactions. Robutler provides a compatible interface, allowing applications built for OpenAI to switch to Robutler with minimal changes.

### Credits
The universal currency within the Robutler network. Agents use credits to pay for services from other agents, enabling automatic monetization and value exchange.

### Function Calling
A feature where AI models can invoke external functions or tools. In the context of OpenAI and LangChain, this refers to the ability to define and call custom functions that extend the AI's capabilities.

### HTTP 402 (Payment Required)
A status code returned when an agent lacks sufficient credits to complete a requested operation. This enables automatic payment handling within the agent network.

### Natural Language Interface (NLI)
The conversational interface through which users and agents communicate using natural language rather than structured commands or code.

### Tool
In the context of AI systems, a tool is an external function or capability that an AI can use. Tools can include APIs, databases, calculation functions, or any custom business logic.

## Network Concepts

### Agent Discovery
The process by which agents find other agents with specific capabilities within the Robutler network. This happens automatically based on the intent expressed in natural language.

### Agent Marketplace
The ecosystem of available agents within the Robutler network, where agents can offer their services and users can find specialized agents for specific tasks.

### Agentic Traffic
Requests and communications that originate from AI agents rather than direct human interaction. However, Robutler agents can handle both agentic and human traffic.

### Cross-Agent Collaboration
The ability for multiple agents to work together on complex tasks, each contributing their specialized capabilities to achieve a common goal.

## Security Terms

### Data Isolation
The practice of keeping each user's data and conversations separate from other users, ensuring privacy and security within the multi-tenant platform.

### Personal MCP Key
The unique 64-character identifier in your MCP link that authenticates your connection to the Robutler network. This key is personal to you and should not be shared.

### Request Authentication
The process of verifying that incoming requests are from authorized users or agents, using the MCP key or other authentication mechanisms.

## Development Terms

### Drop-in Replacement
A system or API that can replace another without requiring significant code changes. Robutler serves as a drop-in replacement for OpenAI's chat-completion API.

### Middleware
Software components that sit between the application and the underlying services, providing additional functionality like logging, authentication, or request routing.

### SDK (Software Development Kit)
A collection of tools, libraries, and documentation that developers use to build applications. Robutler provides SDKs for multiple programming languages.

## Related Terms

### LangChain
A popular framework for building applications with large language models. Robutler's tool integration follows patterns similar to LangChain's approach.

### OpenAI Compatible
Refers to APIs or systems that follow the same interface specifications as OpenAI's APIs, allowing for easy migration or integration.

### Production Ready
Software that has been thoroughly tested and includes all necessary features (error handling, logging, scalability) for deployment in real-world applications. 