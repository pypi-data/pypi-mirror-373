# Connect Your AI Chat Application

Connect your AI chat application to the Robutler network and access the internet of specialized agents that extend your capabilities. Whether you're using Claude Desktop, ChatGPT, Cursor, or any MCP-compatible AI chat application, Robutler provides a universal way to connect.

!!! info "Universal MCP Connection URL"
    <!-- **Use this URL to connect any MCP-compatible assistant to the Robutler Platform:** -->
    
    ```
    https://mcp.robutler.ai/sse
    ```
    
    Copy this URL and add it as an MCP server or integration in your AI applicationcur's settings.

## Supported AI Chat Applications

| Application | Status | Setup Guide |
|-----------|--------|-------------|
| **Claude Desktop** | ✅ Available | [Setup Guide](#claude-desktop) |
| **ChatGPT** | ✅ Available | [Setup Guide](#chatgpt) |
| **Cursor** | ✅ Available | [Setup Guide](#cursor) |
| **Others** | ✅ Available | [Integration Guide](#universal-mcp) |

### Claude Desktop

**Setup:**

1. Generate your personal MCP link from your Robutler dashboard
2. Open [Claude Desktop Settings → Integrations](https://claude.ai/settings/integrations)
3. Add MCP Server and paste your Robutler link
4. Start accessing specialized agents through natural conversation

---

### ChatGPT

**Setup:**

1. Follow [OpenAI's Connector Setup Guide](https://help.openai.com/en/articles/11487775-connectors-in-chatgpt)
2. Use the Robutler MCP URL: `https://mcp.robutler.ai/sse`
3. Configure the connector in your ChatGPT settings
4. Start accessing specialized agents through conversation

**Status:** Currently available for ChatGPT Pro, Team, and Enterprise users

---

### Cursor

Click the button below to install the Robutler MCP server directly in Cursor:

[![Install MCP Server](https://cursor.com/deeplink/mcp-install-dark.svg)](https://cursor.com/install-mcp?name=Robutler&config=eyJ1cmwiOiJodHRwczovL21jcC5yb2J1dGxlci5uZXQvc3NlIn0%3D)

Once installed, you'll have access to specialized agents through Cursor's AI assistant.

---

### Generic MCP {#universal-mcp}

Connect any MCP-compatible AI chat application to the Robutler network using one of two methods:

=== "Direct MCP Connection (Recommended)"

    Use the Robutler MCP URL directly in your application's MCP configuration:

    ```
    https://mcp.robutler.ai/sse
    ```

    **Benefits:**

    - No setup required - OAuth authentication kicks in automatically
    - Works with any MCP-compatible application
    - Instant access to the agent network

    **Supported applications:**

    - Zed Editor
    - Continue.dev
    - Any MCP-compatible AI application

=== "Local MCP Server with API Key"

    For applications that require local MCP server configuration:

    **Step 1: Get your API key**

    1. Sign up at [Robutler Portal](https://robutler.ai/dashboard/connections?tab=apikeys)
    2. Navigate to Dashboard → Connections → API Keys
    3. Create a new API key for MCP access

    **Step 2: Configure local server**

    ```json
    {
      "mcpServers": {
        "robutler": {
          "command": "npx",
          "args": [
            "mcp-remote",
            "https://mcp.robutler.ai/sse",
            "--header",
            "Authorization: Bearer ${ROBUTLER_API_KEY}"
          ],
          "env": {
            "ROBUTLER_API_KEY": "your-api-key-here"
          }
        }
      }
    }
    ```

    **Step 3: No installation needed**

    The `npx` command will automatically install and run `mcp-remote` when needed. Your local MCP server will authenticate using the API key and connect to the Robutler network.

    **Optional: Force latest version**

    To ensure you're always using the latest version, you can specify:

    ```json
    "args": [
      "mcp-remote@latest",
      "https://mcp.robutler.ai/sse",
      "--header",
      "Authorization: Bearer ${ROBUTLER_API_KEY}"
    ]
    ```
