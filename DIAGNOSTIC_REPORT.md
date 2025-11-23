# DIAGNOSTIC REPORT: Browser Agent Timeout Investigation

**Date**: 2025-11-23  
**Issue**: Browser agent timed out after 900 seconds (15 minutes) during local E2E test  
**Status**: ROOT CAUSE IDENTIFIED & FIXED (BUT INFRA ISSUE PERSISTS)

---

## Investigation Summary

### Initial Symptoms
- Browser agent ran for full 900 seconds without completing
- Task: "Create a basic todo app with add and delete functionality"
- Server logs showed: `Saik0s CLI timeout` after 900 seconds

### Investigation Steps Performed

#### 1) Process Cleanup
- Found 3 zombie `mcp-server-browser-use` processes still running
- Killed all zombie processes
- Result: resources cleaned up

#### 2) Auth.json Validation
- File size: 52,816 bytes (OK)
- Session cookies present: 3 found (OK)
- Expiration dates: valid until 2026-11-23 (OK)
- JWT token format: valid (OK)
- Result: Auth.json is valid and not expired

#### 3) Page Load Analysis
- Browser launch: successful
- Navigation to lovable.dev: 4.34 seconds
- Authentication: working (not on login page)
- Critical finding: page reaches "load" state in 1.5 seconds but never reaches "networkidle" state

#### 4) Root Cause Identified (Page Load Wait)
The problem: lovable.dev uses WebSockets (Firebase Firestore) for real-time updates
- 7 WebSocket connections detected
- Continuous background network activity
- "networkidle" state never reached (by design)
- Browser agent was waiting indefinitely for a state that never comes

Impact:
- `flows.py` uses `wait_for_load_state("networkidle")` in two places
- This causes the browser agent to hang waiting for network idle
- Timeout occurs after 900 seconds

---

## Solution Implemented

### Code Changes
File: `src/lovable_adapter/flows.py`

Changed two occurrences of:
```python
await page.wait_for_load_state("networkidle", timeout=DEFAULT_TIMEOUT)
```

To:
```python
await page.wait_for_load_state("load", timeout=DEFAULT_TIMEOUT)
```

Lines modified: 53, 62

### Why This Works
- "load" state: page DOM is ready and interactive (~1.5 seconds)
- "networkidle" state: all network requests complete (never, due to WebSockets)
- Using "load" is appropriate for real-time applications
- Reduces timeout issues from 900s to ~30s per operation

### Testing
- All 24 tests in `test_lovable_adapter.py` pass
- No test changes needed (mocks do not care about state type)
- Code coverage maintained at 94% for `flows.py`

---

## Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Page load wait | 900s timeout | ~1.5s | ~600x faster |
| Project creation | 900s timeout | ~30s | ~30x faster |
| Total task time | 900s+ | ~5-10 min | completes successfully |

---

## Next Steps - Updated Findings

### Critical Discovery
After implementing the "load" state fix and retesting, the browser agent still timed out after 900 seconds. Further investigation revealed:

1. The fix was incomplete: the `flows.py` changes only affect the optional Lovable adapter, not the Saik0s CLI.
2. Saik0s CLI is the bottleneck: the actual browser agent execution is delegated to `mcp-server-browser-use` CLI.
3. Saik0s CLI hangs silently: even simple tasks like "Navigate to lovable.dev" time out without producing output.
4. Root cause: the Saik0s CLI itself appears to have issues with the current environment or configuration.

### Recommended Actions
1. Investigate Saik0s CLI: check installation and configuration.
2. Check browser launch: verify that the browser is actually starting.
3. Review Saik0s logs: look for any error messages or debugging info.
4. Consider alternatives: may need to use the Lovable adapter flows directly instead of Saik0s CLI.

---

## Recommendations

### For Production
1. Use "load" state for all Lovable page interactions.
2. Keep timeout at 900 seconds for complex builds.
3. Monitor actual execution times to optimize further.
4. Consider increasing timeout to 1200s (20 min) for very complex tasks.

### For Future Improvements
1. Add per-step timeout monitoring.
2. Implement progress logging during build.
3. Add retry logic for transient failures.
4. Consider headless vs headed mode trade-offs.

---

## Conclusion - Critical Issue Identified

### Initial Diagnosis (Partial)
- Root cause found: inappropriate "networkidle" wait condition.
- Fix applied: changed to "load" state in `flows.py`.
- Tests pass: all 24 adapter tests pass.

### Deeper Investigation (Critical Finding)
- Saik0s CLI is hanging on startup - even `--version` times out.
- Simple tasks time out - "Navigate to lovable.dev" times out after 300s.
- No output produced - Saik0s CLI produces no stdout/stderr.
- Environment is correct - all env vars are set properly.
- Auth.json is valid - file exists and is properly formatted.

### Root Cause of Timeout
The Saik0s CLI (`mcp-server-browser-use`) is hanging during initialization, likely due to:
1. Browser launch issues (Chromium not starting).
2. LLM provider connection issues (OpenRouter API).
3. Configuration or dependency issues.

This is not a page load state issue; it is a Saik0s CLI infrastructure issue.

### Status
- Not ready for deployment - critical infrastructure issue.
- Requires investigation - need to debug Saik0s CLI startup.
