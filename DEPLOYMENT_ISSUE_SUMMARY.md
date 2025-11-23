# Fly.io Deployment Failure — Image Too Large

## What happened
- GitHub Actions run `19597802122` failed during “Deploy to Fly.io” after ~23m52s.
- Image built successfully (reported ~3.4 GB compressed), but machine never reached a running state.
- Fly app `lovable-mcp-gateway` currently has **no machines** running.

## Evidence
- Workflow log: `Error: timeout reached waiting for machine's state to change`; machine `48e7363a74e378` created but never started.
- Fly logs (multiple regions): `Not enough space to unpack image, possibly exceeds maximum of 8GB uncompressed`.
- `fly status --app lovable-mcp-gateway`: shows app with hostname but no image/machines.

## Likely root cause
- Uncompressed image exceeds Fly’s ~8GB root filesystem limit; unpack fails, so the machine cannot start.
- Heavy dependency stack (browser automation + ML/LLM libs such as torch/transformers/langchain) bloats the image.

## Options to fix
1) **Increase root filesystem size (if plan allows)**
   - Example: `fly deploy --ha=false --vm-memory 16384 --vm-rootfs-size 20` (or set `rootfs_size_gb = 20` in `fly.toml` if supported).
   - Pros: fast to try. Cons: may still be close to limits; slower cold starts; may incur cost/plan constraints.

2) **Slim the image (preferred for long-term stability)**
   - Split into two services: thin FastAPI gateway (auth/validation) + separate worker for Playwright/LLM (browser-use). Gateway image stays small and deploys fast; worker can be heavier and scaled separately.
   - If keeping monolith: remove or gate heavy deps not needed at runtime (torch/transformers/faiss/langchain-*). Create a “light” dependency set for production and adjust `pyproject.toml`/Docker accordingly.
   - Verify apt layer is minimal; avoid copying build caches; keep dev deps out (already using `--no-dev`).

## Suggested next steps
- Decide short-term path:
  - If urgency > refactor: try larger rootfs deploy to confirm the app starts.
  - If stability/operability > speed: start slimming (gateway/worker split or light deps).
- After successful deploy: run health/auth checks, `/tools/run_browser_agent` smoke, and rate-limit/concurrency probes.
- Add CI guard: enforce image-size budget (e.g., `docker build` then `docker image inspect` size check) and keep heavy deps isolated.
