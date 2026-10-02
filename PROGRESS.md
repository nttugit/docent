<!-- Template
## Day N — YYYY-MM-DD — <theme>  (time: Xh / planned Yh)

**Issue:** #N

**Done:**
-

**Evidence:** (PR link, CI run, metric numbers, screenshots)

**Blockers / risks:**

**Decisions:** (→ ADR if significant)

**Learned:** 1 concept + 1 interview question I can now answer

**Tomorrow (top 3):**
1.
-->

## Day 1 — 2026-10-02 — Repo foundation  (time: _ / 2.5h)

**Issue:** #1

**Done:**
- [x] uv project, src layout, deps locked
- [x] pre-commit (ruff, mypy, gitleaks, conventional commits)
- [x] FastAPI /health + tests
- [x] Dockerfile multi-stage, smoke test passes
- [ ] CI green on main, branch protection on

**Evidence:**
- `make check`: 3 tests pass, coverage 100%, mypy strict 0 errors
- Docker image `docent:dev` (arm64, local): 271MB on disk / 59.2MB compressed. Baseline trước khi bake model (Day 11)
- Smoke: `GET /health` → 200 `{"status":"ok","version":"0.1.0","env":"dev"}`
- CI run: <link sau khi push>

**Blockers / risks:**
- Starlette TestClient báo deprecation warning cho httpx. Chỉ là warning; xem lại khi upgrade deps.

**Decisions:** ADR 0001

**Learned:**

**Tomorrow (top 3):**
1.
