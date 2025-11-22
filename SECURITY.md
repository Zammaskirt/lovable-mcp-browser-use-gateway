# Security Policy

## Threat Model

This gateway automates browser interactions with Lovable.dev. Key security considerations:

### 1. Authentication & Authorization
- **Bearer Token**: Required for all endpoints except `/health`
- **No Credential Leakage**: LLM API keys and auth state are never exposed in responses
- **Token Validation**: Middleware validates token on every request

### 2. Rate Limiting
- **Per-IP Limiting**: Prevents abuse from single source
- **Global Concurrency**: Limits resource consumption
- **Configuration**: `MCP_RATE_LIMIT_PER_MIN` and `MCP_AGENT_CONCURRENCY`

### 3. Secrets Management
- **Never in Code**: All secrets via environment variables
- **Fly.io Secrets**: Use `fly secrets set` for production
- **Auth State**: Stored as Fly secret, not in repository
- **No Logging**: Secrets not logged or exposed in responses

### 4. Browser Automation
- **Headless Mode**: Recommended for production (`MCP_BROWSER_HEADLESS=true`)
- **Isolated Context**: Each request gets isolated browser context
- **Timeout Protection**: `MCP_AGENT_TIMEOUT_SEC` prevents runaway tasks
- **Resource Limits**: Concurrency semaphore prevents resource exhaustion

### 5. Input Validation
- **Pydantic Models**: All inputs validated
- **Task Sanitization**: Tasks passed to Saik0s are not executed as shell commands
- **No Code Injection**: Saik0s CLI is invoked safely via subprocess

### 6. Output Handling
- **Error Mapping**: Errors mapped to generic codes (no internal details leaked)
- **Response Filtering**: Only safe data returned to client
- **No Stack Traces**: Internal errors don't expose implementation details

## Best Practices

### Deployment
1. **Use HTTPS**: Fly.io enforces HTTPS by default
2. **Strong Tokens**: Generate cryptographically secure bearer tokens
3. **Rotate Secrets**: Regularly rotate API keys and auth state
4. **Monitor Logs**: Check for suspicious activity

### Configuration
1. **Minimal Permissions**: Only enable needed features
2. **Headless Mode**: Always use `MCP_BROWSER_HEADLESS=true` in production
3. **Rate Limits**: Adjust based on expected load
4. **Concurrency**: Set to reasonable limits (3-5 for most use cases)

### Monitoring
1. **Health Checks**: Fly.io performs automatic health checks
2. **Logs**: Monitor for auth failures, timeouts, errors
3. **Metrics**: Track request rates and response times

## Incident Response

### Compromised Bearer Token
1. Generate new token
2. Update `MCP_BEARER_TOKEN` secret
3. Redeploy: `fly deploy`
4. Monitor for unauthorized requests

### Lovable Auth Expired
1. Regenerate auth state: `python scripts/save_auth_state.py ./auth.json`
2. Update secret: `fly secrets set MCP_AUTH_STATE_PATH=@./auth.json`
3. Redeploy: `fly deploy`

### Rate Limit Abuse
1. Check logs for suspicious IPs
2. Increase `MCP_RATE_LIMIT_PER_MIN` if legitimate
3. Consider IP-based blocking at Fly.io level

## Compliance

- **No Data Storage**: Gateway doesn't persist user data
- **No Tracking**: No analytics or telemetry
- **Stateless**: Each request is independent
- **Audit Trail**: All requests logged with run_id for tracing

## Reporting Security Issues

Do not open public issues for security vulnerabilities.

Contact: [security contact info]

## Dependencies

Security updates for dependencies:
- `mcp-server-browser-use`: Monitor GitHub releases
- `fastapi`: Security patches applied automatically
- `playwright`: Keep updated for browser security

Run `uv sync` regularly to get security updates.

