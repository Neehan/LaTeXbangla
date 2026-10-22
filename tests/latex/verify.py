#!/usr/bin/env python3
"""Check rendered behavior as well as TeX exit codes.

Run on the host with PyMuPDF and pypdf. Outputs are disposable build artifacts.
Ligatures can extract as decomposed Bengali text, so assertions use stable
numeric labels, Latin marker words, font metadata and auxiliary-file records.
"""
import argparse
import json
import math
from pathlib import Path
import re
from typing import cast

import fitz
from pypdf import PdfReader
from pypdf.generic import ContentStream, DictionaryObject
from cases import cases, BENGALI_FONTS, REPO

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--engine", choices=("xelatex", "lualatex"), default="xelatex")
ENGINE = parser.parse_args().engine
BUILD = Path(__file__).resolve().parent / "build" / ENGINE
RESULTS_PATH = BUILD / "results.json"
if not RESULTS_PATH.exists():
    raise SystemExit("No test results found. Run sh tests/latex/run.sh first.")
RESULTS = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
CHECKS = []
PDFS = {}


def check(condition, description):
    CHECKS.append(dict(passed=bool(condition), description=description))


def inspect(name):
    directory = BUILD / name
    document = fitz.open(directory / "main.pdf")
    spans, links, targets = [], [], []
    for page in document:
        for block in page.get_textpage().extractDICT()["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    spans.append({key: span[key] for key in ("text", "font", "size", "bbox")})
        links.extend(
            {key: value for key, value in link.items() if key != "from"}
            for link in page.get_links()
        )
    reader = PdfReader(directory / "main.pdf")
    for page in reader.pages:
        for reference in page.get("/Annots", []):
            annotation = reference.get_object()
            action = annotation.get("/A", {})
            destination = action.get("/D", annotation.get("/Dest"))
            if isinstance(destination, str):
                targets.append(destination)
    info = dict(
        text="\n\f\n".join(page.get_textpage().extractText() for page in document),
        pages=len(document),
        spans=spans,
        links=links,
        bookmarks=document.get_toc(),
        targets=targets,
        destinations=list(reader.named_destinations),
    )
    (directory / "text.txt").write_text(info["text"], encoding="utf-8")
    (directory / "pdf-info.json").write_text(
        json.dumps(info, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8"
    )
    if name.startswith("font-") or name in {
        "one-font",
        "real-faces",
        "math",
        "unicode-math-pagella",
        "all-digits",
        "nested-bullets",
        "structures",
        "citations-standard",
        "citations-natbib",
        "citations-biblatex",
        "manual",
    }:
        document[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(directory / "page-1.png")
    if name == "memoir":
        document[8].get_pixmap(matrix=fitz.Matrix(1.5, 1.5)).save(directory / "page-9.png")
    if name == "readme-example":
        # Crop the short lesson to its text, leaving the page footer out of the
        # README illustration. Keep the generated preview in build/ for review
        # before copying it to the versioned image.
        page = document[0]
        content = [block for block in page.get_text("blocks") if block[3] < page.rect.height * 0.8]
        bounds = fitz.Rect(content[0][:4])
        for block in content[1:]:
            bounds |= fitz.Rect(block[:4])
        bounds += (-14, -14, 14, 14)
        page.get_pixmap(matrix=fitz.Matrix(2, 2), clip=bounds).save(directory / "preview.png")
    return info


for name, case in cases().items():
    result = RESULTS.get(name)
    check(result is not None, f"{name}: result recorded")
    if result is None:
        continue
    if case["expect_error"]:
        check(
            any(result["exitcodes"]) and result["expected_error_seen"],
            f"{name}: intended diagnostic, not an unrelated failure",
        )
        continue
    check(
        len(result["exitcodes"]) == case["passes"]
        and not any(result["exitcodes"])
        and result["pdf"]
        and (BUILD / name / "main.pdf").exists(),
        f"{name}: every compilation pass completed and PDF exists",
    )
    check(result["missing_glyph_count"] == 0, f"{name}: no missing glyphs")
    check(not result["warnings"], f"{name}: no final package/font/reference warnings")
    if (BUILD / name / "main.pdf").exists():
        PDFS[name] = inspect(name)
        check(
            all(
                0 <= link["page"] < PDFS[name]["pages"]
                for link in PDFS[name]["links"]
                if link.get("kind") == 1
            ),
            f"{name}: internal links have valid page destinations",
        )
        check(
            all(target in PDFS[name]["destinations"] for target in PDFS[name]["targets"]),
            f"{name}: named link targets resolve",
        )


def text(name):
    return PDFS.get(name, {}).get("text", "")


def spans(name):
    return PDFS.get(name, {}).get("spans", [])


def aux(name):
    return (BUILD / name / "main.aux").read_text(encoding="utf-8")


for token, family in [
    ("EnglishRoman", "TeXGyrePagella-Regular"),
    ("EnglishBold", "TeXGyrePagella-Bold"),
    ("EnglishItalic", "TeXGyrePagella-Italic"),
    ("EnglishSans", "TeXGyreHeros-Regular"),
    ("EnglishMono", "TeXGyreCursor-Regular"),
    ("SansBold", "TeXGyreHeros-Bold"),
    ("MonoBold", "TeXGyreCursor-Bold"),
]:
    check(
        any(token in span["text"] and span["font"] == family for span in spans("one-font")),
        f"Mixed text: {token} uses {family}",
    )
check(
    any(
        "EnglishRoman" in span["text"] and span["font"] == "TeXGyreTermes-Regular"
        for span in spans("font-overrides")
    ),
    "Later English-font override takes effect",
)
check(
    any(
        "EnglishRoman" in span["text"] and span["font"].startswith("LMRoman")
        for span in spans("default-english")
    ),
    "Unconfigured English font retains Latin Modern",
)
check(
    any(
        "বাংলা" in span["text"] and span["font"] == "FreeSerifItalic"
        for span in spans("real-faces")
    ),
    "Usable real Bengali italic face is retained",
)
check(
    not any("FreeSerifBold" in span["font"] for span in spans("real-faces")),
    "Bold faces lacking Bengali are not used for Bangla text",
)
for name in ("dynamic-fallbacks", "retained-override"):
    check(
        not any(span["font"] == "Kalpurush" for span in spans(name))
        and any("FreeSerif" in span["font"] for span in spans(name)),
        f"{name}: unconfigured roles follow the replacement main font",
    )
check(
    any(span["font"] == "Kalpurush" for span in spans("font-overrides"))
    and any("FreeSans" in span["font"] for span in spans("font-overrides")),
    "Explicit Bangla mono and sans roles remain independent",
)
check(
    "(ক)" in text("structures") and "(খ)" in text("structures"),
    "Nested alphabetic lists are Bengali",
)
check("(a)" in text("structures-off"), "Disabling numbering retains Latin alphabetic lists")
check(
    "Custom counter: ১২;" in text("structures") and "Custom counter: 12;" in text("structures-off"),
    "User-defined decimal counter follows the single numbering option",
)
check(
    "(২ক)" in text("structures") and "(২খ)" in text("structures"),
    "Subequations retain their parent/letter structure",
)
for name in ("nested-bullets", "aliased-bullet", "enumitem-bullet", "text-symbols"):
    check("•" in text(name), f"{name}: a missing Bengali bullet uses a visible fallback")
for symbol in "–∗·":
    check(symbol in text("text-symbols"), f"Text-symbol fallback renders {symbol}")
for token, family in (
    ("BoldStart", "TeXGyrePagella-Bold"),
    ("BoldEnd", "TeXGyrePagella-Bold"),
    ("SansStart", "TeXGyreHeros-Regular"),
    ("SansRestored", "TeXGyreHeros-Regular"),
    ("MonoNested", "TeXGyreCursor-Regular"),
    ("MonoStart", "TeXGyreCursor-Regular"),
    ("RomanRestored", "TeXGyrePagella-Regular"),
    ("NormalInside", "TeXGyrePagella-Regular"),
    ("SansOuterEnd", "TeXGyreHeros-Regular"),
):
    check(
        any(
            token in span["text"] and span["font"] == family
            for span in spans("english-first-families")
        ),
        f"English-first and nested families: {token} uses {family}",
    )
check("*" in text("custom-labels"), "Custom item marker survives")
check("Zero=[]." in text("alphabet"), "Alphabetic zero matches LaTeX's empty label")
alphabet_log = (BUILD / "alphabet/main.log").read_text(encoding="utf-8")
for number, letter in enumerate("কখগঘঙচছজঝঞটঠডঢণতথদধনপফবভমযরলশষসহড়ঢ়য়ৎ", 1):
    check(letter in text("alphabet"), f"Alphabet inventory renders {letter}")
    check(
        f"ALPHABET-{number}=[{letter}/{letter}]" in alphabet_log,
        f"Alphabet position {number} expands to {letter} for both formatters",
    )
for name in ("alphalph-before", "alphalph-after"):
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    check("Latin: aa, AA." in text(name), f"{name}: built-in Latin formatters are preserved")
    for value, label in (
        (1, "ক"), (36, "ৎ"), (37, "কক"), (38, "কখ"),
        (72, "কৎ"), (73, "খক"), (1332, "ৎৎ"), (1333, "ককক"),
    ):
        check(f"EXTENDED-{value}=[{label}]" in log, f"{name}: {value} expands to {label}")
        check(label in text(name), f"{name}: {label} is rendered")
    check(
        r"\newlabel{extended-example}{{কক}" in aux(name),
        f"{name}: custom counter reference retains the extended label",
    )
    check("example.37" in PDFS[name]["targets"], f"{name}: reference links to the custom counter")
for name in ("common-cleveref", "common-cleveref-first", "common-cleveref-no-hyperref", "common-cleveref-off"):
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    check("CREF-SORT-KEY: 11" in log, f"{name}: sorting receives Western integer values")
    check("CREF-PAGE-KEY: 2" in log, f"{name}: page sorting receives Western integer values")
    western = name.endswith("-off")
    nine, ten, eleven = ("9", "10", "11") if western else ("৯", "১০", "১১")
    flattened = re.sub(r"\s+", "", text(name))
    for start, end in (("Sorted:", "Range:"), ("Range:", "Theorem:")):
        rendered_range = flattened.split(start)[1].split(end)[0]
        check(
            f"({nine})" in rendered_range and f"({eleven})" in rendered_range
            and rendered_range.index(f"({nine})") < rendered_range.index(f"({eleven})")
            and f"({ten})" not in rendered_range,
            f"{name}: {start} displays an ordered, compressed range in the selected script",
        )
    page_reference = flattened.split("Pages:")[1].split(".")[0]
    check(
        re.findall(r"[0-9০-৯]+", page_reference) == (["1", "2"] if western else ["১", "২"]),
        f"{name}: page references sort numerically while preserving the displayed script",
    )
    check(
        (r"\newlabel{thm:appendix}{{A.1}" if western else r"\newlabel{thm:appendix}{{ক.১}") in aux(name),
        f"{name}: appendix theorem retains its compound label",
    )


def protrusion_codes(name):
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    return dict(re.findall(r"PROTRUSION-([A-Z]+): (\d+)", log))


baseline_protrusion = protrusion_codes("microtype-baseline")
check(
    baseline_protrusion.get("MODE") == "2"
    and all(int(baseline_protrusion.get(key, "0")) > 0 for key in ("PERIOD", "ENDASH", "ACCENT")),
    "Plain fontspec baseline has active, nonzero punctuation and accent protrusion",
)
for suffix in (*BENGALI_FONTS, "first"):
    name = "microtype-" + suffix
    check(protrusion_codes(name) == baseline_protrusion, f"{name}: English protrusion matches fontspec")
    check("EnglishRoman" in text(name), f"{name}: mixed-script specimen renders")

check("Equation (১); theorem ১." in text("common-math"), "Common math packages retain localized references")
with fitz.open(BUILD / "common-math/main.pdf") as math_document:
    check(
        any(
            span["type"] == 1 and span["font"] == "Kalpurush"
            and "".join(chr(char[0]) for char in span["chars"]) == "১২"
            for span in math_document[0].get_texttrace()
        ),
        "The bm package applies the Bengali font's bold fallback to math digits",
    )
check(
    all(token in text("common-tables") for token in ("12.5", "3.0", "Table ১.", "Long table ২.", "12, ১২")),
    "Common table packages preserve numeric data, literal scripts and Bangla table references",
)
check(
    all(token in text("common-layout") for token in ("Section ১;", "figure ১;", "parts ক, খ."))
    and PDFS["common-layout"]["pages"] == 2,
    "Caption/subcaption and heading packages retain Bangla references across two pages",
)
check(
    all(token in text("common-boxes") for token in ("Exercise ১.", "(ক)", "(খ)", "১২")),
    "Tcolorbox theorem and enumitem labels retain Bengali numbers and letters",
)
for name in ("book", "memoir", "report", "hyperref-first"):
    check(
        r"\newlabel{app:book}{{ক}" in aux(name),
        f"{name}: appendix reference stores Bengali alphabetic number",
    )
    # report has no mainmatter transition: its preceding introduction remains
    # chapter 1, so the next chapter must be 2. Preserve that class behavior.
    chapter_number = "২" if name == "report" else "১"
    check(
        r"\newlabel{ch:test}{{" + chapter_number + "}" in aux(name),
        f"{name}: chapter reference preserves the class's counter sequence",
    )
    check(
        any(bookmark[1] == "অতিরিক্ত" for bookmark in PDFS.get(name, {}).get("bookmarks", [])),
        f"{name}: Bangla bookmark survives",
    )
for name in ("converters", "converters-off"):
    check(
        all(
            fragment in text(name)
            for fragment in (
                "Counter: ১২",
                "Number: ১২৩",
                "Negative: -১২",
                "Zero: ০",
                "Leading: ০০১২",
                "১২৩৪৫৬৭৮৯০১২৩৪৫৬৭৮৯০",
            )
        ),
        f"{name}: explicit converters preserve leading zeroes and handle signed counters",
    )
    check(
        any("১২৩" in bookmark[1] for bookmark in PDFS.get(name, {}).get("bookmarks", [])),
        f"{name}: explicit converter expands safely in PDF bookmarks",
    )
check(
    text("all-digits").count("0123456789") >= 2 and text("all-digits").count("০১২৩৪৫৬৭৮৯") >= 2,
    "All ten literal Western and Bengali digits survive in both prose and math",
)
for name in (
    "math",
    "math-off",
    "unicode-math-pagella",
    "unicode-math-lm",
    "unicode-math-first",
    "newtxmath",
):
    sizes = {
        round(span["size"], 1)
        for span in spans(name)
        if any(char in "০১২৩৪৫৬৭৮৯" for char in span["text"]) and span["size"] < 13
    }
    check(len(sizes) >= 3, f"{name}: Bengali digits use text/script/scriptscript sizes")
    check("12" in text(name) and "১২" in text(name), f"{name}: authored digit scripts both survive")
for name in ("citations-standard", "citations-no-hyperref"):
    check(
        "[৩, ১, ২]" in text(name) and "[১]" in text(name),
        f"{name}: citation and bibliography labels agree",
    )
for name in ("citations-natbib", "natbib-first", "citations-biblatex", "biblatex-preloaded"):
    check("[১–৩]" in text(name), f"{name}: numeric range compression remains correct")
for name in ("citations-standard-off", "citations-natbib-off", "citations-biblatex-off"):
    check(
        "[1]" in text(name) and "[১]" not in text(name),
        f"{name}: disabled conversion includes citation labels",
    )
for name in ("citations-standard", "citations-natbib", "citations-biblatex"):
    check(
        "2020" in text(name) and "12–14" in text(name),
        f"{name}: authored years and citation notes stay Western",
    )
    check(bool(PDFS.get(name, {}).get("targets")), f"{name}: citation hyperlinks exist")
check(
    text("citations-text-label").count("[Knuth84]") == 2,
    "Textual bibliography labels are unchanged",
)
check(
    sum(
        "Knuth84" in span["text"] and span["font"] == "TeXGyrePagella-Bold"
        for span in spans("citations-styled-label")
    )
    == 2,
    "Explicit textual labels retain bold formatting in citation and bibliography",
)
check(
    text("citations-numeric-label").count("[১২]") == 2,
    "Explicit numeric citation and bibliography labels agree",
)
check(
    "(১)" in text("natbib-custom-style") and "(১)" in text("biblatex-custom-style"),
    "Citation adapters preserve the author's bibliography brackets",
)
for name in ("natbib-author-year", "biblatex-author-year"):
    check(
        "2020" in text(name) and "২০২০" not in text(name),
        f"{name}: author-year data remains unchanged",
    )
check(
    PDFS.get("citations-standard", {}).get("targets", [])[:3]
    == ["cite.gamma", "cite.alpha", "cite.beta"],
    "Standard citation links retain the original citation keys and order",
)
check(
    PDFS.get("long-mixed", {}).get("pages", 0) >= 10,
    "Representative long mixed document was produced",
)
check("12.5" in text("siunitx"), "siunitx keeps standard Western numeric input")
check(
    "English code 12;" in text("verbatim") and "https://example.org/a12" in text("verbatim"),
    "Verbatim content and URL digits survive",
)

# Each supported Bengali family must stand on its own, including sans/mono
# fallback, text faces, formula digits, lists, tables and citation labels.
for suffix, family in BENGALI_FONTS.items():
    font_prefix = family.replace(" ", "")
    for ending in ("", "-unicode"):
        name = "font-" + suffix + ending
        check(
            any(span["font"].startswith(font_prefix) for span in spans(name)),
            f"{name}: requested Bengali family is embedded",
        )
        check(
            all(
                token in text(name)
                for token in (
                    "Decimal: ১২",
                    "Literal: 12 ১২",
                    "Alphabetic: গ",
                    "(ক)",
                    "[১]",
                    "2020",
                )
            ),
            f"{name}: counters, authored digits, lists and citations retain their semantics",
        )
        sizes = {
            round(span["size"], 1)
            for span in spans(name)
            if span["font"].startswith(font_prefix)
            and any(char in "০১২৩৪৫৬৭৮৯" for char in span["text"])
            and span["size"] < 13
        }
        check(len(sizes) >= 3, f"{name}: Bengali math digits scale through nested scripts")
        for token, english_family in (
            ("EnglishRoman", "TeXGyrePagella-Regular"),
            ("EnglishSans", "TeXGyreHeros-Regular"),
            ("EnglishMono", "TeXGyreCursor-Regular"),
        ):
            check(
                any(
                    token in span["text"] and span["font"] == english_family for span in spans(name)
                ),
                f"{name}: {token} keeps its configured English family",
            )
        if suffix.startswith("noto-"):
            check(
                any(
                    "বাংলা" in span["text"] and span["font"] == font_prefix + "-Bold"
                    for span in spans(name)
                ),
                f"{name}: genuine Noto bold face is retained",
            )
check(
    any(span["font"].startswith("NotoSerifBengali") for span in spans("font-noto-roles"))
    and any(span["font"].startswith("NotoSansBengali") for span in spans("font-noto-roles")),
    "Noto Serif main and Noto Sans sans-serif roles coexist",
)

check(
    "X12" in text("author-numbering-off") and "Y12" in text("author-numbering-off"),
    "Disabling conversion preserves author-defined decimal and alphabetic formatters",
)
for enabled in (True, False):
    name = "signed-counters" + ("" if enabled else "-off")
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    for value in (-2147483647, -12, 0, 12, 2147483647):
        expected = str(value)
        if enabled:
            expected = expected.translate(str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯"))
        check(f"SIGNED-{value}: {expected}" in log, f"{name}: signed counter {value}")
for style, definition in (
    ("symbol", r"\fnsymbol {footnote}"),
    ("roman", r"\roman {footnote}"),
    ("hook", r"F\arabic {footnote}"),
):
    log = (BUILD / ("footnotes-" + style) / "main.log").read_text(encoding="utf-8")
    check(
        "FOOTNOTE-FORMAT: macro:->" + definition in log,
        f"Footnote format {style} survives language activation",
    )
check(
    all(text("footnotes-symbol").count(symbol) >= 2 for symbol in "†‡‖"),
    "Symbolic footnote marks render in both the body and footnote text",
)
switch_log = (BUILD / "numbering-language-switch/main.log").read_text(encoding="utf-8")
# Polyglossia's main language owns global counter formatting. Selecting an
# English passage changes its language, not the document's numbering policy.
check(
    "ENGLISH-COUNTER: -১২" in switch_log
    and "BENGALI-COUNTER: -১২" in switch_log
    and r"SWITCH-FOOTNOTE: macro:->\roman {footnote}" in switch_log,
    "Language switches preserve footnote style and the document's signed counter formatting",
)
check(
    "CustomSection" in text("custom-autoref-before"), "Preexisting custom autoref name is preserved"
)
check(
    "EQUATION-NAME: সমীকরণ" in (BUILD / "custom-autoref-before/main.log").read_text(encoding="utf-8"),
    "Uncustomized autoref names are still translated",
)
for name in ("math", "unicode-math-lm", "newtxmath"):
    check(
        "MATH-SINGLE-TOKEN-WIDTH: equal" in (BUILD / name / "main.log").read_text(encoding="utf-8"),
        f"{name}: single-token Bengali math arguments match braced forms",
    )
for name in ("math-weight", "math-weight-unicode"):
    with fitz.open(BUILD / name / "main.pdf") as document:
        traces = [
            t
            for t in document[0].get_texttrace()
            if t["font"] == "Kalpurush" and "".join(chr(c[0]) for c in t["chars"]) == "১২"
        ]
        fills = [t for t in traces if t["type"] == 0]
        strokes = [t for t in traces if t["type"] == 1]
        check(
            len(fills) == 4
            and len(strokes) == 1
            and math.isclose(strokes[0]["bbox"][1], fills[2]["bbox"][1]),
            f"{name}: only boldmath makes Bengali math digits bold; textbf does not",
        )

# Check all three glue dimensions: natural width, stretch and shrink. The
# tolerance covers TeX's fixed-point rounding, not a visual spacing judgment.
for suffix in BENGALI_FONTS:
    for adjusted in (False, True):
        name = "spacing-" + suffix + ("-adjusted" if adjusted else "-default")
        log = (BUILD / name / "main.log").read_text(encoding="utf-8")
        dimensions = {}
        for label in ("NATIVE", "SELECTED"):
            match = re.search(label + r"-SPACING: ([\d.]+)pt,([\d.]+)pt,([\d.]+)pt", log)
            dimensions[label] = tuple(map(float, match.groups())) if match else ()
        factors = (
            (1.2, 1.3, 1.4) if adjusted else ((1.2,) * 3 if suffix == "siyam-rupali" else (1,) * 3)
        )
        scale = 0.8 if suffix == "siyam-rupali" else 1
        check(
            len(dimensions["NATIVE"]) == len(dimensions["SELECTED"]) == 3
            and all(
                math.isclose(actual, native * scale * factor, abs_tol=0.0001)
                for native, actual, factor in zip(
                    dimensions["NATIVE"], dimensions["SELECTED"], factors
                )
            ),
            f"{name}: default or explicit spacing is applied exactly once at the selected scale",
        )

# Font names alone do not establish an italic shape: the system can resolve
# Noto's bold-italic request to upright bold. Check the actual PDF text matrix.
# These plain-text specimens have no surrounding graphics transformations.
def rendered_slant_sizes(name, family, slant):
    reader = PdfReader(BUILD / name / "main.pdf")
    sizes = set()
    for page in reader.pages:
        resources = cast(DictionaryObject, page["/Resources"])
        font_resources = cast(DictionaryObject, resources["/Font"])
        fonts = {
            key: str(cast(DictionaryObject, value.get_object())["/BaseFont"])
            for key, value in font_resources.items()
        }
        current_font = ""
        current_font_size = 1
        matrix = [1, 0, 0, 1, 0, 0]
        for arguments, operator in ContentStream(page.get_contents(), reader).operations:
            if operator == b"Tf":
                current_font = fonts[arguments[0]]
                current_font_size = float(arguments[1])
            elif operator == b"Tm":
                matrix = list(map(float, arguments))
            elif operator in (b"TJ", b"Tj") and current_font.endswith(family):
                if matrix[0] and math.isclose(matrix[2] / matrix[0], slant, abs_tol=0.0001):
                    sizes.add(round(current_font_size * matrix[0], 2))
    return sizes


face_sample_sizes = {round(size * 72 / 72.27, 2) for size in (8, 11, 16)}
for suffix in ("noto-serif", "noto-sans"):
    name = "font-faces-" + suffix
    family = "NotoSerifBengali" if suffix == "noto-serif" else "NotoSansBengali"
    for weight in ("Regular", "Bold"):
        check(
            face_sample_sizes <= rendered_slant_sizes(name, family + "-" + weight, 0.2),
            f"{name}: {weight} italic has visible slant at footnote, body and heading sizes",
        )
    with fitz.open(BUILD / name / "main.pdf") as document:
        check(
            not any(t["type"] == 1 for page in document for t in page.get_texttrace()),
            f"{name}: genuine bold is not synthetically thickened",
        )
check(
    face_sample_sizes
    <= rendered_slant_sizes("font-slant-override", "NotoSerifBengali-Regular", 0.1)
    and face_sample_sizes
    <= rendered_slant_sizes("font-slant-override", "NotoSerifBengali-Bold", 0.15),
    "Explicit italic and bold-italic slant settings override the package defaults",
)

# Preamble boxes and local font overrides must retain their intended faces.
for marker, family in (
    ("PreambleBold", "TeXGyrePagella-Bold"),
    ("LocalEnglish", "TeXGyreAdventor-Regular"),
    ("OutsideEnglish", "TeXGyrePagella-Regular"),
):
    check(any(marker in span["text"] and span["font"] == family
              for span in spans("preamble-font-box")),
          f"Preamble/local font selection: {marker} uses {family}")

for name in ("switching-contexts", "switching-node-font"):
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    check(len(re.findall(r"FONT-PAIR-[a-z]+: equal", log)) == 15,
          f"{name}: all fifteen automatic/direct font width comparisons agree")

check(face_sample_sizes <= rendered_slant_sizes(
    "noto-file-faces", "NotoSerifBengali-Bold", 0.2),
    "Path-based Noto font loading honors the explicit bold-italic face and slant")
with fitz.open(BUILD / "noto-file-faces/main.pdf") as document:
    check(not any(t["type"] == 1 for page in document for t in page.get_texttrace()),
          "Path-based Noto faces do not receive synthetic bold")
with fitz.open(BUILD / "noto-bold-override/main.pdf") as document:
    strokes = [t for t in document[0].get_texttrace() if t["type"] == 1]
    check(len({round(t["chars"][0][2][1], 2) for t in strokes}) == 2
          and all(t["font"] == "NotoSerifBengali-Regular"
                  and math.isclose(t["linewidth"] / t["size"], 0.04, abs_tol=0.0002)
                  for t in strokes),
          "Explicit Noto AutoFakeBold=4 and AutoFakeSlant apply to both bold styles")

# Synthetic bold shares the regular face's font name. Inspect the actual PDF
# paint operations instead: bold and bold italic must add a 3.5% em stroke;
# the identical regular line must remain unstroked.
with fitz.open(BUILD / "synthetic-bold/main.pdf") as document:
    traces = [trace for trace in document[0].get_texttrace() if trace["font"] == "Kalpurush"]
    strokes = [trace for trace in traces if trace["type"] == 1]
    check(
        len({round(t["chars"][0][2][1], 2) for t in strokes}) == 2
        and all(math.isclose(t["linewidth"] / t["size"], 0.035, abs_tol=0.0002) for t in strokes),
        "Kalpurush bold and bold italic use the intended synthetic stroke strength",
    )
    check(
        bool(traces) and all(t["bbox"][1] > traces[0]["bbox"][1] for t in strokes),
        "Kalpurush regular text remains unstroked",
    )

for suffix in BENGALI_FONTS:
    name = "font-transitions-" + suffix
    check(
        "TRANSITION-GROUPS: balanced" in (BUILD / name / "main.log").read_text(encoding="utf-8"),
        f"{name}: punctuation and accented Latin runs leave balanced font groups",
    )
    check(
        all(mark in text(name) for mark in "—–‘’“”…"),
        f"{name}: Unicode dashes, curly quotes and ellipsis render",
    )
    check(
        any(
            "LatinAgain" in s["text"] and s["font"] == "TeXGyrePagella-Regular" for s in spans(name)
        )
        and "café" in text(name)
        and "Ānand" in text(name),
        f"{name}: nested formatting restores English and preserves accented text",
    )

# Inspect the distributed example too: a working synthetic-face specimen alone
# does not establish that the showcased document retained its intended weight.
with fitz.open(BUILD / "example/main.pdf") as document:
    strokes = [
        t
        for p in document
        for t in p.get_texttrace()
        if t["font"] == "Kalpurush" and t["type"] == 1
    ]
    check(
        bool(strokes)
        and all(math.isclose(t["linewidth"] / t["size"], 0.035, abs_tol=0.0002) for t in strokes),
        "Public example uses Kalpurush's tested default synthetic bold strength of 3.5",
    )

# Legacy font-name resolution must not interfere with English face discovery.
check(
    all(
        any(marker in s["text"] and s["font"] == family for s in spans("legacy-siyam-alias"))
        for marker, family in (
            ("EnglishBold", "TeXGyrePagella-Bold"),
            ("SansBold", "TeXGyreHeros-Bold"),
            ("MonoBold", "TeXGyreCursor-Bold"),
        )
    ),
    "Legacy SiyamRupali alias preserves subsequent English bold-font discovery",
)

# The public guide changes fonts page by page. Check the rendered selections,
# not just the labels, so an accidentally shared family cannot mislead readers.
guide_fonts = (
    ("Kalpurush", "Kalpurush", 3.5),
    ("SolaimanLipi", "SolaimanLipiNormal", 4.5),
    ("Siyam Rupali", "SiyamRupali", 4.5),
    ("Noto Serif Bengali", "NotoSerifBengali", None),
    ("Noto Sans Bengali", "NotoSansBengali", None),
    ("FreeSerif", "FreeSerif", 3.5),
)
with fitz.open(BUILD / "supported-fonts/main.pdf") as document:
    check(
        len(document) == 6
        and document.get_toc() == [[1, name, i + 1] for i, (name, _, _) in enumerate(guide_fonts)],
        "Public font guide has six pages and bookmarks in the intended order",
    )
    for index, (name, family, strength) in enumerate(guide_fonts):
        page = document[index]
        traces = [t for t in page.get_texttrace() if t["font"].startswith(family)]
        strokes = [t for t in traces if t["type"] == 1]
        check(
            bool(traces)
            and (
                bool(strokes)
                and all(
                    math.isclose(t["linewidth"] / t["size"], strength / 100, abs_tol=0.0002)
                    for t in strokes
                )
                if strength is not None
                else not strokes and any(t["font"].endswith("-Bold") for t in traces)
            ),
            f"Public font guide: {name} uses its intended face and bold weight",
        )

for suffix, family, strength, scale in (
    ("kalpurush", "Kalpurush", 3.5, 1),
    ("freeserif", "FreeSerif", 3.5, 1),
    ("solaimanlipi", "SolaimanLipiNormal", 4.5, 1),
    ("siyam-rupali", "SiyamRupali", 4.5, 0.8),
):
    with fitz.open(BUILD / ("font-faces-" + suffix) / "main.pdf") as document:
        strokes = [
            t
            for p in document
            for t in p.get_texttrace()
            if t["font"].startswith(family) and t["type"] == 1
        ]
        check(
            bool(strokes)
            and all(
                math.isclose(t["linewidth"] / t["size"], strength / 100, abs_tol=0.0002)
                for t in strokes
            ),
            f"{suffix}: synthetic faces use the visually reviewed weight",
        )
        check(
            {round(s * scale * 72 / 72.27, 2) for s in (8, 11, 16)}
            <= {round(t["size"], 2) for t in strokes},
            f"{suffix}: default scale applies at footnote, body and heading sizes",
        )

for name, expected_space in (
    ("font-profile-overrides", 4.35938),
    ("font-siyam-file", 4.185),
    ("font-profile-reselection", 4.185),
):
    log = (BUILD / name / "main.log").read_text(encoding="utf-8")
    space = re.search(r"PROFILE-SPACE: ([\d.]+)pt", log)
    height = re.search(r"PROFILE-XHEIGHT: (-?[\d.]+)pt", log)
    check(
        space is not None
        and math.isclose(float(space[1]), expected_space, abs_tol=0.0001)
        and height is not None
        and float(height[1]) > 0,
        f"{name}: Siyam Rupali has positive x-height and the intended space width",
    )
with fitz.open(BUILD / "font-profile-overrides/main.pdf") as document:
    strokes = [
        t
        for p in document
        for t in p.get_texttrace()
        if t["font"] == "SiyamRupali" and t["type"] == 1
    ]
    check(
        bool(strokes)
        and all(math.isclose(t["linewidth"] / t["size"], 0.015, abs_tol=0.0002) for t in strokes),
        "Explicit synthetic face weight overrides a known-font profile",
    )

# Both opening listings compile independently, including the comparison that
# deliberately does not load LaTeXbangla. Check the actual English font faces.
for name in ("manual-english-font", "manual-fontspec-comparison"):
    for word, face in (("keeps", "Regular"), ("read", "Bold"), ("English", "Italic")):
        check(
            any(word in span["text"] and span["font"] == f"TeXGyreAdventor-{face}"
                for span in spans(name)),
            f"{name}: English {face.lower()} uses the chosen Adventor face",
        )
    check(
        any(span["font"] == "Kalpurush" for span in spans(name)),
        f"{name}: Bangla uses Kalpurush alongside Adventor",
    )
check(
    "latexbangla.sty" not in (BUILD / "manual-fontspec-comparison/main.log").read_text(encoding="utf-8"),
    "The fontspec-only manual comparison works without loading LaTeXbangla",
)
if ENGINE == "lualatex":
    check(
        "Kalpurush:mode=harf;" in (BUILD / "manual-fontspec-comparison/main.log").read_text(encoding="utf-8"),
        "The standalone fontspec comparison enables HarfBuzz for Bangla shaping",
    )

# The manual's output panels execute their displayed source. Inspect the
# result boxes so printed source or explanatory prose cannot satisfy assertions.
with fitz.open(BUILD / "manual/main.pdf") as document:
    outline = document.get_toc(simple=False)
    section_pages = {title: page - 1 for _, title, page, _ in outline}
    manual_reader = PdfReader(BUILD / "manual/main.pdf")

    def manual_section_regions(title):
        """Locate a section across pages, using bookmark destinations as bounds."""
        index = next(i for i, entry in enumerate(outline) if entry[1] == title)
        start = outline[index]
        end = next((entry for entry in outline[index + 1:] if entry[0] <= start[0]), None)

        def heading_y(entry):
            destination = entry[3]
            if "nameddest" in destination:
                # Named destinations retain PDF's bottom-up coordinates.
                top = manual_reader.named_destinations[destination["nameddest"]].top
                assert top is not None, f"Heading destination has no vertical position: {entry[1]}"
                return document[entry[2] - 1].rect.height - float(top)
            return destination["to"].y

        last_page = end[2] - 1 if end else len(document) - 1
        for page_index in range(start[2] - 1, last_page + 1):
            page = document[page_index]
            top = heading_y(start) if page_index == start[2] - 1 else 0
            bottom = heading_y(end) if end and page_index == last_page else page.rect.height
            yield page, fitz.Rect(0, top, page.rect.width, bottom)

    def manual_result_panels(title, result_title="Result"):
        """Yield actual output panels, excluding the surrounding prose and code."""
        for page, region in manual_section_regions(title):
            for heading in page.search_for(result_title, clip=region):
                frames = [
                    drawing["rect"] for drawing in page.get_drawings()
                    if drawing["fill"] is not None
                    and drawing["rect"].x0 > page.rect.width / 2
                    # Font ascender boxes can extend above a tightly set title.
                    # Its center must still lie inside the actual panel.
                    and drawing["rect"].contains((heading.tl + heading.br) / 2)
                ]
                if frames:
                    # The outer frame encloses both title and output; its title
                    # background is a smaller rectangle containing the same word.
                    panel = max(frames, key=lambda rect: rect.get_area())
                    yield page, panel

    def manual_result_text(title, result_title="Result"):
        rendered = [page.get_textpage(clip=panel).extractText()
                    for page, panel in manual_result_panels(title, result_title)]
        return re.sub(r"\s+", "", "".join(rendered))

    for title, result_title in (("Quickstart", "Result"), ("দ্রুত আরম্ভ", "ফলাফল")):
        preview_spans = [
            span for page, panel in manual_result_panels(title, result_title)
            for block in page.get_text("dict", clip=panel)["blocks"]
            for line in block.get("lines", []) for span in line["spans"]
            if "English" in span["text"]
        ]
        check(any(span["font"] == "TeXGyreAdventor-Regular" for span in preview_spans)
              and not any(span["font"] == "TeXGyrePagella-Regular" for span in preview_spans),
              f"Manual {title} preview preserves its local Adventor font")

    check(
        (REPO / "latexbangla/logo.png").read_bytes() == (REPO / "img/logo.png").read_bytes()
        and bool(document[0].get_images()),
        "Manual includes the repository logo and bundles the identical source image",
    )
    manual_aux = (BUILD / "manual/main.aux").read_text(encoding="utf-8")
    check(
        r"\newlabel{ex:custom}{{১২}" in manual_aux
        and r"\newlabel{eq:speed}{{১}" in manual_aux
        and r"\newlabel{sec:numbering}{{4}{" in manual_aux
        and document[section_pages["Numbers, lists and your own counters"]]
        .get_text().strip().splitlines()[-1]
        == str(section_pages["Numbers, lists and your own counters"] + 1)
        and "0012" not in manual_result_text("Numbers, lists and your own counters")
        and "০০১২" in manual_result_text("Numbers, lists and your own counters"),
        "Manual uses Bangla example counters, Western navigation and explicit digit conversion",
    )
    check(
        "[১]" in manual_result_text("Labels, references and citations")
        and "১২" in manual_result_text("Labels, references and citations")
        and "(১)" in manual_result_text("Labels, references and citations"),
        "Manual output resolves its citation, custom counter and equation reference",
    )
    for title, result_title in (
        ("Extended alphabetic labels", "Result"),
        ("একাধিক বর্ণের নম্বর", "ফলাফল"),
    ):
        check(
            "ৎ,কক,কখ" in manual_result_text(title, result_title),
            f"Manual extended alphabet example executes correctly: {title}",
        )
    check(
        all(token in manual_result_text("Mathematics, tables and theorems")
            for token in ("12", "১২", "৩", "৪")),
        "Manual math output preserves Western and Bengali digits",
    )
    bold_strokes = [
        t for page, region in manual_section_regions("Control boldness and emphasis")
        for t in page.get_texttrace()
        if t["font"] == "Kalpurush" and t["type"] == 1
        and t["bbox"][0] > page.rect.width / 2
        and region.contains(fitz.Rect(t["bbox"]))
    ]
    check(
        len({round(t["chars"][0][2][1], 2) for t in bold_strokes}) == 2
        and all(math.isclose(t["linewidth"] / t["size"], 0.04, abs_tol=0.0002)
                for t in bold_strokes),
        "Manual AutoFakeBold example applies strength 4 to both bold and bold italic",
    )
    check(
        "Overfull" not in (BUILD / "manual/main.log").read_text(encoding="utf-8"),
        "Manual has no overflowing text or boxes",
    )
    bangla_start = section_pages["বাংলা ব্যবহার নির্দেশিকা"]
    bangla_digits = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    check(
        r"\newlabel{bn:sec:numbering}{{৪}" in manual_aux
        and all(
            document[index].get_textpage().extractText().strip().splitlines()[-1]
            == str(index + 1).translate(bangla_digits)
            for index in range(bangla_start + 1, len(document))
        ),
        "Bangla manual uses Bengali section and continuous page numbers",
    )
    check(
        r"\newlabel{bn:ex:custom}{{১২}" in manual_aux
        and r"\newlabel{bn:eq:speed}{{১}" in manual_aux
        and "০০১২" in manual_result_text("ক্রমসংখ্যা, তালিকা ও নিজের কাউন্টার", "ফলাফল")
        and all(
            token in manual_result_text("লেবেল, রেফারেন্স ও তথ্যসূত্র", "ফলাফল")
            for token in ("[১]", "১২", "(১)")
        ),
        "Bangla manual executes its own counter, equation and citation examples",
    )
    reference_targets = {
        link["page"]
        for page, region in manual_section_regions("লেবেল, রেফারেন্স ও তথ্যসূত্র")
        for link in page.get_links()
        if link.get("kind") in (fitz.LINK_GOTO, fitz.LINK_NAMED)
        and "page" in link
        and region.contains(link["from"])
    }
    counter_pages = {page.number for page, _ in manual_section_regions("ক্রমসংখ্যা, তালিকা ও নিজের কাউন্টার")}
    math_pages = {page.number for page, _ in manual_section_regions("গণিত, সারণি ও উপপাদ্য")}
    check(
        bool(counter_pages & reference_targets) and bool(math_pages & reference_targets)
        and all(page >= bangla_start for page in reference_targets),
        "Bangla references link to the translated examples, not the English counters",
    )

(BUILD / "checks.json").write_text(json.dumps(CHECKS, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
failures = [item for item in CHECKS if not item["passed"]]
print(
    f"{len(CHECKS)-len(failures)}/{len(CHECKS)} acceptance checks passed; {len(PDFS)} PDFs inspected."
)
for failure in failures:
    print("FAIL:", failure["description"])
raise SystemExit(bool(failures))
