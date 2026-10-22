# XeLaTeX tests

Compile test documents and check their PDFs for correct fonts, numbering,
references, links, and expected errors. Package usage is in the
[main README](../../README.md) and [manual](../../latexbangla/latexbangla.pdf).

## Run

Requirements: Python 3.10+, Docker, and `ar` (binutils on Linux or developer
tools on macOS). From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r tests/requirements.txt
sh tests/xelatex/run.sh
python3 tests/xelatex/verify.py
```

The first run downloads the pinned Docker image and test fonts. Subsequent runs
reuse verified downloads. TeX compilation runs without network access. The manual
uses restricted shell escape for minted; other tests disable shell escape.
PDF inspection runs on the host.

To list or rerun individual tests:

```sh
python3 tests/xelatex/run.py --list
sh tests/xelatex/run.sh one-font math citations-biblatex
```

Run the full suite once before using the verifier, which checks all recorded
results. Output is saved in the ignored `build/` directory. Each rerun replaces
only the selected tests. Run one runner at a time: results share a JSON file.

## Coverage

- Mixed Bangla/English text, six font families, styles, spacing, and font overrides.
- Decimal and alphabetic counters, nested lists, footnotes, and appendices.
- Bangla math text and digits, conventional math fonts, and unicode-math.
- Article, report, book, memoir, AMS environments, tables, references, and citations.
- Legacy options, invalid configurations, the manual, and public examples.

Common-package tests cover these combinations:

| Area | Packages and behavior |
| --- | --- |
| Mathematics | `amsmath`, `mathtools`, `amssymb`, `bm`, `cancel`, `amsthm`; Bangla text, digits and references |
| Tables | `array`, `booktabs`, `tabularx`, `longtable`, `multirow`, `siunitx`; mixed-script cells and captions |
| Layout | `geometry`, `graphicx`, `xcolor`, `float`, `caption`, `subcaption`, `fancyhdr`, `titlesec` |
| References | `hyperref`, `cleveref`; sorting, ranges, page references, footnotes and appendices |
| Citations | Standard LaTeX, `natbib`, `biblatex`; numeric and author–year styles |
| Lists and boxes | `enumitem`, `tcolorbox`; custom labels and numbered theorem boxes |
| Extended labels | `alphalph`; both load orders, the 36-letter Bangla alphabet, multi-letter labels and links |
| Typography | `microtype`; six Bangla fonts, both load orders and nonzero English protrusion matching fontspec |

These tests exercise the listed features, not every option of each package.
Cleveref names and connecting words use its own customization commands;
LaTeXbangla preserves Bengali label display while adapting numeric sorting.

Successful tests require all compilation passes, a PDF, and no missing glyphs
or final package/font/reference warnings. Expected-error tests must produce the
intended diagnostic. PDF checks inspect actual fonts, strokes, text, and links.
The bilingual manual runs its code/output examples during compilation; checks
also inspect their rendered counters, citations, boldness, and reference links.

## Test environment and fonts

[run.sh](run.sh) pins the TeX Live 2026 Docker image by digest. The baseline uses
XeTeX 0.999998, LaTeX 2026-06-01, Polyglossia 2.13, fontspec 2.9h, and
ucharclasses 2.6.0. Test logs record loaded package versions.
Older distributions, LuaLaTeX, and hosted Overleaf builds are not covered.

| Fonts | Source |
| --- | --- |
| Kalpurush, FreeSerif | Pinned TeX Live image |
| Noto Serif Bengali, Noto Sans Bengali 2.001 | Ubuntu 22.04 `fonts-noto-core` archive |
| SolaimanLipi 1.6.1, Siyam Rupali 1.070 | [OmicronLab](https://www.omicronlab.com/bangla-fonts.html) |

[fetch-fonts.py](fetch-fonts.py) verifies SHA-256 hashes. Downloaded fonts and the
Noto license notice stay in the ignored `fonts/` directory; fonts are not
redistributed. `fonts.conf` makes them available only to the test processes.

For offline preparation, supply the Noto archive with
`python3 tests/xelatex/fetch-fonts.py --archive /path/to/fonts-noto-core.deb`
and place the pinned SolaimanLipi and Siyam Rupali files in `tests/xelatex/fonts/`.
The Docker image must already be available locally to run tests offline.

## Add or change tests

Define cases in [cases.py](cases.py), shared TeX bodies in [fixtures/](fixtures/),
and PDF assertions in [verify.py](verify.py). Test the visible behavior that
matters to an author, including regressions when fixing bugs.

For font changes, inspect the rendered `font-faces-*` samples at 8, 11, and 16 pt,
and the [font guide](../../examples/supported-fonts.pdf). Check conjuncts,
spacing, bold contrast, and slant; successful compilation alone is insufficient.
Synthetic-bold checks inspect PDF strokes because the face name can stay the same.
Explicit user settings must continue to override package defaults.
