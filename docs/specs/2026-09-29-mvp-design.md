# swiss-tax-docs MVP — Design
**Date:** 29/09/2026 · **Statut:** Approuvé (GO Tars) · **Réf étude:** ~/projects/ch-doc-classifier/ETUDE-OPEN-SOURCE.md

## Problème
Les fiduciaires romandes saisissent à la main les décisions de taxation cantonales (revenu, fortune,
impôts, acomptes, solde). Aucun OSS ne les parse (26 formats cantonaux = barrière de maintenance).
Les extracteurs LLM génériques hallucinent des totaux plausibles — inacceptables en comptabilité.

## Solution
Librairie Python déterministe : extraction PDF → parsing par canton → **validators arithmétiques
qui refusent un document incohérent**. "Un LLM peut halluciner un total qui tombe juste ;
le validator déterministe ne le peut pas." Open core MIT dès le départ (leçon Redis/Elastic :
jamais de full-open puis relicensier).

## Architecture (v0.1 — périmètre VD personnes physiques)

```
PDF ──► extract.texte_pdf() ──► parsers.vd.parse_vd() ──► DecisionTaxation + validations
      (natif pdfplumber            (détection, lignes         │
       | scan tesseract fra)        montants, mapping)         └─► validators.validate() → warnings
```

- **models.py** — `Ligne`, `DecisionTaxation`, regex montants suisses (1'234.56 · 17'502 fr.95)
- **extract.py** — natif (pdfplumber) / scan (pypdfium2 300dpi → tesseract fra)
- **parsers/vd.py** — détection (≥2 marqueurs), extraction lignes, mapping clés cibles, métadonnées
- **validators.py** — équilibres (revenu, fortune), plafonds légaux VD (ICC ≤ 30% revenu, fortune ≤ 10‰),
  cohérence solde (ICC + fortune + IFD − acomptes)
- **cli.py** — `swiss-tax-docs parse document.pdf [--canton vd] [--json]`
- Backends LLM/Typesafe : HORS périmètre v0.1 (YAGNI — l'adapter Typesafe reste privé)

## Maquette sortie CLI

```
$ swiss-tax-docs parse decision.pdf
✓ Document reconnu : décision de taxation VD (période 2024)
✓ 9 champs extraits · 5/5 validators OK

  revenu_imposable     95'000.00
  fortune_nette       210'000.00
  icc_revenu          16'399.08
  impot_fortune          410.60
  ifd                   4'050.00
  acomptes             14'000.00
  solde                 6'859.68

$ swiss-tax-docs parse decision_falsifiee.pdf   # solde +100.-
✗ VALIDATION: solde: 16'399.08 + 410.60 + 4'050.00 - 14'000.00 = 6'859.68 ≠ 6'959.68 (lu)
  → document à revoir avant toute utilisation comptable
```

## Décisions clés
| Décision | Raison |
|---|---|
| Zéro dépendance runtime obligatoire* | Le parsing marche sur .txt ; pdfplumber optionnel (extra `[pdf]`) |
| Fixtures synthétiques + 1 jurisprudence publique | NLPD : jamais de vraie décision dans le repo |
| src layout + pyproject + console script | Installable `pip install swiss-tax-docs` |
| MIT | Max adoption ; notre avantage reste l'adapter privé + futur service |

*extract.py importe pdfplumber/pypdfium2 en lazy (ImportError → message clair).

## Tests (TDD)
1. Détection VD : 2 fixtures OK, doc étranger rejeté
2. Extraction : tous champs clés présents, notation fr.95, lignes avec `:`
3. Validators : 9/9 verts sur fixtures ; falsification solde → warning (2 fixtures)
4. Prose rejetée (pas de faux positifs)
5. Extract : marqué intégration (skip sans pdf réel)

## Hors périmètre v0.1
Autres cantons · impôt à la source · personnes morales · OCR multi-langues · API web · LLM backend.
