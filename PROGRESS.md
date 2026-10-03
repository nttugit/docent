## Day 1 — 2026-10-02 — Repo foundation  (time: ???h / 2.5h)

**Issue:** #1

**Done:**
- [x] uv project, src layout, deps locked
- [x] pre-commit (ruff, mypy, gitleaks, conventional commits)
- [x] FastAPI /health + tests
- [x] Dockerfile multi-stage, smoke test passes
- [x] CI green on main, branch protection on

**Evidence:**
- `make check`: 3 tests pass, coverage 100%, mypy strict 0 errors
- Docker image `docent:dev` (arm64, local): 271MB on disk / 59.2MB compressed. Baseline trước khi bake model (Day 11)
- Smoke: `GET /health` → 200 `{"status":"ok","version":"0.1.0","env":"dev"}`
- CI run: https://github.com/nttugit/docent/actions/runs/37065931632 (commit 9e6ff74)

**Blockers / risks:**
- Starlette TestClient báo deprecation warning cho httpx. Chỉ là warning; xem lại khi upgrade deps.

**Decisions:**
- ADR 0001 (modular monolith, hand-rolled RAG core, Cloud Run)
- Ruff và mypy chạy qua hook local `uv run` → uv.lock là nguồn version duy nhất
- `requires-python = ">=3.12,<3.13"` để tránh resolve fail với torch ở Day 8

**Learned:**
- Q: Pre-commit đã chạy ruff/mypy/gitleaks ở local, vì sao CI vẫn chạy lại? Nêu ≥ 2 lý do và 1 nhược điểm của việc CI chạy `pre-commit run --all-files`.
- A: Local hooks are a convenience, not an enforcement point: they can be skipped with —no-verify, never installed by a new contributor or bypassed by edits on Github’s web UI. CI is the gate, because it’s tied to branch protection, nothing merges without passing. CI also runs in a clean environment with tool versions pinned by the lock file, which removes “works on my machine” and version drift between developers. The trade-off of running pre-commit run —all-files in CI is that it re-checks unchanged files, so cost grows with repo size, and bundling all tools into one job makes failures less visible than separate jobs per tool.


**Tomorrow (top 3):**
1. Khám phá CUAD: cấu trúc dataset, số lượng hợp đồng, dạng answer span; chọn nguồn text hay PDF
2. Thiết kế model `Chunk` (doc_id, page, char_start, char_end) và tự viết chunker
3. Viết test round-trip `source[start:end] == chunk.text`
