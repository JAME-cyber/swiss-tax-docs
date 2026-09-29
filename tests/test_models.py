from swiss_tax_docs.models import Ligne, DecisionTaxation, _montant


def test_montant_notation_juridique_fr():
    assert _montant("17'502", "95") == 17502.95


def test_montant_notation_fr_apostrophe_typographique():
    assert _montant("17’502", "95") == 17502.95


def test_montant_classique():
    assert _montant("95'000.00") == 95000.0


def test_montant_sans_separateur():
    assert _montant("95000") == 95000.0


def test_ligne():
    l = Ligne(label="revenu imposable", valeur=95000.0)
    assert l.valeur == 95000.0


def test_decision_get_et_dict():
    d = DecisionTaxation(periode_fiscale=2024)
    d.sections["revenu_imposable"] = Ligne("revenu imposable", 95000.0)
    assert d.get("revenu_imposable").valeur == 95000.0
    assert d.get("absent") is None
    j = d.to_dict()
    assert j["periode_fiscale"] == 2024
    assert j["sections"]["revenu_imposable"]["valeur"] == 95000.0
