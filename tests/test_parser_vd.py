import json
from pathlib import Path

import pytest

from swiss_tax_docs.parsers.vd import detect, parse_vd

FIX = Path(__file__).parent.parent / "fixtures"


@pytest.fixture
def synthetique():
    return (FIX / "decision_vd_2024_synthetique.txt").read_text()


@pytest.fixture
def jurisprudence():
    return (FIX / "decision_vd_2020_jurisprudence.txt").read_text()


def test_detect_vd(synthetique, jurisprudence):
    assert detect(synthetique)
    assert detect(jurisprudence)


def test_detect_rejette_document_etranger():
    lettre = "Madame, Monsieur, veuillez trouver ci-joint votre relevé de compte de 1'234.50 CHF."
    assert not detect(lettre)


def test_parse_synthetique_champs(synthetique):
    d = parse_vd(synthetique)
    for k in ("revenu_brut", "deductions", "revenu_imposable", "actif_imposable",
              "dettes", "fortune_nette", "icc_revenu", "impot_fortune", "acomptes", "solde", "ifd"):
        assert k in d.sections, f"champ manquant: {k}"
    assert d.periode_fiscale == 2024
    assert d.sections["revenu_imposable"].valeur == 95000.0
    assert d.sections["solde"].valeur == 6859.68


def test_parse_jurisprudence_notation_fr(jurisprudence):
    d = parse_vd(jurisprudence)
    assert d.sections["icc_revenu"].valeur == 17502.95
    assert d.sections["ifd"].valeur == 2286.65
    assert d.sections["solde"].valeur == 19789.60


def test_to_dict_serialisable(synthetique):
    d = parse_vd(synthetique)
    j = json.dumps(d.to_dict(), ensure_ascii=False)  # ne doit pas lever
    assert "revenu_imposable" in j


def test_parse_rejette_non_reconnu():
    with pytest.raises(ValueError):
        parse_vd("Cher client, votre facture de 120.00 est en pièce jointe.")
