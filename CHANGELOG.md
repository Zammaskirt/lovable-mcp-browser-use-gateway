# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-01-21

### Added
- Initial release of Lovable MCP Gateway
- FastAPI HTTP gateway wrapping Saik0s `mcp-server-browser-use` engine
- Bearer token authentication middleware
- Per-IP rate limiting with slowapi
- Global concurrency control with asyncio.Semaphore
- Structured JSON logging with structlog
- PRD-compliant response contracts
  - Success responses with preview URL extraction
  - Error responses with mapped error codes
- Saik0s CLI delegation layer (agent_runner.py)
  - Subprocess-based invocation for stability
  - Tenacity retry logic
  - Timeout protection
- Lovable adapter module (optional)
  - Deterministic Playwright selectors
  - Helper flows for login, project creation, build triggering
  - Preview URL extraction
- Auth state generator script (save_auth_state.py)
  - Manual Lovable login with Playwright
  - Storage state persistence
- Docker support
  - Multi-stage Dockerfile
  - Playwright Chromium installation
  - System dependency management
- Fly.io deployment
  - fly.toml.example configuration
  - Health checks
  - Autoscaling support (optional)
- GitHub Actions CI/CD
  - Automated testing on PR/push
  - Linting with ruff and black
  - Type checking with mypy
  - Automated deployment to Fly.io on main branch
- Comprehensive documentation
  - README.md with quick start guide
  - SECURITY.md with threat model and best practices
  - CHANGELOG.md (this file)
- Test suite
  - Unit tests for URL extraction and error mapping
  - E2E smoke tests for gateway endpoints
  - Response model validation tests

### Configuration
- Environment variables for all settings
- .env.example with documented options
- Support for OpenRouter LLM provider
- Configurable rate limits and concurrency
- Optional vision/screenshot analysis
- Optional auth state path configuration

### Error Handling
- Error code mapping:
  - TIMEOUT_BUILD: Execution timeout
  - AUTH_EXPIRED: Authentication failure
  - UI_CHANGED: Selector/element not found
  - NETWORK_ERROR: Connection issues
  - UNKNOWN_ERROR: Other failures
- Graceful error responses with run_id for tracing

### Security
- No secrets in code
- Bearer token required for all endpoints except /health
- Rate limiting per IP
- Global concurrency limits
- Structured logging without credential exposure
- Input validation with Pydantic

## Future Roadmap

### v0.2.0 (Planned)
- [ ] WebSocket support for streaming responses
- [ ] Request queuing with priority levels
- [ ] Metrics/Prometheus endpoint
- [ ] Advanced error recovery strategies
- [ ] Support for multiple LLM providers in single request
- [ ] Caching layer for repeated tasks

### v0.3.0 (Planned)
- [ ] Database persistence for request history
- [ ] User management and API key rotation
- [ ] Advanced analytics and reporting
- [ ] Custom webhook notifications
- [ ] Batch request processing

## Known Limitations

- Single worker process (Fly.io can scale horizontally)
- No persistent storage (stateless design)
- Lovable UI changes may require selector updates
- Browser automation inherently slower than API calls
- Auth state expires periodically (requires regeneration)

## Migration Guide

### From v0.0.0 to v0.1.0
This is the initial release. No migration needed.

## Support

For issues, questions, or contributions:
- GitHub Issues: [link]
- Documentation: See README.md and SECURITY.md
- Security Issues: See SECURITY.md for reporting guidelines

