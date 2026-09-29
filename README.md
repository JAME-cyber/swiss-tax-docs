# swiss-tax-docs 🇨🇭

**Parsing déterministe des décisions de taxation suisses, avec validators arithmétiques.**

> Un LLM peut halluciner un total qui tombe juste. Un validator déterministe ne le peut pas.

Les fiduciaires romandes saisissent à la main les décisions de taxation — revenu imposable,
fortune, impôts cantonal/communal/fédéral, acomptes, solde. Les extracteurs LLM génériques
produisent des totaux *plausibles mais faux*, inacceptables en comptabilité.
`swiss-tax-docs` extrait les champs par règles et **refuse un document incohérent**.

## État — v0.1.0 (alpha)

- ✅ Canton de **Vaud** (VD), personnes physiques, décision de taxation (ICC + IFD)
- ✅ Entrées : `.txt` ou `.pdf` (natif via pdfplumber, ou scan via tesseract fra)
- ✅ Validators : équilibres revenu/fortune, plafonds légaux VD (ICC ≤ 30 % du revenu,
  fortune ≤ 10 ‰), cohérence du solde (ICC + fortune + IFD − acomptes)
- ✅ Notations gérées : `1'234'567.89`, `95'000`, `17'502 fr.95` (style juridique)
- ❌ Pas encore : autres cantons (26 formats), personnes morales, impôt à la source, API

## Installation

```bash
pip install swiss-tax-docs        # parsing .txt
pip install "swiss-tax-docs[pdf]" # + PDF natif/scans (tesseract-ocr-fra requis pour les scans)
```

## Usage

```bash
$ swiss-tax-docs parse decision.pdf
✓ Document reconnu : décision de taxation VD (période 2024)
✓ 14 champs extraits · 5/5 validators OK

  revenu_imposable          95'000.00
  fortune_nette            210'000.00
  icc_revenu                16'399.08
  ...
  solde                      6'859.68

$ swiss-tax-docs parse decision.pdf --json   # sortie machine
```

```python
from swiss_tax_docs.parsers.vd import parse_vd
from swiss_tax_docs.validators import validate

d = validate(parse_vd(open("decision.txt").read()))
if d.warnings:
    print("Document incohérent, relecture humaine requise:", d.warnings)
print(d.get("solde").valeur)
```

Un document falsifié ou mal OCRisé est **signalé, jamais silencieusement accepté** :

```
⚠ solde: ICC + fortune + IFD - acomptes = solde: 16'399.08 + 410.60 + 4'050.00 - 14'000.00 = 6'859.68 ≠ 6'959.68
  → document à revoir avant toute utilisation comptable
```

## Ajouter un canton

Un canton = un fichier dans `src/swiss_tax_docs/parsers/` (détection, libellés, règles) + des
fixtures. Les validators arithmétiques génériques (équilibres, plafonds) se réutilisent tels quels.
PRs bienvenues — particulièrement pour GE, FR, VS, TI.

## Tests & fiabilité

```bash
pip install -e ".[pdf]" && pytest   # 24 tests
```

La suite inclut des **tests anti-hallucination** : on falsifie un solde de +100 CHF dans les
fixtures et on exige que le parser le signale. Les fixtures sont **100 % synthétiques ou issues
de jurisprudence publique** — jamais de vraie décision de contribuable (nLPD).

## Licence

MIT. Ce projet n'est pas affilié aux administrations fiscales cantonales ni à la Confédération.
