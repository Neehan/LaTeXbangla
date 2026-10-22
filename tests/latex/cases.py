"""Acceptance specimens for the maintained package; shared TeX bodies are fixtures."""
# Copyright 2026 Adib Hasan. LPPL 1.3c or later; see ../../LICENSE.
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
FIXTURES = ROOT / "fixtures"
FONTS = (FIXTURES / "english-fonts.tex").read_text(encoding="utf-8")
FONT_BODY = (FIXTURES / "fonts.tex").read_text(encoding="utf-8")
FONT_FACE_BODY = (FIXTURES / "font-faces.tex").read_text(encoding="utf-8")
MATH_BODY = (FIXTURES / "math.tex").read_text(encoding="utf-8")
STRUCT_BODY = (FIXTURES / "structures.tex").read_text(encoding="utf-8")
BOOK_BODY = (FIXTURES / "book.tex").read_text(encoding="utf-8")


def document(preamble, body, document_class="article"):
    return (
        r"\documentclass[12pt]{"
        + document_class
        + "}\n"
        + r"\listfiles\tracinglostchars=2"
        + "\n"
        + preamble
        + "\n"
        + r"\begin{document}"
        + "\n"
        + body
        + "\n"
        + r"\end{document}"
        + "\n"
    )


# Supported Bengali font families. Noto test assets are
# pinned separately because the TeX Live image does not include the OS fonts.
BENGALI_FONTS = {
    "noto-serif": "Noto Serif Bengali",
    "noto-sans": "Noto Sans Bengali",
    "kalpurush": "Kalpurush",
    "freeserif": "FreeSerif",
    "solaimanlipi": "SolaimanLipi",
    "siyam-rupali": "Siyam Rupali",
}


def setup(options="", font="Kalpurush"):
    return (
        r"\usepackage[" + options + r"]{latexbangla}" + FONTS + r"\setbanglamainfont{" + font + "}"
    )


