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
ASSAMESE_FONT_FACE_BODY = (
    FONT_FACE_BODY.replace(r"\bengalifont", r"\assamesefont")
    .replace("শিক্ষার্থী, দৃষ্টি, স্বচ্ছ, স্বাধীনতা, পূর্ণসংখ্যা, ক্ষুদ্র, জ্ঞান।",
             "অসমীয়া, প্ৰশ্ন, ৰাষ্ট্ৰ, শ্ৰদ্ধা, স্বৰ, ৰু, ৰূ, ৱা।")
    .replace("বাংলা", "অসমীয়া").replace("এবং", "আৰু")
)
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


# Supported font selections. fetch-fonts.py pins assets not bundled in TeX Live.
BENGALI_FONTS = {
    "noto-serif": "Noto Serif Bengali",
    "noto-sans": "Noto Sans Bengali",
    "kalpurush": "Kalpurush",
    "freeserif": "FreeSerif",
    "solaimanlipi": "SolaimanLipi",
    "siyam-rupali": "Siyam Rupali",
    # Load the variable file directly: XeTeX's family-name lookup can select
    # a named instance that xdvipdfmx cannot embed. A bracket-free filename
    # avoids XeTeX's interpretation of brackets in a font loading request.
    "anek-bangla": "AnekBangla-VF.ttf",
    "tiro-bangla": "Tiro Bangla",
    "galada": "Galada",
    "hind-siliguri": "Hind Siliguri",
    "nikosh": "Nikosh",
    "mukti": "Mukti",
    "baloo-da-2": "Baloo Da 2",
    "lohit-bengali": "Lohit Bengali",
    "jamrul": "Jamrul",
    "likhan": "Likhan",
    "shimanto": "Shimanto",
    "mina": "Mina",
    "adorsholipi": "AdorshoLipi",
    "bensen": "BenSen",
    "bensen-handwriting": "BenSenHandwriting",
    "atma": "Atma",
    "alkatra": "Alkatra-VF.ttf",
}
# Kohinoor is supplied by the tester, never downloaded or distributed here.
if (ROOT / "fonts/KohinoorBangla.ttc").exists():
    BENGALI_FONTS["kohinoor-bangla"] = "Kohinoor Bangla"

