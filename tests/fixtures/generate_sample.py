#!/usr/bin/env python3
"""
Generate a small sample ZIP for CI benchmark and tests/fixtures/sample.zip
"""
import zipfile
from pathlib import Path

OUT = Path("tests/fixtures")
OUT.mkdir(parents=True, exist_ok=True)
SAMPLE = OUT / "sample.zip"
with zipfile.ZipFile(SAMPLE, "w") as zf:
    zf.writestr("file1.txt", b"hello world")
    zf.writestr("dir1/file2.txt", b"another file")
    # Add a few more small files
    for i in range(5):
        zf.writestr(f"data/data_{i}.bin", b"x" * 1024)
print(f"Wrote sample zip: {SAMPLE}")
