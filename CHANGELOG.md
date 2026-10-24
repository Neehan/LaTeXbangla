# Changelog

## 2.1

- Translate standard `cleveref` reference names and connecting words automatically.
- Add Mina, AdorshoLipi, BenSen, BenSenHandwriting, Atma, Alkatra and Shonar Bangla, with tuned font defaults.
- Support updated TeX Live 2024 and later.
- Keep combining Latin accents in the English font, fixing names such as Erdős with Kalpurush.

## 2.0

- Add Assamese language support with `language=assamese`, translated examples and a complete Assamese manual.
- Add LuaLaTeX support.
- Expand the supported Bangla fonts and the font comparison guide.
- Refine boldness, size and word spacing across supported fonts.
- Preserve locally selected English fonts, including nested font and style changes.
- Keep font styles and sizing consistent across engines, including bold italic
  and Siyam Rupali's heading spacing.

## 1.0

- Modernize for current XeLaTeX and Polyglossia, fixing the old numbering incompatibility.
- Require only one Bangla font, with fontspec-style setters, automatic bold/italic,
  and independent English and math font choices. Test six Bangla font families.
- Improve Bangla numbering, alphabetic lists, references, citations, and math digits.
  Typed Western and Bangla digits keep their original script.
- Add compatibility with cleveref and microtype, and document extended alphabetic
  labels with alphalph.
- Preserve legacy font options and `changecounternumbering`. Remove `feature=0/1/2`
  and bundled theorem/layout styles; define these in your document or class.
- Refresh the manual and examples, add a font comparison PDF, and expand automated
  compilation and PDF checks.
