# Contributing

For bugs, include a small complete document, its expected and actual output,
font names, and the XeLaTeX log. Add `\listfiles` to the document to record
package versions. Remove personal information before sharing a log.
Use [GitHub Issues](https://github.com/Neehan/LaTeXbangla/issues) or
[the discussion group](https://groups.google.com/g/latexbangla).

## Tests

See [the test guide](tests/xelatex/README.md) for setup, commands, font assets,
and coverage.

Keep changes focused and add a regression specimen when fixing a behavior bug.
Tests must inspect the relevant output, not just the compiler's exit status.
Preserve the division between language support and document layout. Prefer public
upstream APIs; explain any unavoidable dependency on package internals beside it.

For font fallback changes, render and visually inspect the `font-faces-*`
specimens before choosing bold or slant strengths. Compare regular, bold,
italic and bold italic at all three sizes, including conjuncts and punctuation.
Check the corrected output again after making adjustments. Compilation and font
metadata do not replace this review. Document changed defaults in the manual.

## Manual and example PDFs

After editing their sources, compile and copy the generated PDFs:

```sh
sh tests/xelatex/run.sh manual example supported-fonts
cp tests/xelatex/build/manual/main.pdf latexbangla/latexbangla.pdf
cp tests/xelatex/build/example/main.pdf examples/example.pdf
cp tests/xelatex/build/supported-fonts/main.pdf examples/supported-fonts.pdf
```

Inspect the PDFs and check the logs for missing glyphs and overfull boxes.
All three PDFs are versioned; intermediate LaTeX files are ignored.
The manual uses minted for syntax highlighting, with TeX Live's restricted shell
escape enabled by the test runner. Keep both language versions in sync.

After changing the README example or its font defaults, refresh its screenshot:

```sh
sh tests/xelatex/run.sh readme-example
python3 tests/xelatex/verify.py
cp tests/xelatex/build/readme-example/preview.png img/example.png
```

The verifier renders the exact README snippet with its page margins cropped.
Inspect the generated preview before copying it; the verifier needs an existing
full test run, as described in the test guide.

## Release contents

The `latexbangla/` directory is the complete CTAN upload folder. It contains six
runtime files (four implementation modules under `code/`), the manual source
and PDF, its logo, README, and LICENSE. Upload that folder as an archive according to [CTAN's upload instructions](https://ctan.org/help/upload-pkg).
Tests, standalone examples, and repository documentation stay outside that folder.
Keep the manual's `logo.png` identical to `img/logo.png`.

Before release, run the full suite, refresh the PDFs, update the changelog and
version metadata, and validate any newly claimed engine, font, or package support.
