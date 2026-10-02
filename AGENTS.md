# AGENTS.md — Docent

Contract analytics service: **classify** clauses (fine-tuned DistilBERT on LEDGAR), **extract** key fields to JSON (Gemini structured output), **ask** questions via RAG with page-level citations (CUAD). Every capability has an eval; CI gates on retrieval metrics.

## Commands
- `make install` — sync deps (locked) + install git hooks
- `make check`   — lint + typecheck + tests w/ coverage (what CI runs)
- `make run`     — dev server on :8000 (`/health`, `/docs`)
- `make docker-build && make docker-run` — container on :8000

## Layout
- `src/docent/{ingest,retrieval,llm,classify,evals,api}` — see `.cursor/rules/python.mdc` for boundaries
- `src/docent/config.py` — all settings from env (pydantic-settings)
- `tests/` mirrors `src/`
- `evals/datasets` (golden sets, committed) · `evals/reports` (generated, gitignored)
- `docs/adr/` — architecture decisions · `PROGRESS.md` — daily log

## Definition of done (any change)
1. `make check` green locally  2. tests for new behavior  3. `.env.example` / README updated if config or usage changed  4. Conventional Commit message
