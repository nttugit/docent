import random
from itertools import pairwise

import pytest

from docent.ingest.chunking import Chunk, chunk_document

PROSE = "\n\n".join(
    f"Section {i}. The Licensee shall pay the Licensor a royalty of {i}% of Net Sales. "
    "Payments are due within thirty (30) days after the end of each calendar quarter."
    for i in range(1, 40)
)

CUAD_LIKE = (
    "Exhibit 10.13\n\nConfidential Materials omitted.\n\nDATED: OCTOBER 15, 2009\n\n"
    "PACIRA PHARMACEUTICALS, INC.\n\nand\n\nEKR THERAPEUTICS, INC.        AMENDED AND "
    'RESTATED   STRATEGIC LICENSING AGREEMENT\n\n\n\n\n\nTHIS AGREEMENT (the  "Agreement") '
    "is made on October 15, 2009 between:   PACIRA, INC. a Delaware corporation.\n\n"
    '          1.1 "Affiliate" means any entity.\n  \n\t\n2.  Term.  \r\n\r\nThe term '
    "is five (5) years.            Page 3 of 40\n\n\n\n"
) * 20

UNICODE = (
    "Le présent Contrat est régi par le droit français. Élection de for à Paris.\n\n"
    "本合同受中华人民共和国法律管辖。双方应友好协商解决争议。\n\n"
    "Die Vertragsparteien vereinbaren Folgendes: Gerichtsstand ist München. "
    "Ñandú — “quoted” clause.\n\n"
) * 30


def _random_text(seed: int) -> str:
    rng = random.Random(seed)  # noqa: S311 (deterministic test data, not crypto)
    words = ["agreement", "party", "Licensee.", "shall", "é", "合同。", "x" * 70, "(a)", "Inc."]
    seps = [" ", "  ", "\n", "\n\n", "\n \n", "\t", "\r\n\r\n", "            "]
    return "".join(rng.choice(words) + rng.choice(seps) for _ in range(800))


TEXTS = {
    "prose": PROSE,
    "cuad_like": CUAD_LIKE,
    "unicode": UNICODE,
    "random0": _random_text(0),
    "random1": _random_text(1),
    "one_long_paragraph": "word " * 2000,
    "one_huge_token": "x" * 3500,
    "short": "  Short contract.  ",
}
PARAMS = [(1500, 200), (1000, 200), (300, 50), (100, 99), (50, 0), (1, 0)]


def _assert_invariants(text: str, chunks: list[Chunk], max_chars: int, overlap: int) -> None:
    covered = [False] * len(text)
    for i, c in enumerate(chunks):
        assert c.index == i
        assert c.chunk_id == f"doc:{i}"
        assert c.doc_id == "doc"
        assert text[c.char_start : c.char_end] == c.text
        assert 0 < len(c.text) <= max_chars
        assert c.text == c.text.strip() or not c.text.strip()
        assert not c.text[0].isspace()
        assert not c.text[-1].isspace()
        for pos in range(c.char_start, c.char_end):
            covered[pos] = True
        if i:
            prev = chunks[i - 1]
            assert prev.char_start < c.char_start
            assert prev.char_end < c.char_end
            assert max(0, prev.char_end - c.char_start) <= overlap
    uncovered = [i for i, ch in enumerate(text) if not ch.isspace() and not covered[i]]
    assert uncovered == []


@pytest.mark.parametrize(("max_chars", "overlap"), PARAMS)
@pytest.mark.parametrize("name", TEXTS)
def test_invariants(name: str, max_chars: int, overlap: int) -> None:
    text = TEXTS[name]
    chunks = chunk_document("doc", text, max_chars=max_chars, overlap_chars=overlap)
    _assert_invariants(text, chunks, max_chars, overlap)


@pytest.mark.parametrize("name", TEXTS)
def test_deterministic(name: str) -> None:
    assert chunk_document("doc", TEXTS[name]) == chunk_document("doc", TEXTS[name])


@pytest.mark.parametrize("text", ["", " ", "\n\n\n", " \t\r\n\f\v ", "\u3000\u00a0"])
def test_empty_or_whitespace_only(text: str) -> None:
    assert chunk_document("doc", text) == []


def test_short_text_single_trimmed_chunk() -> None:
    text = "\n\n  Short contract.  \n"
    [c] = chunk_document("d1", text)
    assert c == Chunk(
        chunk_id="d1:0", doc_id="d1", index=0, text="Short contract.", char_start=4, char_end=19
    )


def test_packs_paragraphs_up_to_max_chars() -> None:
    text = "aaaa\n\nbbbb\n\ncccc"
    chunks = chunk_document("doc", text, max_chars=10, overlap_chars=0)
    assert [c.text for c in chunks] == ["aaaa\n\nbbbb", "cccc"]


def test_long_paragraph_splits_at_sentence_boundaries() -> None:
    sentences = [f"Sentence number {i} is here." for i in range(10)]
    text = " ".join(sentences)
    chunks = chunk_document("doc", text, max_chars=60, overlap_chars=0)
    assert len(chunks) > 1
    for c in chunks:
        assert c.text.endswith(".")
        assert c.text.startswith("Sentence")


def test_long_sentence_splits_at_whitespace() -> None:
    text = " ".join(f"w{i:03d}" for i in range(200))
    chunks = chunk_document("doc", text, max_chars=50, overlap_chars=0)
    words = text.split()
    for c in chunks:
        assert all(w in words for w in c.text.split())
    assert [w for c in chunks for w in c.text.split()] == words


def test_token_longer_than_max_chars_is_hard_cut() -> None:
    text = "start " + "x" * 2500 + " end"
    chunks = chunk_document("doc", text, max_chars=1000, overlap_chars=200)
    assert [c.text for c in chunks] == ["start", "x" * 1000, "x" * 1000, "x" * 500 + " end"]


def test_overlap_snaps_to_word_boundary() -> None:
    text = " ".join(f"word{i}" for i in range(400))
    chunks = chunk_document("doc", text, max_chars=200, overlap_chars=40)
    assert len(chunks) > 1
    for prev, cur in pairwise(chunks):
        overlap = prev.char_end - cur.char_start
        assert 0 < overlap <= 40
        assert text[cur.char_start - 1] == " "


def test_overlap_zero_gives_disjoint_chunks() -> None:
    chunks = chunk_document("doc", PROSE, max_chars=500, overlap_chars=0)
    for prev, cur in pairwise(chunks):
        assert prev.char_end <= cur.char_start


def test_unicode_offsets_are_code_points() -> None:
    text = "  Élection  de for.\n\n本合同受法律管辖。  "
    chunks = chunk_document("doc", text, max_chars=1500)
    [c] = chunks
    assert c.char_start == 2
    assert c.text == "Élection  de for.\n\n本合同受法律管辖。"


def test_preserves_irregular_internal_whitespace() -> None:
    text = 'THIS AGREEMENT (the  "Agreement")   between:\t PACIRA'
    [c] = chunk_document("doc", text)
    assert c.text == text


@pytest.mark.parametrize(
    ("max_chars", "overlap"),
    [(0, 0), (-1, 0), (100, -1), (100, 100), (100, 101)],
)
def test_invalid_args_raise(max_chars: int, overlap: int) -> None:
    with pytest.raises(ValueError, match="must be"):
        chunk_document("doc", "text", max_chars=max_chars, overlap_chars=overlap)
