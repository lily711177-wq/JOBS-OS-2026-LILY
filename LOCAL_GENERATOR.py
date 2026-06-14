#!/usr/bin/env python3
"""
LOCAL GENERATOR — JOBS OS Lily Edition
Reads local_config.json, replaces [NAME]/[PHONE]/[EMAIL] placeholders,
outputs real-name TXT files locally (gitignored).

Usage:
  python3 LOCAL_GENERATOR.py                  # Process all SHOOT_*.md files found
  python3 LOCAL_GENERATOR.py --all             # Process ALL markdown files
  python3 LOCAL_GENERATOR.py path/to/file.md   # Process specific file
"""

import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
CONFIG = ROOT / "local_config.json"
OUTPUT = ROOT / "OUTPUT"

REPLACE_MAP = {}

def load_config():
    global REPLACE_MAP
    if not CONFIG.exists():
        print(f"ERROR: {CONFIG} not found. Create it with your real info.")
        print("Template:")
        print('  {"name": "Your Name", "phone": "[PHONE]", "email": "[EMAIL]"}')
        sys.exit(1)
    with open(CONFIG) as f:
        cfg = json.load(f)
    REPLACE_MAP = {
        "[NAME]": cfg.get("name", "[NAME]"),
        "[PHONE]": cfg.get("phone", "[PHONE]"),
        "[EMAIL]": cfg.get("email", "[EMAIL]"),
        "[LINKEDIN]": cfg.get("linkedin", "[LINKEDIN]"),
    }
    return cfg

def replace_placeholders(text):
    for k, v in REPLACE_MAP.items():
        text = text.replace(k, v)
    return text

def process_file(md_path):
    if not md_path.exists():
        print(f"  SKIP: {md_path} not found")
        return

    text = md_path.read_text(encoding="utf-8")
    resolved = replace_placeholders(text)

    stem = md_path.stem.replace("SHOOT_", "RESUME_")
    txt_path = OUTPUT / f"{stem}.txt"
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    txt_path.write_text(resolved, encoding="utf-8")
    print(f"  ✓ {txt_path}")

    # Also extract just the resume section if it exists
    resume_match = re.search(r"## 3\. RESUME TEXT.*?\n(.*?)(?=\n## \d|\Z)", resolved, re.DOTALL)
    if resume_match:
        resume_only = resume_match.group(1).strip()
        resume_path = OUTPUT / f"{stem}_resume_only.txt"
        resume_path.write_text(resume_only, encoding="utf-8")
        print(f"  ✓ {resume_path} (resume text only)")

def main():
    load_config()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    targets = []
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        targets = sorted(ROOT.rglob("*.md"))
        targets = [t for t in targets if ".git" not in str(t) and t.name != "README.md" and t.name != "AGENTS.md"]
    elif len(sys.argv) > 1:
        p = ROOT / sys.argv[1]
        if p.exists():
            targets = [p]
        else:
            targets = sorted(ROOT.rglob(sys.argv[1]))
    else:
        targets = sorted(ROOT.rglob("SHOOT_*.md"))

    if not targets:
        print("No SHOOT files found. Run SHOOT first or specify a file.")
        print("Usage: python3 LOCAL_GENERATOR.py [file.md | --all]")
        return

    print(f"Generating real-name files ({len(targets)} document(s))...")
    print(f"Config: {REPLACE_MAP['[NAME]']} | {REPLACE_MAP['[EMAIL]']}")
    for t in targets:
        process_file(t)

    print(f"\nDone. Files in: {OUTPUT}/")
    print("These files are gitignored — safe for local use.")

if __name__ == "__main__":
    main()
