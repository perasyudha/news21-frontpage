#!/usr/bin/env python3
"""Copy the rendered front page to the make.fun output directory.

The gate reads the PNG header and the byte count, so the copy is checked
against both before and after it is written: the whole payload is hashed
again from disk, which catches a short write or a leftover file from an
earlier run just as plainly as it catches a truncated read.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

MAX_BYTES = 1 << 20  # the gate's 1 MiB cap
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
NAME = "entry.png"

source = Path(__file__).resolve().parent / NAME
data = source.read_bytes()

if len(data) > MAX_BYTES:
    sys.exit(f"entry.png is {len(data)} bytes, over the {MAX_BYTES}-byte cap")
if not data.startswith(PNG_SIGNATURE):
    sys.exit("entry.png does not start with the PNG signature")

output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
output_dir.mkdir(parents=True, exist_ok=True)
destination = output_dir / NAME
destination.write_bytes(data)

expected = hashlib.sha256(data).hexdigest()
actual = hashlib.sha256(destination.read_bytes()).hexdigest()
if actual != expected:
    sys.exit(f"copy differs from source: {actual} != {expected}")

print(f"wrote {destination} ({len(data)} bytes, sha256 {expected[:12]})")