def cases():
    data = {}

    def add(name, pre, body, cls="article", passes=3, backend=None, error=None):
        data[name] = dict(
            tex=document(pre, body, cls), passes=passes, backend=backend, expect_error=error
        )

    add(
        "preamble-font-box",
        setup() + r"""
\newfontfamily\alternateenglishfont{TeX Gyre Adventor}
\newsavebox\preamblebox
\sbox\preamblebox{\bengalifont\textbf{PreambleBold বাংলা}}
""",
        r"""
\usebox\preamblebox\par
{\let\rmfamilylatin\alternateenglishfont\bengalifont LocalEnglish বাংলা}\par
OutsideEnglish বাংলা।
""", passes=1,
    )
    # File loads name their faces explicitly. fontspec only forces synthetic
    # bold italic when both AutoFakeBold and AutoFakeSlant are requested.
    add(
        "noto-file-faces",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[Path=/work/tests/latex/fonts/,BoldFont=NotoSerifBengali-Bold.ttf,BoldItalicFont=NotoSerifBengali-Bold.ttf,BoldItalicFeatures={FakeSlant=0.2}]{NotoSerifBengali-Regular.ttf}",
        FONT_FACE_BODY, passes=1,
    )
    add(
        "noto-bold-override",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[AutoFakeBold=4,AutoFakeSlant=0.2]{Noto Serif Bengali}",
        r"বাংলা\par\textbf{বাংলা}\par\textbf{\textit{বাংলা}}", passes=1,
    )
    add("one-font", setup(), FONT_BODY)
    add(
        "switching-contexts", setup() + r"\setotherlanguage{english}",
        (FIXTURES / "switching-contexts.tex").read_text(encoding="utf-8"),
        passes=1,
    )
    add(
        "switching-node-font",
        setup() + r"\setotherlanguage{english}"
        + r"\ifdefined\directlua\setmainfont[Renderer=Node]{TeX Gyre Pagella}\fi",
        (FIXTURES / "switching-contexts.tex").read_text(encoding="utf-8"),
        passes=1,
    )
    add(
        "english-first-families",
        setup(font="Noto Serif Bengali")
        + r"\setbanglasansfont{Noto Sans Bengali}\setbanglamonofont{Kalpurush}",
        r"""
EnglishStart বাংলা EnglishEnd.
\textbf{BoldStart বাংলা BoldEnd} বাংলা RomanAfter.
\textsf{SansStart বাংলা SansEnd \texttt{MonoNested বাংলা MonoEnd} বাংলা SansRestored}
বাংলা RomanRestored.
\texttt{MonoStart বাংলা MonoLast} বাংলা RomanLast.
{\sffamily SansOuter বাংলা {\normalfont NormalInside বাংলা NormalEnd} SansOuterEnd বাংলা}
""",
    )
    add("default-english", r"\usepackage{latexbangla}\setbanglamainfont{Kalpurush}", FONT_BODY)
    add("real-faces", setup(font="FreeSerif"), FONT_BODY)
    add(
        "legacy-siyam-alias",
        r"\usepackage[banglamainfont=SolaimanLipi,banglattfont=SiyamRupali]{latexbangla}" + FONTS,
        FONT_BODY,
    )
    # Measure native dimensions before the package selects the same font.
    # Separate compilations prevent fontspec's global WordSpace adjustments
    # from contaminating the native and explicit-feature comparisons.
    for suffix, font in BENGALI_FONTS.items():
        add(
            "font-transitions-" + suffix,
            setup(font=font),
            r"""
\edef\initialgrouplevel{\the\currentgrouplevel}
English—বাংলা—English.\par
বাংলা “English” বাংলা; English ‘বাংলা’ English.\par
English…বাংলা–English.\par
% Explicit Unicode notation keeps the class-zero joiner regression visible.
\textbf{English^^^^200cবাংলা^^^^200cEnglish}\par
ক্^^^^200cষ ক্^^^^200dষ।\par
\textbf{Bold—বাংলা—café naïve Ānand বাংলা।}\par
\textit{বাংলা—Italic café Ānand—বাংলা।}\par
\textsf{Sans—বাংলা \texttt{Mono—বাংলা} SansAgain—বাংলা।}\par
LatinAgain café Ānand বাংলা।\par
\ifnum\currentgrouplevel=\initialgrouplevel\relax
  \typeout{TRANSITION-GROUPS: balanced}
\fi
""",
            passes=1,
        )
        add(
            "font-faces-" + suffix,
            setup(font=font) + r"\usepackage[a4paper,margin=20mm]{geometry}",
            FONT_FACE_BODY,
            passes=1,
        )
        for adjusted in (False, True):
            pre = r"\usepackage{latexbangla}" + FONTS
            pre += (
                r"\begingroup\fontspec[Script=Bengali]{" + font + r"}"
                r"\typeout{NATIVE-SPACING: \the\fontdimen2\font,"
                r"\the\fontdimen3\font,\the\fontdimen4\font}\endgroup"
                r"\setbanglamainfont"
                + (r"[WordSpace={1.2,1.3,1.4}]" if adjusted else "")
                + "{"
                + font
                + "}"
            )
            add(
                "spacing-" + suffix + ("-adjusted" if adjusted else "-default"),
                pre,
                r"""
\bengalifont
\typeout{SELECTED-SPACING: \the\fontdimen2\font,\the\fontdimen3\font,\the\fontdimen4\font}
{\raggedright
সমকোণী ত্রিভুজের দুই লম্ব বাহুর দৈর্ঘ্য জানা থাকলে অতিভুজের দৈর্ঘ্য নির্ণয় করা যায়।
বাংলা লেখার মধ্যে English words এবং 12 ও ১২ থাকলেও শব্দগুলোর মাঝে স্বাভাবিক ফাঁক থাকা উচিত।\par}
\medskip
সমকোণী ত্রিভুজের দুই লম্ব বাহুর দৈর্ঘ্য জানা থাকলে অতিভুজের দৈর্ঘ্য নির্ণয় করা যায়।
বাংলা লেখার মধ্যে English words এবং 12 ও ১২ থাকলেও শব্দগুলোর মাঝে স্বাভাবিক ফাঁক থাকা উচিত।
""",
                passes=1,
            )
    add(
        "synthetic-bold",
        setup(),
        r"""
বাংলা লেখা সহজ ও সুন্দর।\par
\textbf{বাংলা লেখা সহজ ও সুন্দর।}\par
\textbf{\textit{বাংলা লেখা সহজ ও সুন্দর।}}\par
""",
        passes=1,
    )
    add(
        "font-slant-override",
        r"\usepackage{latexbangla}"
        + FONTS
        + r"\setbanglamainfont[ItalicFeatures={FakeSlant=0.1},BoldItalicFeatures={FakeSlant=0.15}]{Noto Serif Bengali}"
        + r"\usepackage[a4paper,margin=20mm]{geometry}",
        FONT_FACE_BODY,
        passes=1,
    )
    add(
        "font-profile-overrides",
        r"\usepackage{latexbangla}"
        + FONTS
        + r"\setbanglamainfont[Scale=1,WordSpace=1,BoldFeatures={FakeBold=1.5},"
        r"BoldItalicFeatures={FakeBold=1.5,FakeSlant=0.1}]{Siyam Rupali}"
        r"\usepackage[a4paper,margin=20mm]{geometry}",
        r"\bengalifont\typeout{PROFILE-SPACE: \the\fontdimen2\font}"
        r"\typeout{PROFILE-XHEIGHT: \the\fontdimen5\font}" + FONT_FACE_BODY,
        passes=1,
    )
    add(
        "font-siyam-file",
        r"\usepackage{latexbangla}"
        + FONTS
        + r"\setbanglamainfont[Path=/work/tests/latex/fonts/]{Siyamrupali.ttf}"
        r"\usepackage[a4paper,margin=20mm]{geometry}",
        r"\bengalifont\typeout{PROFILE-SPACE: \the\fontdimen2\font}"
        r"\typeout{PROFILE-XHEIGHT: \the\fontdimen5\font}" + FONT_FACE_BODY,
        passes=1,
    )
    add(
        "font-profile-reselection",
        setup(font="Siyam Rupali")
        + r"\setbanglasansfont{Siyam Rupali}\setbanglamonofont{Siyam Rupali}"
        r"\setbanglamainfont{Siyam Rupali}",
        r"\bengalifont\typeout{PROFILE-SPACE: \the\fontdimen2\font}"
        r"\typeout{PROFILE-XHEIGHT: \the\fontdimen5\font}" + FONT_BODY,
        passes=1,
    )
    font_integration_body = r"""
\newcounter{sample}\setcounter{sample}{12}
Decimal: \arabic{sample}. Literal: 12 ১২.
\setcounter{sample}{3}Alphabetic: \alph{sample}.
\begin{enumerate}\item বাংলা\begin{enumerate}\item বাংলা\end{enumerate}\end{enumerate}
\begin{itemize}\item বাংলা bullet\end{itemize}
\begin{tabular}{lr}বাংলা&১২\\English&12\end{tabular}
বাংলা\footnote{বাংলা footnote।} Citation: \cite{sample}.
\begin{thebibliography}{9}\bibitem{sample}বাংলা এবং English. 2020.\end{thebibliography}
"""
    for suffix, font in BENGALI_FONTS.items():
        for unicode_math in (False, True):
            pre = setup(font=font) + r"\usepackage{amsmath,hyperref}"
            if unicode_math:
                pre += r"\usepackage{unicode-math}\setmathfont{TeX Gyre Pagella Math}"
            add(
                "font-" + suffix + ("-unicode" if unicode_math else ""),
                pre,
                FONT_BODY + MATH_BODY + font_integration_body,
            )
    add(
        "font-noto-roles",
        setup(font="Noto Serif Bengali") + r"\setbanglasansfont{Noto Sans Bengali}",
        FONT_BODY,
    )
    add(
        "font-overrides",
        setup()
        + r"""
\setbanglamainfont{FreeSerif}
\setbanglasansfont{FreeSans}[Scale=1.05]
\setbanglamonofont[Scale=0.95]{Kalpurush}
\setmainfont{TeX Gyre Termes}
""",
        FONT_BODY,
    )
    add("dynamic-fallbacks", setup() + r"\setbanglamainfont{FreeSerif}", FONT_BODY)
    add(
        "retained-options",
        r"\usepackage[banglamainfont=Kalpurush,banglattfont=Kalpurush,changecounternumbering=1]{latexbangla}"
        + FONTS,
        FONT_BODY,
    )
    add(
        "retained-main-only",
        r"\usepackage[banglamainfont=Kalpurush]{latexbangla}" + FONTS,
        FONT_BODY,
    )
    add(
        "retained-override",
        r"\usepackage[banglamainfont=Kalpurush]{latexbangla}"
        + FONTS
        + r"\setbanglamainfont{FreeSerif}",
        FONT_BODY,
    )
    add(
        "direct-poly-font",
        r"\usepackage{polyglossia}\newfontfamily\bengalifont[Script=Bengali,AutoFakeBold,AutoFakeSlant]{FreeSerif}\usepackage{latexbangla}"
        + FONTS,
        FONT_BODY,
    )
    add(
        "font-file",
        r"\usepackage{latexbangla}"
        + FONTS
        + r"\setbanglamainfont[Path=/usr/local/texlive/2026/texmf-dist/fonts/truetype/public/bangla/]{fontkalpurush.ttf}",
        FONT_BODY,
    )
    add(
        "explicit-font-features",
        setup()
        + r"\setbanglamainfont[BoldFont=FreeSerif,ItalicFont=FreeSerifItalic,BoldItalicFont=FreeSerifItalic,Scale=1.1]{Kalpurush}",
        FONT_BODY,
    )
    add("missing-font", r"\usepackage{latexbangla}", "বাংলা", error="No Bangla main font")
    add("wrong-engine", setup(), "বাংলা", error="XeTeX")
    data["wrong-engine"]["engine"] = "pdflatex"
    add(
        "empty-font",
        r"\usepackage{latexbangla}\setbanglamainfont{}",
        "বাংলা",
        error="must not be empty",
    )
    add(
        "unknown-font",
        setup(font="NoSuchBanglaFontForTest"),
        "বাংলা",
        error="Package fontspec Error",
    )
    add(
        "non-bengali-font",
        setup(font="TeX Gyre Pagella"),
        "বাংলা",
        error="Choose a font with Bengali coverage",
    )
    add("late-setter", setup(), r"\setbanglamainfont{FreeSerif}", error="must be used before")
    for option in ("banglamainfont", "banglattfont"):
        add(
            "empty-legacy-" + option,
            r"\usepackage[" + option + r"={}]{latexbangla}",
            "বাংলা",
            error="must not be empty",
        )
    for feature in range(3):
        add(
            f"removed-feature-{feature}",
            setup(f"feature={feature}"),
            "বাংলা",
            error="has been removed",
        )
    structures = r"""
\usepackage{amsmath,amsthm,longtable,enumitem,hyperref}
\newtheorem{theorem}{উপপাদ্য}[section]
\providecommand\theoremautorefname{উপপাদ্য}
\renewcommand\theoremautorefname{উপপাদ্য}
"""
    add("structures", setup() + structures, STRUCT_BODY)
    add("structures-off", setup("changecounternumbering=false") + structures, STRUCT_BODY)
    add(
        "author-environments",
        r"\newenvironment{example}{\par Example: }{\par}\newenvironment{solution}{\par Solution: }{\par}"
        + setup(),
        r"\begin{example}বাংলা\end{example}\begin{solution}বাংলা\end{solution}",
    )
    add(
        "numeric-zero-option",
        setup("changecounternumbering=0"),
        r"\section{বাংলা}\begin{enumerate}\item বাংলা\end{enumerate}",
    )
    add(
        "author-numbering-off",
        r"\renewcommand\arabic[1]{X\number\value{#1}}"
        r"\renewcommand\alph[1]{Y\number\value{#1}}" + setup("changecounternumbering=false"),
        r"\newcounter{sample}\setcounter{sample}{12}\arabic{sample}\quad\alph{sample}",
        passes=1,
    )
    for enabled in (True, False):
        add(
            "signed-counters" + ("" if enabled else "-off"),
            setup("" if enabled else "changecounternumbering=false"),
            r"\newcounter{sample}"
            + "\n".join(
                r"\setcounter{sample}{" + str(value) + r"}"
                r"\typeout{SIGNED-" + str(value) + r": \arabic{sample}}"
                r"\arabic{sample}\quad\tobangla{sample}\par"
                for value in (-2147483647, -12, 0, 12, 2147483647)
            ),
            passes=1,
        )
    for style in ("symbol", "roman", "hook"):
        pre = setup() + r"\usepackage{hyperref}"
        if style == "symbol":
            pre = r"\renewcommand\thefootnote{\fnsymbol{footnote}}" + pre
        elif style == "roman":
            pre += r"\renewcommand\thefootnote{\roman{footnote}}"
        else:
            pre += r"\AtBeginDocument{\renewcommand\thefootnote{F\arabic{footnote}}}"
        add(
            "footnotes-" + style,
            pre,
            r"\typeout{FOOTNOTE-FORMAT: \meaning\thefootnote}"
            + "\n".join(
                r"বাংলা\footnote{বাংলা footnote.}\par" for _ in range(9 if style == "symbol" else 2)
            ),
        )
    add(
        "numbering-language-switch",
        setup() + r"\setotherlanguage{english}\renewcommand\thefootnote{\roman{footnote}}",
        r"\newcounter{sample}\setcounter{sample}{-12}"
        r"\selectlanguage{english}\typeout{ENGLISH-COUNTER: \arabic{sample}}"
        r"English\footnote{English.}"
        r"\selectlanguage{bengali}\typeout{BENGALI-COUNTER: \arabic{sample}}"
        r"\typeout{SWITCH-FOOTNOTE: \meaning\thefootnote}বাংলা\footnote{বাংলা।}",
        passes=1,
    )
    # alphalph's built-in commands remain Latin. A custom formatter delegates
    # each digit to the active Bengali alphabet, with an explicit radix of 36.
    for order in ("before", "after"):
        pre = (
            r"\usepackage{alphalph}" + setup()
            if order == "before"
            else setup() + r"\usepackage{alphalph}"
        )
        add(
            "alphalph-" + order,
            pre + r"""
\usepackage{hyperref}
\makeatletter
\newalphalph{\extendedBangla}{\@alph}{36}
\makeatother
\newcounter{example}
\renewcommand\theexample{\extendedBangla{\value{example}}}
""",
            r"Latin: \alphalph{27}, \AlphAlph{27}.\par"
            + "\n".join(
                r"\typeout{EXTENDED-" + str(value) + r"=[\extendedBangla{"
                + str(value) + r"}]}\extendedBangla{" + str(value) + r"}\quad"
                for value in (1, 36, 37, 38, 72, 73, 1332, 1333)
            )
            + r"""
\par\setcounter{example}{36}\refstepcounter{example}\label{extended-example}
Example \theexample. Reference: \ref{extended-example}.
""",
        )
    alph = r"\newcounter{test}\setcounter{test}"
    add(
        "alphabet",
        setup(),
        alph
        + r"{0}Zero=[\alph{test}].\par"
        + "\n".join(
            r"\setcounter{test}{"
            + str(i)
            + r"}\alph{test}/\Alph{test}\quad"
            + r"\typeout{ALPHABET-"
            + str(i)
            + r"=[\alph{test}/\Alph{test}]}"
            for i in range(1, 37)
        ),
    )
    for command in ("alph", "Alph"):
        add(
            f"overflow-{command}",
            setup(),
            alph + "{37}\\" + command + "{test}",
            error="Counter too large",
        )
    add("negative-alphabet", setup(), alph + r"{-1}\alph{test}", error="Counter too large")
    helpers = r"""
\newcounter{custom}\setcounter{custom}{12}
Counter: \tobangla{custom}. Number: \numtobangla{123}.
\setcounter{custom}{-12}Negative: \tobangla{custom}.
Zero: \numtobangla{0}. Leading: \numtobangla{0012}.
Long: \numtobangla{12345678901234567890}.
\section{বাংলা \numtobangla{123}}\label{sec:helper}
\ref{sec:helper}.
"""
    add("converters", setup() + r"\usepackage{hyperref}", helpers)
    add("converters-off", setup("changecounternumbering=false") + r"\usepackage{hyperref}", helpers)
    for cls in ("book", "memoir", "report"):
        body = BOOK_BODY
        if cls == "report":
            for command in (r"\frontmatter", r"\mainmatter", r"\backmatter"):
                body = body.replace(command, "")
        add(cls, setup() + r"\usepackage{amsmath,hyperref}", body, cls=cls)
    add(
        "hyperref-first",
        r"\usepackage{hyperref}" + setup() + r"\usepackage{amsmath}",
        BOOK_BODY,
        cls="book",
    )
    add(
        "custom-labels",
        setup()
        + r"\usepackage{hyperref}\renewcommand\sectionautorefname{বিভাগ}\renewcommand\labelitemi{*}",
        r"\section{বাংলা}\label{sec:a}\autoref{sec:a}\begin{itemize}\item বাংলা\end{itemize}",
    )
    add(
        "custom-autoref-before",
        r"\usepackage{hyperref}\newcommand\authorsectionname{CustomSection}"
        r"\renewcommand\sectionautorefname{\authorsectionname}" + setup() + r"\usepackage{amsmath}",
        r"\section{বাংলা}\label{sec:a}\autoref{sec:a}"
        r"\begin{equation}x=১\label{eq:a}\end{equation}\autoref{eq:a}"
        r"\typeout{EQUATION-NAME: \equationautorefname}",
    )
    nested = r"\begin{itemize}\item বাংলা " * 4 + r"\end{itemize}" * 4
    add("nested-bullets", setup(), nested)
    add(
        "aliased-bullet",
        setup() + r"\let\labelitemi\textbullet",
        r"\begin{itemize}\item বাংলা\end{itemize}",
    )
    add(
        "enumitem-bullet",
        setup() + r"\usepackage{enumitem}",
        r"\begin{itemize}[label=\textbullet,leftmargin=*]\item বাংলা\item[\textbullet] বাংলা\end{itemize}",
    )
    add(
        "text-symbols",
        setup(),
        r"বাংলা \textbullet\ \textendash\ \textasteriskcentered\ \textperiodcentered\ বাংলা",
    )
    add("math", setup() + r"\usepackage{amsmath}", MATH_BODY)
    add(
        "common-math",
        setup() + r"\usepackage{mathtools,amssymb,bm,cancel,amsthm,hyperref}"
        r"\newtheorem{result}{উপপাদ্য}",
        r"""
\section{গণিত Mathematics}
\begin{equation}\label{eq:common}
\begin{aligned}
\text{দূরত্ব}&=১২+3\\
\bm{x}_২&=\cancel{২}+\mathbb{R}
\end{aligned}
\end{equation}
\begin{result}\label{thm:common}বাংলা theorem.\end{result}
\begin{proof}বাংলা proof $\bm{১২}+\frac{৩}{৪}$.\end{proof}
Equation \eqref{eq:common}; theorem \ref{thm:common}.
""",
    )
    add(
        "common-tables",
        setup() + r"\usepackage{array,booktabs,tabularx,longtable,multirow,siunitx,hyperref}",
        r"""
\begin{table}[ht]
\caption{বাংলা সারণি}\label{tab:common}
\begin{tabularx}{\linewidth}{lX S[table-format=2.1]}
\toprule
নাম & বিবরণ & {Value}\\\midrule
\multirow{2}{*}{বাংলা} & English and বাংলা ১২ & 12.5\\
& আরও লেখা & 3.0\\\bottomrule
\end{tabularx}
\end{table}
Table \ref{tab:common}. Literal: 12, ১২.
\begin{longtable}{ll}
\caption{আরও তথ্য}\label{tab:long}\\
\toprule নাম & মান\\\midrule\endhead
বাংলা & ১২\\English & 12\\\bottomrule
\end{longtable}
Long table \ref{tab:long}.
""",
    )
    add(
        "common-layout",
        setup() + r"""
\usepackage[margin=25mm,headheight=18pt]{geometry}
\usepackage{microtype,graphicx,xcolor,float,caption,subcaption,fancyhdr,titlesec,hyperref}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{বাংলা English}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries}{\thesection}{1em}{}
""",
        r"""
\section{বাংলা শিরোনাম}\label{sec:layout}
Mixed English and বাংলা text.\footnote{বাংলা footnote.}
\begin{figure}[H]\centering
\begin{subfigure}{.4\linewidth}\centering
\fbox{\rule{0pt}{15mm}\rule{20mm}{0pt}}\caption{প্রথম}\label{fig:first}
\end{subfigure}\quad
\begin{subfigure}{.4\linewidth}\centering
\textcolor{blue}{\fbox{\rule{0pt}{15mm}\rule{20mm}{0pt}}}\caption{দ্বিতীয়}\label{fig:second}
\end{subfigure}
\caption{বাংলা চিত্র}\label{fig:common}
\end{figure}
Section \ref{sec:layout}; figure \ref{fig:common}; parts \subref{fig:first}, \subref{fig:second}.
\newpage
Second page বাংলা.\par\textbf{Bold English বাংলা.}
""",
    )
    reference_packages = r"""
\usepackage{amsmath,amsthm,hyperref}
\usepackage[english]{cleveref}
\newtheorem{result}{উপপাদ্য}[section]
\crefname{equation}{সমীকরণ}{সমীকরণসমূহ}
\crefname{result}{উপপাদ্য}{উপপাদ্যসমূহ}
\AtBeginDocument{%
  \renewcommand{\crefrangeconjunction}{ থেকে }%
  \renewcommand{\crefpairconjunction}{ ও }%
}
"""
    reference_body = (FIXTURES / "common-references.tex").read_text(encoding="utf-8")
    for variant in ("", "-off", "-first", "-no-hyperref"):
        pre = setup("changecounternumbering=false" if variant == "-off" else "")
        pre = reference_packages + pre if variant == "-first" else pre + reference_packages
        if variant == "-no-hyperref":
            pre = pre.replace("amsmath,amsthm,hyperref", "amsmath,amsthm")
        add("common-cleveref" + variant, pre, reference_body)
    protrusion_body = (FIXTURES / "microtype.tex").read_text(encoding="utf-8")
    protrusion_font = r"\newfontfamily\protrusionfont{TeX Gyre Pagella}"
    add(
        "microtype-baseline",
        r"\usepackage{fontspec}" + FONTS + r"\usepackage{microtype}" + protrusion_font,
        protrusion_body,
        passes=1,
    )
    for suffix, font in BENGALI_FONTS.items():
        add(
            "microtype-" + suffix,
            setup(font=font) + r"\usepackage{microtype}" + protrusion_font,
            FONT_BODY + protrusion_body,
            passes=1,
        )
    add(
        "microtype-first",
        r"\usepackage{microtype}" + setup() + protrusion_font,
        FONT_BODY + protrusion_body,
        passes=1,
    )
    add(
        "common-boxes",
        setup() + r"""
\usepackage{amsmath,enumitem,tcolorbox,hyperref}
\tcbuselibrary{breakable,theorems}
\newtcbtheorem{exercisebox}{অনুশীলনী}{colback=blue!3,colframe=blue!50!black}{exercise}
""",
        r"""
\begin{exercisebox}{বাংলা English}{first}
\textbf{বাংলা bold.} $\text{মান}=১২+3$।
\begin{enumerate}[label=(\alph*)]
\item প্রথম\item দ্বিতীয়
\end{enumerate}
\end{exercisebox}
Exercise \ref{exercise:first}.
\begin{tcolorbox}[breakable,title={বাংলা শিরোনাম}]
বাংলা paragraph with English.\par বাংলা paragraph.
\end{tcolorbox}
""",
    )
    add("math-off", setup("changecounternumbering=false") + r"\usepackage{amsmath}", MATH_BODY)
    for unicode_math in (False, True):
        add(
            "math-weight" + ("-unicode" if unicode_math else ""),
            setup()
            # Latin Modern Math has no bold face. Define the bold math version
            # explicitly so its missing face does not obscure the digit-weight test.
            + (
                r"\usepackage{unicode-math}\setmathfont{Latin Modern Math}"
                r"\setmathfont[version=bold]{Latin Modern Math}"
                if unicode_math
                else ""
            ),
            r"$১২+34$\par\textbf{$১২+34$}\par{\boldmath $১২+34$}\par$১২+34$",
            passes=1,
        )
    for font, suffix in (("TeX Gyre Pagella Math", "pagella"), ("Latin Modern Math", "lm")):
        add(
            "unicode-math-" + suffix,
            setup() + r"\usepackage{unicode-math}\setmathfont{" + font + "}",
            MATH_BODY,
        )
    add(
        "unicode-math-first",
        r"\usepackage{unicode-math}\setmathfont{TeX Gyre Pagella Math}" + setup(),
        MATH_BODY,
    )
    add("newtxmath", r"\usepackage{amsmath,newtxmath}" + setup(), MATH_BODY)
    add(
        "all-digits",
        setup() + r"\usepackage{amsmath}",
        r"""
0123456789 এবং ০১২৩৪৫৬৭৮৯।
\[0123456789\qquad ০১২৩৪৫৬৭৮৯\]
\[x^{৯}+x^{y^{৮}}+\frac{১২}{\frac{৩}{৪}}\]
{\boldmath $১২+34$}\quad $\mathbf{১২+34}$
""",
    )
    bibbody = r"""
Citation: \cite{gamma,alpha,beta}. Single: \cite{beta}.
Note: \cite[pp.~12--14]{alpha}.
\begin{thebibliography}{9}
\bibitem{alpha} Alpha author. English title. 2020.
\bibitem{beta} বাংলা লেখক। বাংলা শিরোনাম। ২০২১।
\bibitem{gamma} Gamma author. Another title. 2022.
\end{thebibliography}
"""
    for system in ("standard", "natbib", "biblatex"):
        for enabled in (True, False):
            options = "" if enabled else "changecounternumbering=false"
            pre = setup(options)
            backend = None
            body = bibbody
            if system == "natbib":
                pre += r"\usepackage[numbers,sort&compress]{natbib}"
            if system == "biblatex":
                pre += r"\usepackage[backend=biber,style=numeric-comp]{biblatex}\addbibresource{references.bib}"
                body = r"Citation: \cite{gamma,alpha,beta}. Single: \cite{beta}. Note: \cite[12--14]{alpha}.\printbibliography"
                backend = "biber"
            add(
                "citations-" + system + ("" if enabled else "-off"),
                pre + r"\usepackage{hyperref}",
                body,
                backend=backend,
            )
    add(
        "citations-text-label",
        setup() + r"\usepackage{hyperref}",
        r"\cite{a}\begin{thebibliography}{Knuth84}\bibitem[Knuth84]{a}A book. 1984.\end{thebibliography}",
    )
    add(
        "citations-styled-label",
        setup() + r"\usepackage{hyperref}",
        r"\cite{a}\begin{thebibliography}{Knuth84}\bibitem[\textbf{Knuth84}]{a}A book. 1984.\end{thebibliography}",
    )
    add(
        "citations-numeric-label",
        setup() + r"\usepackage{hyperref}",
        r"\cite{a}\begin{thebibliography}{12}\bibitem[12]{a}A book. 1984.\end{thebibliography}",
    )
    add("citations-no-hyperref", setup(), bibbody)
    add(
        "natbib-first",
        r"\usepackage[numbers,sort&compress]{natbib}" + setup() + r"\usepackage{hyperref}",
        bibbody,
    )
    add(
        "natbib-custom-style",
        setup()
        + r"\usepackage[numbers]{natbib}\renewcommand\citenumfont[1]{\textbf{#1}}\renewcommand\bibnumfmt[1]{(#1)}\usepackage{hyperref}",
        bibbody,
    )
    add(
        "natbib-author-year",
        setup() + r"\usepackage[authoryear]{natbib}\usepackage{hyperref}",
        r"\citet{a}; \citep{a}.\begin{thebibliography}{1}\bibitem[Author(2020)]{a}Author. A book. 2020.\end{thebibliography}",
    )
    add(
        "biblatex-wrong-order",
        r"\usepackage[backend=biber,style=numeric-comp]{biblatex}\addbibresource{references.bib}"
        + setup(),
        "বাংলা",
        error="'polyglossia' loaded after biblatex",
    )
    add(
        "biblatex-preloaded",
        r"\usepackage{polyglossia}\usepackage[backend=biber,style=numeric-comp]{biblatex}\addbibresource{references.bib}"
        + setup()
        + r"\usepackage{hyperref}",
        r"\cite{alpha,beta,gamma}\printbibliography",
        backend="biber",
    )
    add(
        "biblatex-custom-style",
        setup()
        + r"\usepackage[backend=biber,style=numeric]{biblatex}\addbibresource{references.bib}\DeclareFieldFormat{labelnumberwidth}{\mkbibparens{#1}}\usepackage{hyperref}",
        r"\cite{alpha,beta,gamma}\printbibliography",
        backend="biber",
    )
    add(
        "biblatex-author-year",
        setup()
        + r"\usepackage[backend=biber,style=authoryear]{biblatex}\addbibresource{references.bib}\usepackage{hyperref}",
        r"\cite{alpha}\printbibliography",
        backend="biber",
    )
    add(
        "siunitx",
        setup() + r"\usepackage{siunitx}",
        r"\num{12.5}\begin{tabular}{S}12.5\\3.75\end{tabular}",
    )
    add(
        "verbatim",
        setup() + r"\usepackage{hyperref}",
        r"""
বাংলা \url{https://example.org/a12}।
\begin{verbatim}
English code 12; বাংলা ১২
\end{verbatim}
""",
    )
    add(
        "long-mixed",
        setup() + r"\usepackage{amsmath}",
        (r"বাংলা English text 12 ১২। \textbf{বাংলা Bold} $x^{২}+12$।\par" + "\n") * 400,
        passes=1,
    )
    add(
        "standalone-fontspec",
        r"\usepackage{fontspec}\setmainfont{TeX Gyre Pagella}\newfontfamily\banglatext[Script=Bengali]{Kalpurush}",
        r"An English sentence with {\banglatext বাংলা লেখা}.",
    )
    manual_source = (REPO / "latexbangla/latexbangla.tex").read_text(encoding="utf-8")
    # Compile the displayed font comparison independently. In particular, the
    # fontspec-only example must not inherit the manual's language package.
    manual_documents = [
        block for block in re.findall(
            r"\\begin\{code\}(.*?)\\end\{code\}", manual_source, re.S
        ) if r"\documentclass" in block
    ]
    opening_document = next(
        block for block in manual_documents if r"\usepackage{latexbangla}" in block
    )
    opening_body = re.search(
        r"\\begin\{examplepair\}(.*?)\\end\{examplepair\}", manual_source, re.S
    )
    assert opening_body is not None, "The manual needs its opening code/output example."
    data["manual-english-font"] = dict(
        tex=opening_document.split(r"\begin{document}", 1)[0]
        + "\\begin{document}\n" + opening_body.group(1) + "\n\\end{document}\n",
        passes=1, backend=None, expect_error=None,
    )
    data["manual-fontspec-comparison"] = dict(
        tex=next(
            block for block in manual_documents if r"\usepackage{latexbangla}" not in block
        ),
        passes=1, backend=None, expect_error=None,
    )
    data["manual"] = dict(
        tex=manual_source,
        passes=3,
        backend=None,
        expect_error=None,
        restricted_shell_escape=True,
    )
    data["example"] = dict(
        tex=(REPO / "examples/example.tex").read_text(encoding="utf-8"), passes=3, backend=None, expect_error=None
    )
    data["supported-fonts"] = dict(
        tex=(REPO / "examples/supported-fonts.tex").read_text(encoding="utf-8"),
        passes=2,
        backend=None,
        expect_error=None,
    )
    # Compile the exact README snippet; verify.py renders its preview for refreshing the README.
    readme_example = (REPO / "README.md").read_text(encoding="utf-8").split("```latex\n", 1)[1].split("```", 1)[0]
    data["readme-example"] = dict(tex=readme_example, passes=1, backend=None, expect_error=None)
    # graphicx loads epstopdf on LuaTeX. Use TeX Live's normal restricted shell
    # policy for these graphics examples, as for the minted manual.
    for name in ("common-math", "common-layout", "common-boxes"):
        data[name]["restricted_shell_escape"] = True
    return data
