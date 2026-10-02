# Docent

![CI](https://github.com/nttugit/docent/actions/workflows/ci.yml/badge.svg)

AI contract analytics: **classify** clauses, **extract** key fields, and **ask** questions with page-level citations — with evals gating every change.

> Status: Day 1/14 — foundation. See [PROGRESS.md](PROGRESS.md).

## Features (planned)
| Capability | Approach | Eval |
|---|---|---|
| Ask (RAG) | Hybrid search (BM25 + vector, RRF) + reranker + Gemini | Recall@k, MRR, faithfulness, citation accuracy |
| Classify | DistilBERT fine-tuned on LEDGAR (vs TF-IDF baseline) | Accuracy, macro-F1 |
| Extract | Gemini structured output → JSON schema | Exact / fuzzy match vs CUAD |

## Architecture
_TODO (Day 14): Mermaid diagram — see [ADR 0001](docs/adr/0001-architecture.md)._

## Quickstart
```bash
uv sync && cp .env.example .env
make run            # http://localhost:8000/docs
```

## Development
```bash
make install   # deps + git hooks
make check     # lint + typecheck + tests (same as CI)
make help      # all targets
```

## Eval results
_TODO: tables land Day 4, 6, 9, 10._

## Decisions
Architecture decisions live in [`docs/adr/`](docs/adr/).
