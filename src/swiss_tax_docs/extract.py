"""Extraction texte depuis PDF: natif (pdfplumber) ou scan (pypdfium2 + tesseract fra).

Dépendances optionnelles: pip install swiss-tax-docs[pdf]  (+ tesseract-ocr-fra pour les scans).
"""
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

MIN_CHARS_PAR_PAGE = 60  # sous ce seuil -> considéré comme scan


def texte_pdf(pdf: str | Path) -> tuple[str, str]:
    """Retourne (texte, méthode) avec méthode dans {'natif', 'ocr'}."""
    pdf = Path(pdf)
    try:
        import pdfplumber
    except ImportError as e:
        raise ImportError("PDF natif: installez l'extra — pip install swiss-tax-docs[pdf]") from e

    with pdfplumber.open(pdf) as doc:
        pages = [p.extract_text() or "" for p in doc.pages]
    if sum(len(t) for t in pages) >= MIN_CHARS_PAR_PAGE * max(1, len(pages)):
        return "\n".join(pages), "natif"
    return _ocr(pdf), "ocr"


def _ocr(pdf: Path) -> str:
    try:
        import pypdfium2 as pdfium
    except ImportError as e:
        raise ImportError("PDF scanné: pip install swiss-tax-docs[pdf] + tesseract-ocr-fra") from e
    doc = pdfium.PdfDocument(str(pdf))
    out = []
    for page in doc:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            tmp = Path(f.name)
        page.render(scale=300 / 72).to_pil().save(tmp)
        r = subprocess.run(
            ["tesseract", str(tmp), "stdout", "-l", "fra", "--psm", "6"],
            capture_output=True, text=True,
        )
        out.append(r.stdout)
        tmp.unlink(missing_ok=True)
    return "\n".join(out)
