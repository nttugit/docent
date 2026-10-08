"""Download and extract the CUAD v1 dataset (SQuAD format) into data/raw/cuad/.

Usage: uv run python scripts/download_cuad.py
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import urllib.request
import zipfile
from pathlib import Path

URL = "https://github.com/TheAtticusProject/cuad/raw/main/data.zip"
ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "raw" / "cuad"
ZIP_PATH = DEST / "data.zip"


def download(url: str, dest: Path) -> None:
    if not url.startswith("https://"):
        raise ValueError(f"refusing non-https URL: {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(url) as resp, tmp.open("wb") as out:  # noqa: S310 (scheme checked)
        shutil.copyfileobj(resp, out)
    tmp.replace(dest)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def extract(zip_path: Path, dest: Path) -> list[Path]:
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(dest)
        names = [n for n in zf.namelist() if not n.endswith("/")]
    return [dest / n for n in names]


def main() -> int:
    DEST.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.exists():
        print(f"zip exists, skipping download: {ZIP_PATH.relative_to(ROOT)}")
    else:
        print(f"downloading {URL} ...")
        download(URL, ZIP_PATH)

    print(f"sha256  {sha256(ZIP_PATH)}  {ZIP_PATH.relative_to(ROOT)}")
    for path in extract(ZIP_PATH, DEST):
        print(f"  {path.relative_to(ROOT)}  ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
