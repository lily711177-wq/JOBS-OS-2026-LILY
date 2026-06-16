#!/usr/bin/env python3
"""
LOCAL GENERATOR — JOBS OS Lily Edition
Reads local_config.json, replaces [NAME]/[PHONE]/[EMAIL] placeholders,
outputs real-name TXT + DOCX files locally (gitignored).

Usage:
  python3 LOCAL_GENERATOR.py                  # Process all SHOOT_*.md files
  python3 LOCAL_GENERATOR.py --all             # Process ALL markdown files
  python3 LOCAL_GENERATOR.py path/to/file.md   # Process specific file
"""

import io
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent
CONFIG = ROOT / "local_config.json"
OUTPUT = ROOT / "OUTPUT"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"

def w(tag):
    return f"{{{W_NS}}}{tag}"

REPLACE_MAP = {}

def load_config():
    global REPLACE_MAP
    if not CONFIG.exists():
        print(f"ERROR: {CONFIG} not found.")
        print('Create it: {"name": "Lily", "phone": "[PHONE]", "email": "[EMAIL]"}')
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

def md_to_docx_parts(text):
    body = ET.Element(w("body"))
    for line in text.split("\n"):
        stripped = line.strip()
        if not stripped:
            ET.SubElement(body, w("p"))
            continue
        p = ET.SubElement(body, w("p"))
        pPr = ET.SubElement(p, w("pPr"))
        if stripped.startswith("**") and "**" in stripped[2:]:
            clean = stripped.replace("**", "")
            pStyle = ET.SubElement(pPr, w("pStyle"))
            pStyle.set(w("val"), "Heading1")
            r = ET.SubElement(p, w("r"))
            rPr = ET.SubElement(r, w("rPr"))
            ET.SubElement(rPr, w("b"))
            sz = ET.SubElement(rPr, w("sz"))
            sz.set(w("val"), "28")
            t = ET.SubElement(r, w("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = clean
            continue
        if stripped.startswith("- "):
            bullet = stripped[2:]
            pStyle = ET.SubElement(pPr, w("pStyle"))
            pStyle.set(w("val"), "ListBullet")
            r = ET.SubElement(p, w("r"))
            t = ET.SubElement(r, w("t"))
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            t.text = bullet
            continue
        r = ET.SubElement(p, w("r"))
        t = ET.SubElement(r, w("t"))
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        t.text = stripped
    return body

def build_docx(doc_body):
    doc = ET.Element(w("document"))
    doc.set("xmlns:w", W_NS)
    doc.set("xmlns:r", R_NS)
    doc.append(doc_body)
    doc_xml = ET.tostring(doc, encoding="UTF-8", xml_declaration=True)

    ct = ET.Element("Types", xmlns=CT_NS)
    for ext, ct_val in [("rels", "application/vnd.openxmlformats-package.relationships+xml"),
                         ("xml", "application/xml")]:
        d = ET.SubElement(ct, "Default")
        d.set("Extension", ext)
        d.set("ContentType", ct_val)
    ov = ET.SubElement(ct, "Override")
    ov.set("PartName", "/word/document.xml")
    ov.set("ContentType", "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")

    rels = ET.Element("Relationships", xmlns=R_NS)
    rel = ET.SubElement(rels, "Relationship")
    rel.set("Id", "rId1")
    rel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument")
    rel.set("Target", "word/document.xml")

    drels = ET.Element("Relationships", xmlns=R_NS)
    drel = ET.SubElement(drels, "Relationship")
    drel.set("Id", "rId1")
    drel.set("Type", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles")
    drel.set("Target", "styles.xml")

    styles = ET.Element(w("styles"))
    for sid, sname, isHeading in [("Heading1", "heading 1", True), ("ListBullet", "List Bullet", False)]:
        style = ET.SubElement(styles, w("style"))
        style.set(w("type"), "paragraph")
        style.set(w("styleId"), sid)
        sn = ET.SubElement(style, w("name"))
        sn.set(w("val"), sname)
        if isHeading:
            sr = ET.SubElement(style, w("rPr"))
            ET.SubElement(sr, w("b"))

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ET.tostring(ct, encoding="UTF-8", xml_declaration=True))
        z.writestr("_rels/.rels", ET.tostring(rels, encoding="UTF-8", xml_declaration=True))
        z.writestr("word/document.xml", doc_xml)
        z.writestr("word/_rels/document.xml.rels", ET.tostring(drels, encoding="UTF-8", xml_declaration=True))
        z.writestr("word/styles.xml", ET.tostring(styles, encoding="UTF-8", xml_declaration=True))
    return buf.getvalue()

def process_file(md_path):
    if not md_path.exists():
        print(f"  SKIP: {md_path} not found")
        return

    text = md_path.read_text(encoding="utf-8")
    resolved = replace_placeholders(text)

    base = md_path.stem.replace("SHOOT_", "")
    OUTPUT.mkdir(parents=True, exist_ok=True)

    txt_path = OUTPUT / f"{base}.txt"
    txt_path.write_text(resolved, encoding="utf-8")
    print(f"  ✓ TXT: {txt_path}")

    try:
        docx_body = md_to_docx_parts(resolved)
        docx_bytes = build_docx(docx_body)
        docx_path = OUTPUT / f"{base}.docx"
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        print(f"  ✓ DOCX: {docx_path}")
    except Exception as e:
        print(f"  ✗ DOCX failed: {e}")

    resume_match = re.search(r"## 3\. RESUME TEXT.*?\n(.*?)(?=\n## \d|\Z)", resolved, re.DOTALL)
    if resume_match:
        resume_only = resume_match.group(1).strip()
        resume_path = OUTPUT / f"{base}_resume.txt"
        resume_path.write_text(resume_only, encoding="utf-8")
        print(f"  ✓ {resume_path} (resume only)")

        try:
            resume_body = md_to_docx_parts(resume_only)
            resume_docx = build_docx(resume_body)
            resume_docx_path = OUTPUT / f"{base}_resume.docx"
            with open(resume_docx_path, "wb") as f:
                f.write(resume_docx)
            print(f"  ✓ DOCX: {resume_docx_path} (resume only)")
        except Exception as e:
            print(f"  ✗ Resume DOCX failed: {e}")

def main():
    load_config()
    OUTPUT.mkdir(parents=True, exist_ok=True)

    targets = []
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        targets = sorted(ROOT.rglob("*.md"))
        targets = [t for t in targets if ".git" not in str(t)
                   and t.name not in ("README.md", "AGENTS.md")]
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
        return

    print(f"Generating real-name documents ({len(targets)} file(s))...")
    print(f"  Name:  {REPLACE_MAP['[NAME]']}")
    print(f"  Email: {REPLACE_MAP['[EMAIL]']}")
    print(f"  Phone: {REPLACE_MAP['[PHONE]']}")
    for t in targets:
        process_file(t)
    print(f"\nDone. Files in: {OUTPUT}/")

if __name__ == "__main__":
    main()
