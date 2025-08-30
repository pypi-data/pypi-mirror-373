## Google Calendar Skill (r-google-calendar)

This document explains how to set up and test the Google Calendar skill for the dedicated agent `r-google-calendar`.

### What it does
- Provides tools to authorize access to a user’s Google Calendar and read upcoming events.
- Uses a lightweight per-agent key-value store to persist OAuth tokens under a dedicated namespace (`auth`).
- Exposes an HTTP callback to receive Google OAuth redirects.

### Prerequisites
- Running Robutler Portal (Next.js) and Agents service.
- `r-google-calendar` agent exists in the Portal and has an API key.
- The Agents service is publicly reachable at a base URL (can be local) for agent routes.

### Environment variables (Agents service)
Set these in the Agents service environment:

- `GOOGLE_CLIENT_ID`: OAuth 2.0 Client ID
- `GOOGLE_CLIENT_SECRET`: OAuth 2.0 Client Secret
- `AGENT_PUBLIC_BASE_URL`: Base URL where agents are reachable, for example `http://localhost:8000/agents`

Example (bash):
```
export GOOGLE_CLIENT_ID=xxxxxxxx.apps.googleusercontent.com
export GOOGLE_CLIENT_SECRET=xxxxxxxx
export AGENT_PUBLIC_BASE_URL=http://localhost:8000/agents
```

### Google Cloud Console setup
1. Create OAuth 2.0 credentials (Web application) in Google Cloud Console.
2. Authorized redirect URI (must match exactly):
   - `{AGENT_PUBLIC_BASE_URL}/r-google-calendar/oauth/google/calendar/callback`
   - Example: `http://localhost:8000/agents/r-google-calendar/oauth/google/calendar/callback`
3. Scopes used by the skill:
   - `https://www.googleapis.com/auth/calendar.readonly`
   - `https://www.googleapis.com/auth/calendar.events.readonly`

### KV Store (Portal) – Token persistence
The skill persists tokens in the Portal’s key-value API under the `auth` namespace.
Entries are per-user and per-agent:
- key: `gcal_tokens_<userId>`
- namespace: `auth`

The Portal endpoint (already included):
- `POST /api/kv` – body `{ agentId, key, value, namespace? }`
- `GET /api/kv?agentId=...&key=...&namespace=...`
- `DELETE /api/kv?agentId=...&key=...&namespace=...`

Authentication:
- User cookie session OR `X-API-Key: <agent_api_key>` (agent’s own API key) are accepted.

### Dynamic Factory wiring
The Agents service factory automatically adds:
- `GoogleCalendarSkill` to the agent named `r-google-calendar`.
- `KVSkill` to agents (used by the calendar skill to persist tokens).

No manual registration of tools is required; tools are discovered and scoped by the SDK.

### Tools and HTTP endpoints
- Tools (owner scope where noted):
  - `init_calendar_auth()` – returns a Google consent URL to authorize access.
  - `list_events(max_results=10)` (owner) – lists upcoming events for the authorized user.
- HTTP callback:
  - `GET /{agentName}/oauth/google/calendar/callback?code=...&state=...`
  - The skill exchanges the `code` for tokens and saves them in KV under `namespace=auth`.

### How to test
1. Create `r-google-calendar` agent in Portal and mint an API key. Ensure the agent is dynamic and available.
2. Restart the Agents service so the dynamic factory loads the agent.
3. Ask the calendar agent to start auth (Options):
   - Via another agent (preferred): Instruct that agent to communicate with `r-google-calendar` and call `init_calendar_auth`. The skill will respond with an authorization URL.
   - Direct HTTP (simple): Call chat completions and prompt the agent to call the tool.
     ```
     POST {AGENT_PUBLIC_BASE_URL}/r-google-calendar/chat/completions
     Headers:
       Content-Type: application/json
       X-API-Key: <r-google-calendar agent API key>
     Body:
       {
         "messages": [
           {"role": "user", "content": "Call init_calendar_auth now and give me the URL"}
         ]
       }
     ```
     The response should include an authorization link. Open it and complete the Google consent screen.
4. After consenting, Google redirects to `/{agentName}/oauth/google/calendar/callback`.
   - On success, tokens are saved in KV (namespace `auth`):
     - key: `gcal_tokens_<userId>`
5. Verify events:
   - Prompt the agent: “List my next 5 events” (or explicitly “call list_events with max_results=5”).
   - The tool should return your upcoming events or a message prompting to re-authorize if tokens are invalid/expired.

### Verifying token storage (optional)
Using the Portal API, you can verify the stored token:
```
GET http://localhost:3000/api/kv?agentId=<AGENT_ID>&key=gcal_tokens_<USER_ID>&namespace=auth
Headers:
  X-API-Key: <r-google-calendar agent API key>
```
If present, the JSON access/refresh token payload will be returned in `value`.

### Troubleshooting
- 401 Unauthorized from `/api/kv`: ensure you pass `X-API-Key` for the calendar agent or are authenticated as the user owning the data.
- OAuth redirect mismatch: check `AGENT_PUBLIC_BASE_URL` and the Google Console Authorized Redirect URI.
- Tool not visible: ensure your request is evaluated under the OWNER scope for the agent (owner assertion or agent API key flow).
- Empty events: confirm tokens were stored and valid; re-run `init_calendar_auth` if needed.



