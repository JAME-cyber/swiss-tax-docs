"""Modèles et primitives de parsing : montants suisses, lignes, décision de taxation."""
from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict

# montant suisse: 1'234'567.89 | 95'000.00 | 95000 | 17'502 fr.95 (notation juridique VD)
MONTANT = (
    r"(?P<num>\d{1,3}(?:[' ]\d{3})*(?:\.\d{2})?|\d+(?:\.\d{2})?)"
    r"(?:\s*fr(?:\.(?P<cent>\d{2}))?)?"
)


def _montant(num: str, cent: str | None = None) -> float:
    """'1'234'567.89' | '95000.00' | ('17'502', '95') -> float."""
    base = float(num.replace("’", "'").replace("'", "").replace(" ", ""))
    if cent is not None and "." not in num:
        base += int(cent) / 100.0
    return base


@dataclass
class Ligne:
    label: str
    valeur: float


@dataclass
class DecisionTaxation:
    canton: str = "VD"
    periode_fiscale: int | None = None
    no_contribuable: str | None = None
    sections: dict = field(default_factory=dict)      # clé cible ou libellé -> Ligne
    validations: list = field(default_factory=list)   # [{check, ok, detail}]
    warnings: list = field(default_factory=list)

    def get(self, key: str) -> Ligne | None:
        return self.sections.get(key)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["sections"] = {k: asdict(v) if isinstance(v, Ligne) else v
                         for k, v in self.sections.items()}
        return d
