"""Validators arithmétiques déterministes.

Philosophie: un LLM peut halluciner un total qui tombe juste ; ces checks non.
Tolérance: 0.01 CHF (arrondi suisse 5 centimes).
"""
from __future__ import annotations

from .models import DecisionTaxation

TOL = 0.011


def validate(d: DecisionTaxation) -> DecisionTaxation:
    """Ajoute les checks à d.validations (et d.warnings si échec). Ne lève jamais."""

    def check(nom: str, ok: bool, detail: str = "") -> None:
        d.validations.append({"check": nom, "ok": ok, "detail": detail})
        if not ok:
            d.warnings.append(f"{nom}: {detail}")

    rb, ded, ri = d.get("revenu_brut"), d.get("deductions"), d.get("revenu_imposable")
    if rb and ded and ri:
        check("revenu: brut - déductions = imposable",
              abs(rb.valeur - ded.valeur - ri.valeur) < TOL,
              f"{rb.valeur} - {ded.valeur} != {ri.valeur}")

    ac, det, fn = d.get("actif_imposable"), d.get("dettes"), d.get("fortune_nette")
    if ac and det and fn:
        check("fortune: actif - dettes = nette",
              abs(ac.valeur - det.valeur - fn.valeur) < TOL,
              f"{ac.valeur} - {det.valeur} != {fn.valeur}")

    # plafonds légaux VD (art. 39 LI / 50 LI): ICC <= 30% du revenu imposable; fortune <= 10‰
    icc, ri2 = d.get("icc_revenu"), d.get("revenu_imposable")
    if icc and ri2:
        check("plafond ICC <= 30% du revenu imposable",
              icc.valeur <= 0.30 * ri2.valeur,
              f"{icc.valeur} > 30% de {ri2.valeur}")

    imp_f, fn2 = d.get("impot_fortune"), d.get("fortune_nette")
    if imp_f and fn2:
        check("plafond fortune <= 10‰ de la fortune nette",
              imp_f.valeur <= 0.010 * fn2.valeur,
              f"{imp_f.valeur} > 10‰ de {fn2.valeur}")

    icc2, acm, solde = d.get("icc_revenu"), d.get("acomptes"), d.get("solde")
    if icc2 and acm and solde:
        # l'impôt sur la fortune est soit une ligne séparée, soit inclus dans l'ICC agrégé
        ifd_v = d.get("ifd").valeur if d.get("ifd") else 0.0
        impf_v = imp_f.valeur if imp_f else 0.0
        attendu = icc2.valeur + impf_v + ifd_v - acm.valeur
        check("solde: ICC + fortune + IFD - acomptes = solde",
              abs(attendu - solde.valeur) < TOL,
              f"{icc2.valeur} + {impf_v} + {ifd_v} - {acm.valeur} = {attendu:.2f} != {solde.valeur}")
    return d
