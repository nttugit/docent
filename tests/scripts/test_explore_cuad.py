import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "explore_cuad.py"


@pytest.fixture(scope="module")
def ex() -> ModuleType:
    spec = importlib.util.spec_from_file_location("explore_cuad", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    # dataclasses resolve string annotations via sys.modules[cls.__module__]
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_percentile_nearest_rank(ex: ModuleType) -> None:
    values = list(range(1, 101))
    assert ex.percentile(values, 95) == 95
    assert ex.percentile(values, 100) == 100
    assert ex.percentile([7], 50) == 7


def test_percentile_empty_raises(ex: ModuleType) -> None:
    with pytest.raises(ValueError, match="empty"):
        ex.percentile([], 50)


@pytest.mark.parametrize(
    ("qa_id", "expected"),
    [
        ("Some Title__Parties", "Parties"),
        ("Some Title__Document Name_0", "Document Name"),
        ("T__Cap On Liability_12", "Cap On Liability"),
    ],
)
def test_category_of_id(ex: ModuleType, qa_id: str, expected: str) -> None:
    assert ex.category_of(qa_id, "") == expected


def test_category_of_falls_back_to_question(ex: ModuleType) -> None:
    question = 'Highlight the parts related to "Governing Law" that ...'
    assert ex.category_of("no-separator", question) == "Governing Law"


def _squad(context: str, answers: list[dict[str, object]]) -> dict[str, object]:
    qas = [{"id": "T__Parties", "question": "q", "answers": answers}]
    return {"data": [{"title": "T", "paragraphs": [{"context": context, "qas": qas}]}]}


def test_analyse_detects_offset_drift_after_strip(ex: ModuleType) -> None:
    context = "  Acme Corp\fPage 2 of 9"
    stats = ex.analyse(_squad(context, [{"text": "Acme", "answer_start": 2}]))
    assert stats.n_span_ok_raw == 1
    assert stats.n_span_ok_stripped == 0
    assert stats.n_context_padded == 1
    assert stats.n_form_feed == 1
    assert stats.page_hits["`Page N` / `Page N of M`"] == 1


def test_analyse_counts_unanswered(ex: ModuleType) -> None:
    stats = ex.analyse(_squad("text", []))
    assert stats.n_qas == 1
    assert stats.n_qas_no_answer == 1
    assert stats.n_answers == 0
    assert stats.categories == {"Parties"}
