#!/usr/bin/env python3
"""Export a manuscript (.docx or .pdf) to UTF-8 text and print its SHA-256 for sources.local.json.

Usage: python export_text.py SOURCE OUT.txt
DOCX is read with the standard library (one line per w:p paragraph). PDF needs `pdftotext` on PATH.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paragraphs = []
    for p in root.iter(W + "p"):
        parts = []
        for node in p.iter():
            if node.tag == W + "t" and node.text:
                parts.append(node.text)
            elif node.tag == W + "tab":
                parts.append("\t")
            elif node.tag in (W + "br", W + "cr"):
                parts.append("\n")
        paragraphs.append("".join(parts))
    return "\n".join(paragraphs).strip() + "\n"


def pdf_text(path: Path) -> str:
    out = subprocess.run(["pdftotext", "-enc", "UTF-8", str(path), "-"], capture_output=True, check=True)
    return out.stdout.decode("utf-8").replace("\r\n", "\n").replace("\f", "\n").strip() + "\n"


def main() -> int:
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    text = docx_text(src) if src.suffix.lower() == ".docx" else pdf_text(src)
    data = text.encode("utf-8")
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    print(f"{hashlib.sha256(data).hexdigest()}  {dst.name}  ({len(text)} chars; source sha256 "
          f"{hashlib.sha256(src.read_bytes()).hexdigest()})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
