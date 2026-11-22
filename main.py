#!/usr/bin/env python3
"""Copy the rendered front page to the make.fun output directory."""

from pathlib import Path
import os

OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
SOURCE = Path(__file__).resolve().parent / "entry.png"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "entry.png").write_bytes(SOURCE.read_bytes())
