<p align="center">
  <img src="img/logo.png" alt="LaTeXbangla" width="650">
</p>

Write Bangla in LaTeX with one font and familiar commands: automatic Bangla/English
font switching, bold and italic, Bangla lists and numbering, references, citations,
and Bangla text and digits in math. Choose your own English and math fonts.

[Manual (English ও বাংলা)](latexbangla/latexbangla.pdf) · [Example PDF](examples/example.pdf) · [Example source](examples/example.tex)

## Get started

Copy `latexbangla.sty`, `latexbangla-bengali.lbx`, and the `code/` folder from
[`latexbangla/`](latexbangla/) beside your document. Install one Bangla font and
compile with **XeLaTeX**. Tested on TeX Live 2026.

**Supported Bangla fonts:** Kalpurush, SolaimanLipi, Siyam Rupali, Noto Serif Bengali,
Noto Sans Bengali, and FreeSerif. [Compare the fonts](examples/supported-fonts.pdf).
Use your chosen font name in `\setbanglamainfont`.

```latex
\documentclass{article}
\usepackage{latexbangla}
\setbanglamainfont{Kalpurush}
\setmainfont{TeX Gyre Termes}

\begin{document}
\section{পিথাগোরাসের উপপাদ্য}
সমকোণী ত্রিভুজের দুই লম্ব বাহুর দৈর্ঘ্য $a$ ও $b$,
এবং অতিভুজের দৈর্ঘ্য $c$ হলে, \textit{Pythagorean theorem} অনুযায়ী,
\[a^2+b^2=c^2.\]

A diagonal is the shortest route across a rectangular garden—
বাগানের এক কোণ থেকে বিপরীত কোণে যাওয়ার সরাসরি পথ।
দুই লম্ব বাহুর দৈর্ঘ্য ৩ ও ৪ একক হলে,
\begin{enumerate}
  \item বাহু দুটির দৈর্ঘ্যের বর্গের যোগফল $৩^{২}+৪^{২}=২৫$।
  \item অতিভুজের দৈর্ঘ্য $c=\sqrt{২৫}=৫$ একক।
\end{enumerate}

\textbf{মনে রাখি: a right angle is essential.}
সূত্রটি শুধু সমকোণী ত্রিভুজের জন্য প্রযোজ্য।
\end{document}
```

<img src="img/example.png" alt="A short Bangla lesson on the Pythagorean theorem, typeset in Kalpurush with TeX Gyre Termes for English" width="650">

[Report a bug](https://github.com/Neehan/LaTeXbangla/issues) ·
[latexbangla@googlegroups.com](https://groups.google.com/g/latexbangla) ·
[Contributing](CONTRIBUTING.md)

By [Adib Hasan](https://adibhasan.com) · [LPPL 1.3c or later](LICENSE)
