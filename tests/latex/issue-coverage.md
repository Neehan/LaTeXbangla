# Historical issue coverage

Reviewed on 24 October 2026 against version 2.0. Stack Exchange's search API
returned 44 question/answer matches for `latexbangla`, covering 29 distinct
questions. The table includes questions where the package appears only in an
answer. It is an audit of those reports, not a claim about every possible document.

Tests use the pinned TeX Live environment in [README.md](README.md), on both
XeLaTeX and LuaLaTeX. They check rendered output and references as well as
compilation. Old examples may need migration: `feature=...` and bundled theorem
environments were removed, and `hyperref` must now be loaded explicitly.

| Report | Current behavior and test coverage |
| --- | --- |
| [Broken numerals / macro parameter error](https://tex.stackexchange.com/q/544315) | Current Polyglossia setup specifies native numerals. `book`, `structures`, `converters`, `numeric-zero-option` and `reported-headings-*` cover counters, contents, references and disabling conversion. |
| [Assamese subsection numbers](https://tex.stackexchange.com/q/545910), [section punctuation and hierarchy](https://tex.stackexchange.com/q/611354) | Class numbering is preserved; no forced heading format. `reported-headings-bangla` and `reported-headings-assamese` check nested numbers, resets and contents entries. |
| [Latin font ignored](https://tex.stackexchange.com/q/386111) | `one-font`, `font-overrides`, `english-first-families` and `switching-contexts` check fontspec main/sans/mono choices and styles. `local-fonts-*` additionally checks local Latin families and restoration. |
| [Overleaf fonts and styles](https://tex.stackexchange.com/q/575777) | `one-font`, `font-file`, `font-siyam-file` and font-face tests cover a single font, filename loading and synthetic styles. This does not certify a hosted Overleaf installation or install missing fonts there. |
| [Sans-serif text in the Legrand template](https://tex.stackexchange.com/q/547889) | Sans fallback and explicit sans selection are tested. Templates loading Babel must still be adapted to use Polyglossia; the whole external template is not certified. |
| [Book headers and footers](https://tex.stackexchange.com/q/551240) | `common-layout` checks `fancyhdr`, styled headers, page numbers and captions. The original example also mixed language packages and contained unrelated template errors. |
| [Bengali enumeration](https://tex.stackexchange.com/q/548546) | `structures`, `common-boxes` and `reported-enumerate` check nested native labels. Use `enumerate` placeholders `(1।)` and `(a)`, or enumitem formatters; literal `(১।)` and `(ক)` are not counter placeholders. |
| [English alphabetic bibliography](https://tex.stackexchange.com/q/578976) | `reported-biblatex-english` runs Biber with `style=alphabetic,language=english,autolang=other`. Explicit English language switching requires `\setotherlanguage{english}`. Alphabetic labels and English entries are preserved; the document's bibliography heading remains localized. Numeric and author–year styles have separate tests. |
| [Quotation environments](https://tex.stackexchange.com/q/599656) | `reported-quotation` checks nested mixed-script quotes, attribution and restoration of italic. The old overlapping-language-environment error is absent. `local-fonts-*` checks custom quotation fonts, including inside explicit English passages. |
| [Quotation-mark mapping](https://tex.stackexchange.com/q/599335) | `switching-contexts` compares TeX ligature widths with the selected Latin font; `reported-quotation` checks curly quotes and csquotes nesting. Reinterpreting straight quotes and backticks as identical input is an author-defined mapping, not automatic behavior. |
| [Starred headings and nameref](https://tex.stackexchange.com/q/603292), related [report](https://tex.stackexchange.com/q/569570) and [discussion](https://tex.stackexchange.com/q/397031) | `reported-nameref-plain` passes without titlesec. With titlesec, the starred-section name is still empty, also in a plain fontspec baseline. `reported-nameref-titlesec` verifies an explicit name/anchor workaround, not a package fix. |
| [Per-chapter caption names](https://tex.stackexchange.com/q/668984) | `reported-language-captions` checks an English `Fig.` customization through repeated language switches, restoring the native caption afterward. Font switching alone does not change the document language. |
| [Missing contents levels](https://tex.stackexchange.com/q/548510), [another contents report](https://tex.stackexchange.com/q/728290) | `reported-headings-*` checks `tocdepth`, `secnumdepth` and tocloft, including the actual contents page. External included files in the second report cannot be assessed from its incomplete example. |
| [Ornaments and engine support](https://tex.stackexchange.com/q/418679) | LuaLaTeX is now supported. `reported-ornaments` checks pgfornament with multiline bilingual TikZ nodes on both engines. The separate `tikzrput` path has not been tested. |
| [Basic Bengali setup](https://tex.stackexchange.com/q/99606), [script and font setup](https://tex.stackexchange.com/q/103274), [verbatim text](https://tex.stackexchange.com/q/106466) | `one-font`, font-face cases, `math` and `verbatim` cover the relevant package features. Choosing a mono text family does not make a proportional Bangla font fixed-width. |
| [Wrong compiler](https://tex.stackexchange.com/q/552698) | `wrong-engine` verifies the pdfLaTeX rejection; use XeLaTeX or LuaLaTeX. |
| [MiKTeX font lookup](https://tex.stackexchange.com/q/705412) | LaTeXbangla is commented out in the posted example. Its missing-font/install problem is not a package regression; Windows/MiKTeX is not part of this test environment. |
| [EPUB conversion](https://tex.stackexchange.com/q/648387) | TeX4ht/tex4ebook output is not tested. PDF success does not establish EPUB compatibility or resolve the reported auxiliary-file issue. |
| [Exam-paper layout](https://tex.stackexchange.com/q/603227), [collecting article metadata](https://tex.stackexchange.com/q/598449), [colored contents parts](https://tex.stackexchange.com/q/548515), [relative ornament placement](https://tex.stackexchange.com/q/419060), [line breaks in rput](https://tex.stackexchange.com/q/418680) | These request document design or corrections to author code, rather than a reproducible LaTeXbangla defect. Lists, tables and ordinary graphics are covered; the specific exam class, article-collection template and rput layouts are not. |

## Local font selection

This selects Adventor italic for `QuotationTypeface` on both engines:

```latex
\documentclass{article}
\usepackage{latexbangla}
\setmainfont{TeX Gyre Pagella}
\setbanglamainfont{Kalpurush}
\setotherlanguage{english}
\newfontfamily\quotefont{TeX Gyre Adventor}
\begin{document}
\textit{\textenglish{\quotefont QuotationTypeface}}
\end{document}
```

The `local-fonts-bangla` and `local-fonts-assamese` tests check actual PDF
faces, sizing and letter spacing. They cover declarations before and after
package loading, nested selections, main/sans/mono resets, inline fontspec,
both spellings of addfontfeatures, preamble boxes, footnotes, tables and math
text. Native-script text retains its configured font throughout.

## Starred sections with titlesec

The failure reproduces with `fontspec`, `titlesec` and `hyperref` alone. When
using titlesec, the tested workaround is to supply the name and link anchor:

```latex
\section*{Unnumbered Section}\phantomsection
\makeatletter
\def\@currentlabelname{Unnumbered Section}
\makeatother
\label{sec:unnumbered}
```

LaTeXbangla itself no longer loads titlesec or changes section layouts.
