"""Structure-aware chunking with exact character offsets into the original text."""

from __future__ import annotations

import re
from collections.abc import Iterator

from pydantic import BaseModel

_BLANK_LINE = re.compile(r"\n[^\S\n]*\n")
_SENTENCE_GAP = re.compile(r"""[.!?]["'\u201d\u2019)\]]*(\s+)""")
_WHITESPACE = re.compile(r"\s+")

Span = tuple[int, int]


class Chunk(BaseModel, frozen=True):
    chunk_id: str  # f"{doc_id}:{index}"
    doc_id: str
    index: int
    text: str
    char_start: int
    char_end: int  # exclusive
    page: int | None = None


def _trim(text: str, start: int, end: int) -> Span:
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    return start, end


def _split(text: str, span: Span, pattern: re.Pattern[str], group: int = 0) -> list[Span]:
    """Split `span` at matches of `group` in `pattern`; returns trimmed, non-empty spans."""
    start, end = span
    pieces: list[Span] = []
    pos = start
    for m in pattern.finditer(text, start, end):
        gap_start, gap_end = m.span(group)
        pieces.append((pos, gap_start))
        pos = gap_end
    pieces.append((pos, end))
    trimmed = (_trim(text, s, e) for s, e in pieces)
    return [(s, e) for s, e in trimmed if s < e]


def _atoms(text: str, max_chars: int) -> Iterator[Span]:
    """Yield ordered, disjoint spans of at most `max_chars` covering all non-whitespace.

    Paragraphs if they fit, else sentences, else whitespace-delimited tokens, else hard cuts.
    """
    for para in _split(text, (0, len(text)), _BLANK_LINE):
        if para[1] - para[0] <= max_chars:
            yield para
            continue
        for sent in _split(text, para, _SENTENCE_GAP, group=1):
            if sent[1] - sent[0] <= max_chars:
                yield sent
                continue
            for tok_start, tok_end in _split(text, sent, _WHITESPACE):
                for cut in range(tok_start, tok_end, max_chars):
                    yield cut, min(cut + max_chars, tok_end)


def _snap_forward(text: str, pos: int, limit: int) -> int:
    """Move `pos` forward to the start of the next word, never past `limit`."""
    while pos < limit and pos > 0 and not text[pos - 1].isspace():
        pos += 1
    while pos < limit and text[pos].isspace():
        pos += 1
    return pos


def chunk_document(
    doc_id: str, text: str, *, max_chars: int = 1500, overlap_chars: int = 200
) -> list[Chunk]:
    """Split `text` into overlapping chunks that respect paragraph and sentence boundaries.

    The input is never modified: every chunk satisfies
    ``chunk.text == text[chunk.char_start:chunk.char_end]`` and ``len(chunk.text) <= max_chars``.
    Consecutive chunks overlap by at most ``overlap_chars``.

    Raises:
        ValueError: if ``max_chars <= 0`` or ``overlap_chars`` is not in ``[0, max_chars)``.
    """
    if max_chars <= 0:
        raise ValueError(f"max_chars must be > 0, got {max_chars}")
    if not 0 <= overlap_chars < max_chars:
        raise ValueError(f"overlap_chars must be in [0, max_chars), got {overlap_chars}")

    atoms = list(_atoms(text, max_chars))
    spans: list[Span] = []
    i = 0
    while i < len(atoms):
        first_start, first_end = atoms[i]
        start = first_start
        if spans and overlap_chars:
            prev_start, prev_end = spans[-1]
            # Leave room for the first atom so the chunk still fits in max_chars.
            lo = max(prev_end - overlap_chars, first_end - max_chars, prev_start)
            if lo < first_start:
                start = _snap_forward(text, lo, first_start)

        end = first_end
        i += 1
        while i < len(atoms) and atoms[i][1] - start <= max_chars:
            end = atoms[i][1]
            i += 1
        spans.append(_trim(text, start, end))

    return [
        Chunk(
            chunk_id=f"{doc_id}:{index}",
            doc_id=doc_id,
            index=index,
            text=text[start:end],
            char_start=start,
            char_end=end,
        )
        for index, (start, end) in enumerate(spans)
    ]
