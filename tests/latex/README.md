# XeLaTeX and LuaLaTeX tests

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
sh tests/latex/run.sh
python3 tests/latex/verify.py
sh tests/latex/run.sh --engine lualatex
python3 tests/latex/verify.py --engine lualatex
```

The first run downloads the pinned Docker image and test fonts. Subsequent runs
reuse verified downloads. LuaLaTeX runs register these fonts in luaotfload's
database inside the disposable container. TeX compilation runs without network access. The manual
and graphics examples use restricted shell escape for minted and epstopdf;
other tests disable shell escape.
PDF inspection runs on the host.

To list or rerun individual tests:

```sh
python3 tests/latex/run.py --list
sh tests/latex/run.sh one-font math citations-biblatex
```

Run the full suite once before using the verifier, which checks all recorded
results. Output is saved in ignored `build/xelatex/` and `build/lualatex/` directories. Each rerun replaces
only the selected tests. Run one runner per engine at a time: each engine has its own results file.

## Coverage

- Mixed Bangla/English text, supported font families, styles, spacing, and font overrides.
- Assamese captions, dates, alphabetic labels, font coverage, and shared integrations.
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
| Extended labels | `alphalph`; both load orders, the 35-letter Bangla and 37-entry Assamese alphabets, multi-letter labels and links |
| Typography | `microtype`; supported Bangla fonts, both load orders and nonzero English protrusion matching fontspec |

These tests exercise the listed features, not every option of each package.
Cleveref names and connecting words use its own customization commands;
LaTeXbangla preserves Bengali label display while adapting numeric sorting.

Successful tests require all compilation passes, a PDF, and no missing glyphs
or final package/font/reference warnings. Expected-error tests must produce the
intended diagnostic. PDF checks inspect actual fonts, strokes, text, and links.
The English, Bangla and Assamese manual runs its code/output examples during
compilation; checks inspect their rendered counters, citations, boldness and
reference links. Assamese examples also compile as standalone documents.

## Test environment and fonts

[run.sh](run.sh) pins the TeX Live 2026 Docker image by digest. The baseline uses
XeTeX 0.999998, LaTeX 2026-06-01, Polyglossia 2.13, fontspec 2.9h, and
ucharclasses 2.6.0. Test logs record loaded package versions.
The LuaLaTeX baseline uses LuaHBTeX 1.24.0 with HarfBuzz shaping for Bangla.
Older distributions and hosted Overleaf builds are not covered.

| Fonts | Source |
| --- | --- |
| Kalpurush, FreeSerif | Pinned TeX Live image |
| Noto Serif Bengali, Noto Sans Bengali 2.001 | Ubuntu 22.04 `fonts-noto-core` archive |
| SolaimanLipi 1.6.1, Siyam Rupali 1.070 | [OmicronLab](https://www.omicronlab.com/bangla-fonts.html) |
| Anek Bangla variable font | [Google Fonts](https://github.com/google/fonts/tree/main/ofl/anekbangla), pinned revision |
| Tiro Bangla 1.52, regular and italic | [Google Fonts](https://github.com/google/fonts/tree/main/ofl/tirobangla), pinned revision |
| Galada 1.261 | [Google Fonts](https://github.com/google/fonts/tree/main/ofl/galada), pinned revision |

Hind Siliguri and Lohit Bengali come from pinned Google Fonts revisions;
Nikosh comes from the Bangladesh Navy's font download. Mukti 3.4.3 and the
static Baloo Da 2 1.640 faces come from their authors' releases.
Kohinoor Bangla tests run when a local copy is available. On macOS the fetcher
uses the installed collection; elsewhere, pass `--kohinoor-font /path/to/KohinoorBangla.ttc`
to `fetch-fonts.py`. The collection remains in the ignored font directory.

[fetch-fonts.py](fetch-fonts.py) verifies SHA-256 hashes. Downloaded fonts and the
license notices stay in the ignored `fonts/` directory; fonts are not
redistributed. `fonts.conf` and `OSFONTDIR` make them available to the test processes.
Anek is loaded by filename on both engines; its variable-weight example is
checked with LuaLaTeX. The default uses synthetic bold and italic.

Spacing tests measure native and selected space, stretch and shrink, plus actual
Bangla, English and mixed word pairs. Default Latin Modern is the spacing
reference; explicit `WordSpace` settings are checked separately.

For offline preparation, supply the Noto archive with
`python3 tests/latex/fetch-fonts.py --archive /path/to/fonts-noto-core.deb`
and place the other pinned fonts and license files in `tests/latex/fonts/`.
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

## Compare engines visually

After compiling both suites, run:

```sh
python3 tests/latex/compare-engines.py
```

Open `build/engine-comparison/index.html` for all supported fonts in regular, bold,
italic and bold italic at 8, 11 and 16 pt. The report includes full pages,
aligned text rows, color overlays and difference images. Rows are translated
to the same origin and baseline without scaling or shearing. Magenta marks
XeTeX-only ink, cyan marks LuaTeX-only ink, and black marks shared ink.

TeX measurements compare font size, slant and shaped width; PDF measurements
compare selected faces and synthetic stroke widths. Raster scores exclude blank
background. Inspect differences in context: antialiasing can change edge pixels
without changing the typography. Use `--dpi 300` for finer inspection. The report,
PNGs and machine-readable measurements remain in the ignored build directory.
