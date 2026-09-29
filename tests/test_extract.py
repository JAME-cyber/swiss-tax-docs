import pytest

from swiss_tax_docs.extract import texte_pdf

IMPORT_OK = True
try:
    import pdfplumber  # noqa: F401
except ImportError:
    IMPORT_OK = False


@pytest.mark.integration
@pytest.mark.skipif(not IMPORT_OK, reason="extra [pdf] non installé")
def test_texte_pdf_fichier_absent():
    with pytest.raises(FileNotFoundError):
        texte_pdf("/non/existent.pdf")
