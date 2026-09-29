"""Parser décision de taxation Vaud (personnes physiques) — déterministe, zéro LLM."""
from __future__ import annotations

import re

from ..models import DecisionTaxation, Ligne, MONTANT, _montant

DOC_MARKERS = [r"DÉCISION DE TAXATION", r"CANTON DE VAUD", r"IMPÔT FÉDÉRAL DIRECT"]

# ligne "Label ..... montant" ou "Label: montant" (points de conduite facultatifs)
LIGNE_MONTANT = re.compile(
    rf"^\s*(?P<label>[A-ZÀ-Ÿa-zà-ÿ0-9°%'()\/\-: ]+?)\s*\.*\s*{MONTANT}\.?\s*$"
)

# clés cibles -> libellés acceptés (vocabulaire officiel VD, variantes tolérées)
CIBLES = {
    "revenu_brut": ("revenu brut", "total des revenus", "revenu brut total"),
    "deductions": ("déductions", "total des déductions"),
    "revenu_imposable": ("revenu imposable", "revenu net imposable"),
    "actif_imposable": ("actif imposable", "actif brut", "total de l'actif"),
    "dettes": ("dettes", "total des dettes"),
    "fortune_nette": ("fortune nette imposable", "fortune nette", "fortune imposable"),
    "icc_revenu": (
        "total impôt sur le revenu (cantonal et communal)",
        "impôt cantonal et communal sur le revenu",
        "impôt cantonal et communal",
    ),
    "impot_fortune": ("impôt sur la fortune", "impôt cantonal et communal sur la fortune"),
    "acomptes": ("acomptes versés", "acomptes facturés"),
    "solde": ("solde dû", "solde à payer"),
    "ifd": ("impôt fédéral direct",),
}


def detect(text: str) -> bool:
    """≥2 marqueurs du document officiel VD."""
    t = text.upper()
    return sum(1 for m in DOC_MARKERS if re.search(m, t)) >= 2


def _parse_lignes(text: str) -> dict[str, Ligne]:
    out: dict[str, Ligne] = {}
    for raw in text.splitlines():
        m = LIGNE_MONTANT.match(raw)
        if not m:
            continue
        label = re.sub(r"\s+", " ", m.group("label").strip(" .:").lower())
        try:
            val = _montant(m.group("num"), m.group("cent"))
        except ValueError:
            continue
        out.setdefault(label, Ligne(label=label, valeur=val))
    return out


def parse_vd(text: str, gate: float = 0.0) -> DecisionTaxation:
    """Parse une décision de taxation VD. ValueError si le document n'est pas reconnu."""
    if not detect(text):
        raise ValueError("Document non reconnu comme décision de taxation VD")
    d = DecisionTaxation()
    lignes = _parse_lignes(text)

    m = re.search(r"P[ée]riode fiscale\s*:\s*(\d{4})", text)
    if m:
        d.periode_fiscale = int(m.group(1))
    m = re.search(r"[Nn]°\s*de contribuable\s*:\s*([\d\-]+)", text)
    if m:
        d.no_contribuable = m.group(1)

    # mapping clés cibles (le premier libellé trouvé gagne ; ordre du dict = priorité)
    for key, candidats in CIBLES.items():
        for c in candidats:
            if c in lignes:
                d.sections[key] = lignes[c]
                break

    d.sections.update(lignes)  # conserve aussi les libellés bruts (debug/transparence)
    return d
