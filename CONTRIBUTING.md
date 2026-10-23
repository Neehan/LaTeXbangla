# Contributing

Report bugs through [GitHub Issues](https://github.com/Neehan/LaTeXbangla/issues)
or [the discussion group](https://groups.google.com/g/latexbangla). Include a
small complete document, expected and actual output, font names, and the compiler
log. Add `\listfiles` to record package versions.

Keep changes focused, use readable names and comments, and share code between
engines where possible. Add a regression test for behavior fixes and run the
suite with both engines; see the [test guide](tests/latex/README.md).
For font changes, inspect the rendered styles and engine comparison images too.

Keep the Bangla and Assamese manuals in sync with the English source. Rebuild
affected PDFs and the README preview when their source or output changes.
Before release, update the version and changelog and run the full suite.
The `latexbangla/` directory contains the
complete CTAN upload; tests and repository documentation stay outside it.