if all((ROOT / "fonts" / name).exists() for name in ("Shonar.ttf", "Shonarb.ttf")):
    BENGALI_FONTS["shonar-bangla"] = "Shonar Bangla"


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

    for language in ("bangla", "assamese"):
        add(
            "latin-accents-" + language,
            r"\usepackage[language=" + language + r"]{latexbangla}"
            r"\setbanglamainfont{Kalpurush}\tracinglostchars=3"
            r"\newfontfamily\accenttestfont{TeX Gyre Pagella}",
            (FIXTURES / "latin-accents.tex").read_text(encoding="utf-8"),
            passes=1,
        )
        add(
            "latin-accents-biblatex-" + language,
            r"\usepackage[language=" + language + r"]{latexbangla}"
            r"\setbanglamainfont{Kalpurush}\tracinglostchars=3"
            r"\usepackage[backend=biber,style=numeric]{biblatex}"
            + (FIXTURES / "latin-accent-bibliography.tex").read_text(encoding="utf-8")
            + r"\addbibresource{accent-references.bib}",
            r"\nocite{*}\printbibliography", backend="biber",
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
        "tiro-file-faces",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[Path=/work/tests/latex/fonts/,ItalicFont=TiroBangla-Italic.ttf,BoldItalicFont=TiroBangla-Italic.ttf,BoldItalicFeatures={FakeBold=3.5}]{TiroBangla-Regular.ttf}",
        FONT_FACE_BODY, passes=1,
    )
    add(
        "font-faces-galada-file",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[Path=/work/tests/latex/fonts/]{Galada-Regular.ttf}",
        FONT_FACE_BODY + r"\bengalifont\typeout{GALADA-FILE-SPACE: \the\fontdimen2\font}",
        passes=1,
    )
    for suffix, filename, bold_filename in (
        ("jamrul", "JamrulNormal.ttf", None),
        ("likhan", "LikhanNormal.ttf", None),
        ("shimanto", "Shimanto.ttf", None),
        ("mina", "Mina-Regular.ttf", "Mina-Bold.ttf"),
        ("adorsholipi", "AdorshoLipi_20-07-2007.ttf", None),
        ("bensen", "BenSen.ttf", None),
        ("bensen-handwriting", "BenSenHandwriting.ttf", None),
        ("atma", "Atma-Regular.ttf", "Atma-Bold.ttf"),
        ("shonar-bangla", "Shonar.ttf", "Shonarb.ttf"),
    ):
        if suffix not in BENGALI_FONTS:
            continue
        features = "Path=/work/tests/latex/fonts/"
        if bold_filename:
            features += ",BoldFont=" + bold_filename + ",BoldItalicFont=" + bold_filename
        add("font-faces-" + suffix + "-file",
            r"\usepackage{latexbangla}" + FONTS
            + r"\setbanglamainfont[" + features + "]{" + filename + "}"
            + r"\usepackage[a4paper,margin=20mm]{geometry}",
            FONT_FACE_BODY, passes=1)
    # Isolate Shimanto's missing joiner glyphs from automatic font switching.
    add("shimanto-joiners-fontspec", r"\usepackage{fontspec}\pagestyle{empty}"
        + r"\ifdefined\directlua\defaultfontfeatures{Renderer=HarfBuzz}\fi"
        + r"\setmainfont[Script=Bengali]{Shimanto}",
        r"ক্^^^^200cষ ক্^^^^200dষ।", passes=1)
    add(
        "font-faces-tiro-overrides",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[Scale=0.95,AutoFakeBold=4,AutoFakeSlant=0.1]{Tiro Bangla}",
        FONT_FACE_BODY, passes=1,
    )
    add(
        "noto-bold-override",
        r"\usepackage{latexbangla}" + FONTS
        + r"\setbanglamainfont[AutoFakeBold=4,AutoFakeSlant=0.2]{Noto Serif Bengali}",
        r"বাংলা\par\textbf{বাংলা}\par\textbf{\textit{বাংলা}}", passes=1,
    )
    # Family-specific face hints must remain defaults, not override user choices.
    for suffix in ("mukti", "kohinoor-bangla", "atma", "bensen"):
        if suffix in BENGALI_FONTS:
            add(
                "font-faces-" + suffix + "-overrides",
                r"\usepackage{latexbangla}" + FONTS
                + r"\setbanglamainfont[Scale=0.95,AutoFakeBold=4,AutoFakeSlant=0.1]{"
                + BENGALI_FONTS[suffix] + "}",
                FONT_FACE_BODY, passes=1,
            )

    add("assamese-basic", setup("language=assamese", "Noto Serif Bengali")
        + r"\setbanglasansfont{Noto Sans Bengali}\setbanglamonofont{Mukti}"
        + r"\usepackage{amsthm,hyperref}\setotherlanguage{english}", r"""
\year=2026\month=10\day=23
\typeout{ASSAMESE-LANGUAGE: \languagename/\BCPdata{language}}
\typeout{ASSAMESE-TABLE: \tablename}
\typeout{ASSAMESE-TABLE-LIST: \listtablename}
\typeout{ASSAMESE-EQUATION: \equationautorefname}
\section{অসমীয়া ভাষা}\label{sec:assamese}
অসমীয়া আৰু English একেলগে লিখিব পাৰি। ৰ ৱ ৰ্ক ৰু ৰূ ৱা প্ৰ শ্ৰ ক্ষ।
\textbf{অসমীয়া আৰু BoldEnglish}\textit{অসমীয়া আৰু ItalicEnglish}
\textsf{অসমীয়া ৰ ৱ SansEnglish}\texttt{অসমীয়া ৰ ৱ MonoEnglish}
\footnote{প্ৰথম পাদটীকা।}
\begin{enumerate}\item প্ৰথম।\begin{enumerate}\item ভিতৰৰ পদ।\end{enumerate}\end{enumerate}
\newcounter{review}\setcounter{review}{27}
AlphabetRa: \alph{review}.\setcounter{review}{29} AlphabetWa: \Alph{review}.
\setcounter{review}{37}\typeout{ASSAMESE-LAST-LETTER: \alph{review}}
\begin{equation}x^২ + ৩ = 12\quad\text{প্ৰস্থ}=৩\quad\text{দুৱাৰ}=৪\label{eq:assamese}\end{equation}
\autoref{sec:assamese}; \autoref{eq:assamese}.
\begin{proof}প্ৰমাণৰ উদাহৰণ।\end{proof}
\today.\quad\localnumeral{123}.
\textenglish{English passage.} অসমীয়া আকৌ।
\typeout{ASSAMESE-RETURN: \languagename/\BCPdata{language}}
\begin{thebibliography}{9}\bibitem{sample}অসমীয়া পুথি।\end{thebibliography}
""")
    add("assamese-off", setup("language=assamese,changecounternumbering=false", "Noto Serif Bengali"),
        r"\section{অসমীয়া}১২ আৰু 12।\begin{enumerate}\item পদ।\begin{enumerate}\item পদ।\end{enumerate}\end{enumerate}")
    add("assamese-mukti", setup("language=assamese", "Mukti"),
        r"অসমীয়া ৰ ৱ প্ৰ ৰু ৰূ।\textbf{অসমীয়া}\textit{অসমীয়া}\textbf{\textit{অসমীয়া}}", passes=1)

    add("one-font", setup(), FONT_BODY)
    for language in ("bangla", "assamese"):
        add(
            "local-fonts-" + language,
            r"\usepackage{fontspec}\newfontfamily\quotefont{TeX Gyre Adventor}"
            + setup("language=" + language)
            + r"\setotherlanguage{english}\usepackage{amsmath}"
            r"\newfontfamily\nestedfont{TeX Gyre Termes}"
            r"\newsavebox\localfontbox\sbox\localfontbox{\quotefont PreambleQuote বাংলা}",
            (FIXTURES / "local-fonts.tex").read_text(encoding="utf-8"), passes=1,
        )
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
    # XeLaTeX exercises the portable file default; LuaLaTeX also supports
    # real weight and width selection through the public fontspec features.
    anek_settings = r"""\setbanglamainfont[
  Weight=400,
  BoldFont=*, BoldFeatures={Weight=700},
  BoldItalicFont=*,
  BoldItalicFeatures={Weight=700,FakeSlant=0.2}
]{AnekBangla-VF.ttf}"""
    add(
        "anek-variable-weights",
        r"\usepackage{latexbangla}" + FONTS + r"\ifLuaTeX" + anek_settings
        + r"\else\setbanglamainfont{AnekBangla-VF.ttf}\fi",
        FONT_FACE_BODY + r"""
\ifLuaTeX
  \begingroup\bengalifont
    \typeout{ANEK-REGULAR-FONT: \fontname\font}
    {\bfseries\typeout{ANEK-BOLD-FONT: \fontname\font}}
    {\bfseries\itshape\typeout{ANEK-BOLDITALIC-FONT: \fontname\font}}
    {\addfontfeatures{Width=75}\setbox0=\hbox{বাংলা ভাষা}\typeout{ANEK-CONDENSED: \the\wd0}}
    {\addfontfeatures{Width=125}\setbox0=\hbox{বাংলা ভাষা}\typeout{ANEK-EXPANDED: \the\wd0}}
  \endgroup
\fi
""", passes=1,
    )
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
            FONT_FACE_BODY + (
                r"\bengalifont\typeout{MUKTI-XHEIGHT: \the\fontdimen5\font; ka: \the\fontcharht\font`ক}"
                if suffix == "mukti" else ""
            ),
            passes=1,
        )
        for adjusted in (False, True):
            # Capture LaTeX's actual default English family before Polyglossia
            # and the specimen's English font choices replace it.
            pre = (r"\usepackage{fontspec}\edef\spacingdefaultfamily{\rmdefault}"
                   r"\newcommand\spacingdefaultfont{\fontfamily{\spacingdefaultfamily}\selectfont}"
                   r"\usepackage{latexbangla}" + FONTS)
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
                (FIXTURES / "spacing.tex").read_text(encoding="utf-8"),
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
        + r"\setbanglamainfont{fontkalpurush.ttf}",
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
    # each digit to the selected alphabet, using its length as the radix.
    for language, order, radix in (
        ("bangla", "before", 35), ("bangla", "after", 35),
        ("assamese", "before", 37),
    ):
        language_setup = setup("language=" + language)
        pre = (
            r"\usepackage{alphalph}" + language_setup
            if order == "before"
            else language_setup + r"\usepackage{alphalph}"
        )
        add(
            ("assamese-" if language == "assamese" else "") + "alphalph-" + order,
            pre + r"""
\usepackage{hyperref}
\makeatletter
\newalphalph{\extendedBangla}{\@alph}{RADIX}
\makeatother
\newcounter{example}
\renewcommand\theexample{\extendedBangla{\value{example}}}
""".replace("RADIX", str(radix)),
            r"Latin: \alphalph{27}, \AlphAlph{27}.\par"
            + "\n".join(
                r"\typeout{EXTENDED-" + str(value) + r"=[\extendedBangla{"
                + str(value) + r"}]}\extendedBangla{" + str(value) + r"}\quad"
                for value in (1, radix, radix + 1, radix + 2, 2 * radix,
                              2 * radix + 1, radix * (radix + 1), radix * (radix + 1) + 1)
            )
            + r"""
\par\setcounter{example}{RADIX}\refstepcounter{example}\label{extended-example}
Example \theexample. Reference: \ref{extended-example}.
""".replace("RADIX", str(radix)),
        )
    alph = r"\newcounter{test}\setcounter{test}"
    # Check every position, including multi-code-point Assamese entries.
    for language, size in (("bangla", 35), ("assamese", 37)):
        add(
            "alphabet" if language == "bangla" else "assamese-alphabet",
            setup("language=" + language),
            alph
            + r"{0}Zero=[\alph{test}].\par"
            + "\n".join(
                r"\setcounter{test}{"
                + str(i)
                + r"}\alph{test}/\Alph{test}\quad"
                + r"\typeout{ALPHABET-"
                + str(i)
                + r"=[\alph{test}/\Alph{test}]}"
                for i in range(1, size + 1)
            ),
        )
    # Case names must also be distinct on case-insensitive filesystems.
    for command, suffix in (("alph", "lowercase"), ("Alph", "uppercase")):
        add(
            f"overflow-{suffix}",
            setup(),
            alph + "{36}\\" + command + "{test}",
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
    # Historical reports are linked in issue-coverage.md. These specimens
    # exercise the reported interactions without obsolete template workarounds.
    for language in ("bangla", "assamese"):
        add(
            "reported-headings-" + language,
            setup("language=" + language)
            + r"\usepackage{tocloft,hyperref}\setcounter{tocdepth}{3}\setcounter{secnumdepth}{3}",
            r"""
\tableofcontents
\chapter{Chapter বাংলা}\label{reported:chapter}
\section{Section বাংলা}\label{reported:section}
\subsection{Subsection বাংলা}\label{reported:subsection}
\subsubsection{Detail বাংলা}\label{reported:detail}
References: \ref{reported:section}, \ref{reported:subsection}, \ref{reported:detail}.
\section{Next বাংলা}\subsection{Reset বাংলা}\label{reported:reset}
Reset: \ref{reported:reset}.
""", cls="book",
        )
    for variant in ("plain", "titlesec"):
        # titlesec does not record starred section names for nameref. The
        # author's explicit name and anchor are needed independently of us.
        starred_section = r"\section*{Unnumbered Section}\label{reported:star-section}"
        if variant == "titlesec":
            starred_section = r"""\section*{Unnumbered Section}\phantomsection
\makeatletter\def\@currentlabelname{Unnumbered Section}\makeatother
\label{reported:star-section}"""
        add(
            "reported-nameref-" + variant,
            setup() + (r"\usepackage{titlesec}" if variant == "titlesec" else "")
            + r"\usepackage{hyperref}",
            r"""
\chapter*{Unnumbered Chapter}\label{reported:star-chapter}
STARREDSECTION
\chapter{Numbered Chapter}\label{reported:numbered-chapter}
\section{Numbered Section}\label{reported:numbered-section}
Names: \nameref{reported:star-chapter}; \nameref{reported:star-section};
\nameref{reported:numbered-chapter}; \nameref{reported:numbered-section}.
""".replace("STARREDSECTION", starred_section), cls="book",
        )
    add(
        "reported-quotation",
        setup() + r"""
\setotherlanguage{english}
\usepackage[style=english]{csquotes}
\newenvironment{chapterquote}[1]
  {\def\quoteauthor{#1}\begin{quotation}\itshape}
  {\par\raggedleft\normalfont\quoteauthor\par\end{quotation}}
""",
        r"""
বাংলা BeforeQuote.
\begin{chapterquote}{লেখক (Author)}
বাংলা \enquote{English \enquote{বাংলা} English} বাংলা।
\par\textenglish{EnglishQuotation}
\end{chapterquote}
বাংলা AfterQuote.
\par ``বাংলা'' and ``English''.
""",
    )
    add(
        "reported-language-captions",
        setup() + r"\setotherlanguage{english}"
        r"\gappto\captionsenglish{\renewcommand\figurename{Fig.}}",
        r"""
Native: \figurename.
\begin{english}English: \figurename.\end{english}
Restored: \figurename.
\begin{english}EnglishAgain: \figurename.\end{english}
""", passes=1,
    )
    add(
        "reported-biblatex-english",
        setup() + r"\setotherlanguage{english}\usepackage[style=english]{csquotes}"
        r"\usepackage[backend=biber,style=alphabetic,sorting=nyt,language=english,autolang=other]{biblatex}"
        r"\addbibresource{references.bib}\usepackage{hyperref}",
        r"বাংলা \cite{alpha,gamma}.\printbibliography",
        backend="biber",
    )
    add(
        "reported-enumerate",
        setup() + r"\usepackage{enumerate}",
        r"""
\begin{enumerate}[(1।)]
\item First বাংলা\label{reported:outer}
\begin{enumerate}[(a)]
\item Inner বাংলা\item Next বাংলা\label{reported:inner}
\end{enumerate}
\item Second বাংলা
\end{enumerate}
References: \ref{reported:outer}, \ref{reported:inner}.
""",
    )
    add(
        "reported-ornaments",
        setup() + r"\usepackage{pgfornament}",
        r"""
\begin{tikzpicture}
\node[draw,align=center] (text) {\textbf{বাংলা English}\\আরও লেখা};
\node[anchor=south] at (text.north) {\pgfornament[width=3cm]{71}};
\end{tikzpicture}
""", passes=1,
    )
    data["reported-ornaments"]["restricted_shell_escape"] = True
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
\usepackage{cleveref}
\newtheorem{result}{উপপাদ্য}[section]
\crefname{result}{উপপাদ্য}{উপপাদ্যসমূহ}
"""
    reference_body = (FIXTURES / "common-references.tex").read_text(encoding="utf-8")
    for variant in ("", "-off", "-first", "-no-hyperref"):
        pre = setup("changecounternumbering=false" if variant == "-off" else "")
        pre = reference_packages + pre if variant == "-first" else pre + reference_packages
        if variant == "-no-hyperref":
            pre = pre.replace("amsmath,amsthm,hyperref", "amsmath,amsthm")
        add("common-cleveref" + variant, pre, reference_body)
    # Author names and joins must survive either package order and late setup.
    reference_overrides = r"""
\crefname{equation}{relation}{relations}
\Crefname{equation}{Relation}{Relations}
\newcommand{\crefpairconjunction}{ plus }
\newcommand{\crefrangeconjunction}{ through }
"""
    for variant in ("before", "after", "begin"):
        base = reference_packages
        if variant == "before":
            pre = base + reference_overrides + setup()
        else:
            overrides = reference_overrides.replace(r"\newcommand", r"\renewcommand")
            if variant == "begin":
                overrides = r"\AtBeginDocument{" + overrides + "}"
            pre = setup() + base + overrides
        add("cleveref-overrides-" + variant, pre, reference_body)
    paragraph_body = (FIXTURES / "paragraph-typography.tex").read_text(encoding="utf-8")
    for language in ("bangla", "assamese"):
        for suffix in ("kalpurush", "solaimanlipi", "noto-serif"):
            add(
                "paragraph-" + language + "-" + suffix,
                setup("language=" + language, font=BENGALI_FONTS[suffix])
                + r"\usepackage[margin=20mm]{geometry}",
                paragraph_body,
                passes=1,
            )
    protrusion_body = (FIXTURES / "microtype.tex").read_text(encoding="utf-8")
    # Save the actual Latin font before automatic switching starts. Between
    # text runs the selected font may be Bengali; its protrusion is unrelated.
    protrusion_font = r"""\newfontfamily\protrusionfont{TeX Gyre Pagella}
\AtBeginDocument{\begingroup\protrusionfont
\global\expandafter\let\expandafter\protrusiontestfont\the\font\endgroup}
"""
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
    natbib_fixture = (FIXTURES / "natbib-localization.tex").read_text(encoding="utf-8")
    for style in ("plainnatbn", "abbrvnatbn", "unsrtnatbn"):
        for language in ("bangla", "assamese", "english"):
            for mode in ("numbers", "authoryear"):
                add(
                    f"natbib-{style}-{language}-{mode}",
                    setup("language=" + ("assamese" if language == "assamese" else "bangla"))
                    + r"\setotherlanguage{english}"
                    + r"\usepackage[" + mode + r",sort&compress]{natbib}\usepackage{hyperref}"
                    + natbib_fixture,
                    (r"\selectlanguage{english}" if language == "english" else "")
                    + r"\citet{samea,sameb}; \citep{native}; \citeauthor{native}; \citeyear{samea}."
                    + r"\nocite{*}\bibliographystyle{" + style + r"}\bibliography{native-natbib}",
                    backend="bibtex",
                )

        # Compare English output with the upstream style, including abbreviated
        # names/months/journals, ordering and author-year disambiguation.
        for variant in (style, style.removesuffix("bn")):
            add(
                "natbib-english-baseline-" + variant,
                setup() + r"\setotherlanguage{english}"
                + r"\usepackage[authoryear]{natbib}\usepackage{hyperref}" + natbib_fixture,
                r"\selectlanguage{english}\citet{samea,sameb}; \citep{latin}."
                r"\nocite{editors,chapter,web,masters,doctorate,report}"
                r"\bibliographystyle{" + variant + r"}\bibliography{native-natbib}",
                backend="bibtex",
            )

    for language in ("bangla", "assamese", "english"):
        add(
            "natbib-edgecases-" + language,
            setup("language=" + ("assamese" if language == "assamese" else "bangla"))
            + r"\setotherlanguage{english}\usepackage[numbers]{natbib}\usepackage{hyperref}"
            + natbib_fixture,
            (r"\selectlanguage{english}" if language == "english" else "")
            + r"\nocite{electronic,singlepage,crosschapter,editors}"
            r"\bibliographystyle{plainnatbn}\bibliography{native-natbib}",
            backend="bibtex",
        )

    for mode in ("western", "first", "roundtrip"):
        add(
            "natbib-localized-" + mode,
            (r"\usepackage[authoryear]{natbib}" if mode == "first" else "")
            + setup("changecounternumbering=false" if mode == "western" else "")
            + r"\setotherlanguage{english}"
            + ("" if mode == "first" else r"\usepackage[" +
               ("numbers,sort&compress" if mode == "western" else "authoryear") + r"]{natbib}")
            + r"\usepackage{hyperref}" + natbib_fixture,
            r"\citet{samea,sameb}; \citep{native}."
            + (r"\begin{english}\citet{samea,sameb}; \citeyear{native}.\end{english}"
               r"\citet{samea,sameb}; \citeyear{native}." if mode == "roundtrip" else "")
            + r"\nocite{*}\bibliographystyle{plainnatbn}\bibliography{native-natbib}",
            backend="bibtex",
        )

    add(
        "natbib-localized-custom-punctuation",
        r"\makeatletter\newcommand\bibstyle@plainnatbn{\bibpunct{(}{)}{;}{a}{,}{,}}\makeatother"
        + setup() + r"\usepackage{natbib}\usepackage{hyperref}" + natbib_fixture,
        r"\citep{samea,sameb}\bibliographystyle{plainnatbn}\bibliography{native-natbib}",
        backend="bibtex",
    )

    # The same input digits must survive both backends and explicit English
    # output. Native data is normalized only for backend parsing/sorting.
    def input_script_data(backend):
        filename = ("bibliography" if backend == "biber" else "natbib") + "-input-scripts.bib"
        return (r"\begin{filecontents*}{input-scripts.bib}" + "\n"
                + (FIXTURES / filename).read_text(encoding="utf-8")
                + "\n" + r"\end{filecontents*}" + "\n")

    for language in ("bangla", "assamese", "english"):
        base = setup("language=" + ("assamese" if language == "assamese" else "bangla"))
        base += r"\setotherlanguage{english}"
        for dates in ("long", "short"):
            add(
                f"input-script-biber-{language}-{dates}",
                base + r"\usepackage[backend=biber,style=authoryear,date=" + dates
                + (",language=english,autolang=other" if language == "english" else "")
                + r"]{biblatex}" + input_script_data("biber")
                + r"\addbibresource{input-scripts.bib}\usepackage{hyperref}",
                r"\cite{samewestern,samenative,inherited,overridden}"
                r"\nocite{*}\printbibliography", backend="biber",
            )
        for style in ("plainnatbn", "abbrvnatbn", "unsrtnatbn"):
            add(
                f"input-script-natbib-{language}-{style}",
                base + r"\usepackage[authoryear,sort]{natbib}\usepackage{hyperref}"
                + input_script_data("bibtex"),
                (r"\selectlanguage{english}" if language == "english" else "")
                + r"\citep{later,samenative,earlier,samewestern}; "
                r"\citet{groupa,groupb,groupc}; \citep{westgroupa,westgroupb}; "
                r"\citeyearpar{groupa,groupb,groupc}.\nocite{*}"
                r"\bibliographystyle{" + style + r"}\bibliography{input-scripts}",
                backend="bibtex",
            )
    for mode in ("native", "western"):
        add(
            "input-script-natbib-numbers-" + mode,
            setup("changecounternumbering=" + ("true" if mode == "native" else "false"))
            + r"\usepackage[numbers,sort&compress]{natbib}\usepackage{hyperref}"
            + input_script_data("bibtex"),
            r"\citep{groupa,groupb,groupc}; \citeyearpar{groupa,groupb}."
            r"\nocite{*}\bibliographystyle{plainnatbn}\bibliography{input-scripts}",
            backend="bibtex",
        )

    add(
        "input-script-biber-custom-format",
        setup() + r"\setotherlanguage{english}"
        r"\usepackage[backend=biber,style=numeric,language=english,autolang=other]{biblatex}"
        + input_script_data("biber") + r"\addbibresource{input-scripts.bib}"
        r"\DeclareFieldFormat[article]{volume}{VOL:#1}"
        r"\DeclareFieldFormat[article]{number}{NO:#1}"
        r"\DeclareFieldFormat{pages}{PAGES:#1}"
        r"\DeclareFieldFormat{pagetotal}{TOTAL:#1}",
        r"\nocite{range,native}\printbibliography", backend="biber",
    )

    bibliography_fixture = (FIXTURES / "bibliography-localization.tex").read_text(encoding="utf-8")
    for language in ("bangla", "assamese"):
        for style in ("numeric", "numeric-comp", "alphabetic", "authoryear", "authoryear-comp", "verbose"):
            add(
                f"bibliography-{language}-{style}",
                setup("language=" + language)
                + r"\usepackage[backend=biber,style=" + style
                + r",maxbibnames=3,maxcitenames=2,date=long,urldate=long]{biblatex}"
                + bibliography_fixture + r"\usepackage{hyperref}",
                r"\cite{many}\nocite{*}\printbibliography", backend="biber",
            )
        for option in ("western", "english", "short-dates", "roundtrip", "english-option"):
            add(
                f"bibliography-{language}-{option}",
                setup("language=" + language + ",changecounternumbering=false")
                + r"\setotherlanguage{english}"
                + r"\usepackage[backend=biber,style=numeric,date="
                + ("short,urldate=short" if option == "short-dates" else "long,urldate=long")
                + (",language=english,autolang=other" if option == "english-option" else "")
                + r"]{biblatex}"
                + bibliography_fixture + r"\usepackage{hyperref}",
                r"\nocite{*}"
                + (r"\begin{english}\cite{many}\printbibliography\end{english}"
                   if option == "english" else
                   r"\printbibliography\clearpage\begin{english}\printbibliography\end{english}"
                   r"\clearpage\printbibliography" if option == "roundtrip" else
                   r"\cite{many}\printbibliography"),
                backend="biber",
            )

    add(
        "bibliography-date-ranges",
        setup("changecounternumbering=false")
        + r"\usepackage[backend=biber,style=authoryear,date=short,datezeros=false]{biblatex}"
        + r"""
\begin{filecontents*}{date-ranges.bib}
@book{range, author={Alice Author}, title={Title 1984}, date={2020-03-01/2021-04-02},
 edition={Revised}, volume={IV}, pages={xii-xiv}, publisher={Press 123}}
@book{same1, author={Bob Writer}, title={First}, date={2023}}
@book{same2, author={Bob Writer}, title={Second}, date={2023}}
\end{filecontents*}
\addbibresource{date-ranges.bib}
\usepackage{hyperref}
""",
        r"\cite{same1,same2}\nocite{*}\printbibliography", backend="biber",
    )
    for language in ("bangla", "assamese"):
        for date_format in ("comp", "terse"):
            add(
                f"bibliography-{language}-{date_format}-ranges",
                setup("language=" + language) + r"\setotherlanguage{english}"
                + r"\usepackage[backend=biber,style=authoryear,date=" + date_format
                + r",eventdate=" + date_format + r"]{biblatex}"
                + r"""
\begin{filecontents*}{compact-dates.bib}
@inproceedings{conference, author={Alice Author}, title={Conference Paper},
 booktitle={Proceedings}, eventtitle={Conference},
 date={2023-06-15/2023-06-17}, eventdate={2023-06-15/2023-06-17}}
\end{filecontents*}
\addbibresource{compact-dates.bib}
""",
                r"\nocite{*}\printbibliography\clearpage"
                r"\begin{english}\printbibliography\end{english}\clearpage\printbibliography",
                backend="biber",
            )
    add(
        "bibliography-mixed-languages",
        setup()
        + r"\setotherlanguage{english}"
        + r"\usepackage[backend=biber,style=numeric,autolang=other]{biblatex}"
        + r"""
\begin{filecontents*}{mixed-references.bib}
@book{native, author={Alice Author and Bob Writer}, title={Native Entry},
 date={2023}, edition={2}, langid={bengali}}
@book{english, author={Alice Author and Bob Writer}, title={English Entry},
 date={2023}, edition={2}, langid={english}}
\end{filecontents*}
\addbibresource{mixed-references.bib}
\usepackage{hyperref}
""",
        r"\cite{native,english}\printbibliography", backend="biber",
    )
    add(
        "biblatex-english-native-labels",
        r"\usepackage{latexbangla}\setbanglamainfont{Kalpurush}"
        r"\setotherlanguage{english}"
        r"\usepackage[backend=biber,style=numeric]{biblatex}"
        r"\addbibresource{references.bib}\usepackage{hyperref}",
        r"\begin{english}\cite{alpha}\printbibliography\end{english}",
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
    bibliography_preamble = manual_source.split(
        r"\subsection{Bibliographies and citations}", 1
    )[1].split(r"\begin{code}", 1)[1].split(r"\end{code}", 1)[0]
    for language in ("bangla", "assamese"):
        bibliography_data = manual_source.split(
            r"\begin{VerbatimOut}{\jobname-" + language + ".bib}", 1
        )[1].split(r"\end{VerbatimOut}", 1)[0]
        add(
            "manual-" + language + "-bibliography",
            bibliography_preamble.replace("references.bib", "manual-references.bib").replace(r"\usepackage{latexbangla}",
                r"\usepackage[language=" + language + r"]{latexbangla}")
            + r"\begin{filecontents*}{manual-references.bib}" + bibliography_data
            + r"\end{filecontents*}",
            r"\cite{book,article}\printbibliography", backend="biber",
        )
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
    for language in ("bangla", "assamese"):
        bibliography_data = (ROOT / f"natbib/natbib-{language}.bib").read_text(encoding="utf-8")
        manual_data = manual_source.split(
            r"\begin{VerbatimOut}{\jobname-natbib-" + language + ".bib}", 1
        )[1].split(r"\end{VerbatimOut}", 1)[0]
        assert bibliography_data.strip() == manual_data.strip(), (
            f"The manual's {language} natbib source differs from its test fixture."
        )
        data[f"manual-natbib-{language}"] = dict(
            tex=r"\def\previewlanguage{" + language + "}\n"
                + r"\begin{filecontents*}{manual-natbib.bib}" + "\n"
                + bibliography_data + r"\end{filecontents*}" + "\n"
                + (ROOT / "natbib/natbib-preview.tex").read_text(encoding="utf-8"),
            passes=3, backend="bibtex", expect_error=None,
            restricted_shell_escape=True,
        )
    data["manual"] = dict(
        tex=manual_source.replace(
            r"\phantomsection\label{manual:assamese}",
            r"""\ExplSyntaxOn
\int_step_inline:nn {37}
  {\iow_term:x {MANUAL-AS-ALPHABET-#1=[\use:c {@alph}{#1}/\use:c {@Alph}{#1}]}}
\ExplSyntaxOff
\phantomsection\label{manual:assamese}""",
        ),
        passes=3,
        backend="biber",
        expect_error=None,
        restricted_shell_escape=True,
    )
    # Exercise the translated examples under the actual package option, without
    # the combined manual's local language/font/numbering setup.
    assamese_guide = manual_source.split(r"\label{manual:assamese}", 1)[1]
    assamese_examples = re.findall(
        r"\\begin\{examplepair\}(.*?)\\end\{examplepair\}", assamese_guide, re.S
    )
    assamese_documents = [
        block for block in re.findall(
            r"\\begin\{code\}(.*?)\\end\{code\}", assamese_guide, re.S
        ) if r"\documentclass" in block
    ]
    data["manual-assamese-opening"] = dict(
        tex=assamese_documents[0].split(r"\begin{document}", 1)[0]
        + "\\begin{document}\n" + assamese_examples[0] + "\n\\end{document}\n",
        passes=1, backend=None, expect_error=None,
    )
    data["manual-assamese-fontspec"] = dict(
        tex=assamese_documents[1], passes=1, backend=None, expect_error=None,
    )
    add(
        "manual-assamese-examples",
        setup("language=assamese") + r"""
\setbanglasansfont{Noto Sans Bengali}
\setbanglamonofont{Siyam Rupali}
\usepackage{amsmath,amsthm,hyperref,alphalph}
\newtheorem{assamesetheorem}{উপপাদ্য}
\providecommand{\assamesetheoremautorefname}{উপপাদ্য}
\makeatletter
\newalphalph{\extendedAssamese}{\@alph}{37}
\makeatother
""",
        "\n\\par\n".join("\\begingroup\n" + body + "\n\\endgroup" for body in assamese_examples),
    )
    data["bangla-example"] = dict(
        tex=(REPO / "examples/bangla.tex").read_text(encoding="utf-8"), passes=3, backend=None, expect_error=None
    )
    data["supported-fonts"] = dict(
        tex=(REPO / "examples/supported-fonts.tex").read_text(encoding="utf-8"),
        passes=2,
        backend=None,
        expect_error=None,
    )
    # Compile the exact README snippet; verify.py renders its preview for refreshing the README.
    readme_source = (REPO / "README.md").read_text(encoding="utf-8")
    readme_examples = re.findall(r"```latex\n(.*?)\n```", readme_source, re.S)
    data["readme-example"] = dict(tex=readme_examples[0], passes=1, backend=None, expect_error=None)
    data["readme-font-families"] = dict(
        tex=readme_examples[1], passes=1, backend=None, expect_error=None,
    )
    # graphicx loads epstopdf on LuaTeX. Use TeX Live's normal restricted shell
    # policy for these graphics examples, as for the minted manual.
    for name in ("common-math", "common-layout", "common-boxes"):
        data[name]["restricted_shell_escape"] = True

    # Exercise shared integrations with the other document language without
    # maintaining a second copy of their test documents.
    for source in (
        "signed-counters", "footnotes-symbol", "footnotes-roman",
        "common-cleveref", "common-cleveref-off", "common-cleveref-first",
        "common-cleveref-no-hyperref", "cleveref-overrides-before",
        "cleveref-overrides-after", "cleveref-overrides-begin",
        "common-tables", "common-layout", "common-boxes", "math",
        "unicode-math-pagella", "hyperref-first",
        "citations-standard", "citations-natbib", "citations-biblatex",
        "citations-biblatex-off", "biblatex-preloaded",
    ):
        case = dict(data[source])
        case["tex"] = re.sub(
            r"\\usepackage(?:\[([^\]]*)\])?\{latexbangla\}",
            lambda match: r"\usepackage[language=assamese,"
            + (match[1] or "") + r"]{latexbangla}", case["tex"], count=1,
        )
        data["assamese-" + source] = case
    for suffix, font in BENGALI_FONTS.items():
        add("assamese-font-" + suffix, setup("language=assamese", font),
            ASSAMESE_FONT_FACE_BODY
            + r"\par অসমীয়া ৰ ৱ প্ৰ শ্ৰ ৰ্ক ৰু ৰূ ৱা। $১২+x^২$",
            passes=1)
    add("assamese-direct-font",
        r"\usepackage{polyglossia}\newfontfamily\assamesefont[Script=Bengali]{Noto Serif Bengali}"
        r"\usepackage[language=assamese]{latexbangla}", r"অসমীয়া ৰ ৱ।", passes=1)
    add("assamese-font-overrides", setup("language=assamese", "Noto Serif Bengali")
        + r"\setbanglamainfont[Scale=0.95,AutoFakeBold=4,AutoFakeSlant=0.1]{Mukti}",
        ASSAMESE_FONT_FACE_BODY, passes=1)
    add("assamese-missing-font", r"\usepackage[language=assamese]{latexbangla}",
        "অসমীয়া", error="No Bangla main font")
    add("assamese-wrong-font", setup("language=assamese", "TeX Gyre Pagella"),
        "অসমীয়া", error="required Assamese letters")
    add("invalid-language", r"\usepackage[language=unknown]{latexbangla}",
        "Test", error="accepts only a fixed set of choices")
    add("assamese-overflow", setup("language=assamese", "Noto Serif Bengali"),
        r"\newcounter{large}\setcounter{large}{38}\alph{large}", error="Counter too large")
    data["assamese-example"] = dict(
        tex=(REPO / "examples/assamese.tex").read_text(encoding="utf-8"),
        passes=3, backend=None, expect_error=None,
    )
    return data
