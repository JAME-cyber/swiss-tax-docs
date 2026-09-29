"""CLI swiss-tax-docs: parse un document (.txt ou .pdf) et affiche le résultat + validations."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .parsers.vd import parse_vd
from .validators import validate


def _lire_texte(chemin: Path) -> str:
    if chemin.suffix.lower() == ".pdf":
        from .extract import texte_pdf
        texte, methode = texte_pdf(chemin)
        print(f"# extraction: {methode}", file=sys.stderr)
        return texte
    return chemin.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="swiss-tax-docs",
        description="Parsing déterministe des décisions de taxation suisses avec validators arithmétiques.",
    )
    p.add_argument("commande", nargs="?", default="parse", choices=["parse"],
                   help="action (parse par défaut, peut être omis)")
    p.add_argument("fichier", help="document .txt ou .pdf (décision de taxation)")
    p.add_argument("--canton", default="vd", choices=["vd"], help="canton du document (vd pour l'instant)")
    p.add_argument("--json", action="store_true", help="sortie JSON machine")
    args = p.parse_args(argv)

    chemin = Path(args.fichier)
    if not chemin.exists():
        print(f"Erreur: fichier introuvable: {chemin}", file=sys.stderr)
        return 2

    try:
        texte = _lire_texte(chemin)
        d = validate(parse_vd(texte))
    except (ValueError, ImportError) as e:
        print(f"Erreur: {e}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(d.to_dict(), indent=2, ensure_ascii=False))
    else:
        p_fiscale = d.periode_fiscale or "?"
        n_ok = sum(1 for v in d.validations if v["ok"])
        print(f"✓ Document reconnu : décision de taxation {d.canton} (période {p_fiscale})")
        print(f"{'✓' if not d.warnings else '✗'} {len(d.sections) // 2} champs extraits · {n_ok}/{len(d.validations)} validators OK")
        print()
        for k in ("revenu_imposable", "fortune_nette", "icc_revenu", "impot_fortune", "ifd", "acomptes", "solde"):
            l = d.get(k)
            if l:
                print(f"  {k:<20} {l.valeur:>14,.2f}".replace(",", "'"))
        for w in d.warnings:
            print(f"\n  ⚠ {w}")
        if d.warnings:
            print("\n  → document à revoir avant toute utilisation comptable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
