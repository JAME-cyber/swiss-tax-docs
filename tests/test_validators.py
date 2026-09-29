from pathlib import Path

from swiss_tax_docs.models import DecisionTaxation, Ligne
from swiss_tax_docs.parsers.vd import parse_vd
from swiss_tax_docs.validators import validate

FIX = Path(__file__).parent.parent / "fixtures"


def _falsifie(original: str, ancien: str, nouveau: str) -> str:
    assert ancien in original
    return original.replace(ancien, nouveau)


def test_fixtures_propres_zero_warning():
    for f in ("decision_vd_2024_synthetique.txt", "decision_vd_2020_jurisprudence.txt"):
        d = validate(parse_vd((FIX / f).read_text()))
        assert d.warnings == [], f"{f}: {d.warnings}"
        assert all(v["ok"] for v in d.validations), f"{f}: checks en échec"


def test_falsification_solde_detectee_synthetique():
    t = _falsifie((FIX / "decision_vd_2024_synthetique.txt").read_text(),
                  "6'859.68", "6'959.68")
    d = validate(parse_vd(t))
    assert d.warnings, "falsification non détectée"
    assert any("solde" in w for w in d.warnings)


def test_falsification_solde_detectee_jurisprudence():
    t = _falsifie((FIX / "decision_vd_2020_jurisprudence.txt").read_text(),
                  "19'789.60", "19'839.60")
    d = validate(parse_vd(t))
    assert d.warnings and any("solde" in w for w in d.warnings)


def test_falsification_fortune_detectee():
    t = _falsifie((FIX / "decision_vd_2024_synthetique.txt").read_text(),
                  "Fortune nette imposable ..................................     210'000.00",
                  "Fortune nette imposable ..................................     215'000.00")
    d = validate(parse_vd(t))
    assert any("fortune" in w for w in d.warnings)


def test_plafond_icc_detecte():
    d = DecisionTaxation()
    d.sections["icc_revenu"] = Ligne("icc", 40_000.0)
    d.sections["revenu_imposable"] = Ligne("ri", 100_000.0)
    validate(d)
    assert any("plafond ICC" in w for w in d.warnings)


def test_validate_sur_objet_partiel_ne_leve_pas():
    d = DecisionTaxation()  # aucune section
    validate(d)
    assert d.validations == []
