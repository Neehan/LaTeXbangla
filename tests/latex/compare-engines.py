#!/usr/bin/env python3
"""Compare identical XeLaTeX and LuaLaTeX font specimens without resizing glyphs.

Run after both acceptance suites. The HTML report combines full-page images,
translation-aligned text rows, color overlays, pixel differences and independent
font/PDF measurements. Raster scores describe differences; they are not a
substitute for checking shaping, font selection and document semantics.
"""
# Copyright 2026 Adib Hasan. LPPL 1.3c or later; see ../../LICENSE.
import argparse
import base64
from html import escape
import io
import json
import re

import fitz
from PIL import Image, ImageChops

from cases import BENGALI_FONTS, ROOT

ENGINES = ("xelatex", "lualatex")
STYLES = {"Regular": "regular", "Bold": "bold", "Italic": "italic", "Bold italic": "bolditalic"}


def font_measurements(directory):
    """Read TeX's actual em, slant and shaped box width in source order."""
    log = (directory / "main.log").read_text(encoding="utf-8")
    pattern = (r"FACE-METRICS: size=([\d.]+); style=(\w+); em=([\d.]+)pt; "
               r"slant=(-?[\d.]+)pt; width=([\d.]+)pt")
    return [dict(size_pt=float(size), style=style, em_pt=float(em),
                 slant=float(slant), advance_pt=float(width))
            for size, style, em, slant, width in re.findall(pattern, log)]


def sample_rows(page):
    """Locate printed style labels and the Bangla text following each label."""
    lines = [line for block in page.get_text("dict")["blocks"]
             for line in block.get("lines", [])]
    all_spans = [span for line in lines for span in line["spans"]]
    rows = []
    for line in lines:
        spans = line["spans"]
        label = re.match(r"^(Regular|Bold italic|Bold|Italic):", "".join(s["text"] for s in spans))
        if not label:
            continue
        baseline = spans[0]["origin"][1]
        # PDF extractors may split a physical row at the quad after its label.
        # Match by baseline, not by the extractor's line-grouping heuristic.
        same_baseline = [span for span in all_spans
                         if abs(span["origin"][1] - baseline) < 0.1]
        bangla = [span for span in same_baseline
                  if any("\u0980" <= char <= "\u09ff" for char in span["text"])]
        start = min(span["origin"][0] for span in bangla)
        content = [span for span in same_baseline if span["origin"][0] >= start - 0.01]
        bounds = fitz.Rect(content[0]["bbox"])
        for span in content[1:]:
            bounds |= fitz.Rect(span["bbox"])
        rows.append(dict(style=STYLES[label[1]], bounds=bounds, origin=(start, baseline)))
    if len(rows) != 12:
        raise ValueError(f"Expected twelve font rows, found {len(rows)}")
    return rows


def raster(page, dpi):
    pixmap = page.get_pixmap(dpi=dpi, colorspace=fitz.csRGB, alpha=False)
    return Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)


def aligned_rasters(documents, rows, dpi):
    """Translate both baselines to the same point; never scale or shear text.

    Rendering a translated PDF clip avoids rounding each source clip to a
    different pixel origin. Full-page views separately retain layout shifts.
    """
    left = min(row["bounds"].x0 - row["origin"][0] for row in rows) - 3
    top = min(row["bounds"].y0 - row["origin"][1] for row in rows) - 3
    right = max(row["bounds"].x1 - row["origin"][0] for row in rows) + 3
    bottom = max(row["bounds"].y1 - row["origin"][1] for row in rows) + 3
    images = []
    for document, row in zip(documents, rows):
        x, y = row["origin"]
        clip = fitz.Rect(x + left, y + top, x + right, y + bottom)
        with fitz.open() as translated:
            page = translated.new_page(width=clip.width, height=clip.height)
            page.show_pdf_page(page.rect, document, 0, clip=clip, keep_proportion=False)
            images.append(raster(page, dpi))
    return images


def differences(images):
    """Measure only the union of inked pixels, excluding the blank background."""
    xe, lua = [image.convert("L") for image in images]
    if xe.size != lua.size:
        raise ValueError("Cannot compare rasters with different dimensions")
    masks = [image.point(lambda value: 255 if value < 245 else 0) for image in (xe, lua)]
    union = ImageChops.lighter(*masks)
    intersection = ImageChops.darker(*masks)
    ink_pixels = union.histogram()[255]
    difference = ImageChops.difference(xe, lua)
    histogram = difference.histogram(mask=union)
    metrics = {
        "ink_intersection_over_union": round(intersection.histogram()[255] / max(ink_pixels, 1), 6),
        "mean_absolute_ink_difference_0_to_255": round(
            sum(value * count for value, count in enumerate(histogram)) / max(ink_pixels, 1), 4),
    }
    # Shared ink is black, XeTeX-only ink magenta, LuaTeX-only ink cyan.
    overlay = Image.merge("RGB", (lua, xe, ImageChops.lighter(xe, lua)))
    return overlay, ImageChops.invert(difference), metrics


def pdf_measurements(page, row):
    """Record actual PDF fonts, sizes and synthetic strokes within this row."""
    traces = [trace for trace in page.get_texttrace()
              if row["bounds"].intersects(fitz.Rect(trace["bbox"]))
              and any(0x0980 <= char[0] <= 0x09FF for char in trace["chars"])]
    return {
        "fonts": sorted({trace["font"] for trace in traces}),
        "sizes_bp": sorted({round(trace["size"], 6) for trace in traces}),
        "synthetic_strokes_bp": sorted({round(trace["linewidth"], 6) for trace in traces
                                        if trace["type"] == 1}),
    }


def image_tag(image, path, title):
    """Keep PNGs for inspection and embed them in a portable HTML report."""
    image.save(path)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    return (f'<figure><figcaption>{escape(title)}</figcaption>'
            f'<img alt="{escape(title)}" src="data:image/png;base64,{encoded}"></figure>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dpi", type=int, default=192)
    args = parser.parse_args()
    if not 72 <= args.dpi <= 600:
        parser.error("--dpi must be between 72 and 600")
    output = ROOT / "build" / "engine-comparison"
    output.mkdir(parents=True, exist_ok=True)
    report = [f"""<!doctype html><html lang="en"><meta charset="utf-8">
<title>LaTeXbangla: XeLaTeX and LuaLaTeX</title>
<style>
body {{font:16px/1.5 system-ui,sans-serif;max-width:1500px;margin:2rem auto;padding:0 1rem;color:#24363e}}
h1,h2 {{color:#006847}} section {{border-top:1px solid #ccd6d6;margin-top:2rem}}
.grid {{display:grid;grid-template-columns:1fr 1fr;gap:1rem}} figure {{margin:0;overflow:auto}}
img {{max-width:100%;height:auto}} figcaption {{font-weight:600}}
.sample {{margin:1.5rem 0;padding:1rem;background:#f4f7f7}} summary {{cursor:pointer}}
pre {{white-space:pre-wrap}} table {{border-collapse:collapse;width:100%;margin:.5rem 0}}
th,td {{text-align:left;padding:.3rem .5rem;border-bottom:1px solid #dbe2e2}}
@media(max-width:700px) {{.grid {{grid-template-columns:1fr}}}}
</style><h1>XeLaTeX and LuaLaTeX font comparison</h1>
<p>Identical source, fonts and {args.dpi} DPI rasterization. Full pages retain layout
positions. Individual rows are translated to a common starting point and baseline;
no resizing, rotation or shearing is applied. Zoom in to examine edges.</p>
<p>Overlay: <b style="color:#b000b0">magenta = XeTeX only</b>,
<b style="color:#008b8b">cyan = LuaTeX only</b>, black = shared ink.
Difference images show changes in dark pixels against white. Raster scores exclude
blank background and do not by themselves establish typographic correctness.</p>
<p>Font dimensions and shaped advance come from TeX, in pt. Slant is dimensionless.
Actual PDF font sizes and stroke widths use bp (72 per inch, versus 72.27 pt).
All numeric deltas are LuaLaTeX minus XeLaTeX.</p>"""]
    report.append("<details><summary>Engine versions</summary><pre>")
    for engine in ENGINES:
        report.append(escape((ROOT / "build" / engine / "engine.txt").read_text(encoding="utf-8")))
    report.append("</pre></details>")
    results = {}
    for suffix, font_name in BENGALI_FONTS.items():
        directories = [ROOT / "build" / engine / ("font-faces-" + suffix) for engine in ENGINES]
        if (directories[0] / "main.tex").read_bytes() != (directories[1] / "main.tex").read_bytes():
            raise SystemExit(f"Source differs for font-faces-{suffix}; recompile both engines first.")
        measurements = [font_measurements(directory) for directory in directories]
        if any(len(values) != 12 for values in measurements):
            raise SystemExit(f"Recompile font-faces-{suffix} with both engines to record twelve measurements.")
        documents = [fitz.open(directory / "main.pdf") for directory in directories]
        rows = [sample_rows(document[0]) for document in documents]
        report.append(f'<section id="{suffix}"><h2>{escape(font_name)}</h2><details><summary>Full pages and layout differences</summary><div class=grid>')
        full_images = [raster(document[0], args.dpi) for document in documents]
        overlay, diff, _ = differences(full_images)
        for image, label in zip([*full_images, overlay, diff], [*ENGINES, "overlay", "difference"]):
            report.append(image_tag(image, output / f"{suffix}-page-{label}.png", label))
        report.append("</div></details>")
        results[suffix] = []
        for index, (xe_row, lua_row) in enumerate(zip(*rows)):
            row_measurements = [values[index] for values in measurements]
            if not (xe_row["style"] == lua_row["style"] == row_measurements[0]["style"]
                    == row_measurements[1]["style"]):
                raise ValueError(f"Style order differs in {suffix} row {index}")
            aligned = aligned_rasters(documents, [xe_row, lua_row], args.dpi)
            overlay, diff, scores = differences(aligned)
            delta = {key: round(row_measurements[1][key] - row_measurements[0][key], 6)
                     for key in ("em_pt", "slant", "advance_pt")}
            pdf = [pdf_measurements(document[0], row)
                   for document, row in zip(documents, [xe_row, lua_row])]
            results[suffix].append(dict(tex=dict(zip(ENGINES, row_measurements)),
                                        pdf=dict(zip(ENGINES, pdf)), delta=delta, raster=scores))
            title = f'{row_measurements[0]["size_pt"]:g} pt — {xe_row["style"]}'
            report.append(f'<div class=sample><h3>{escape(title)}</h3><div class=grid>')
            for image, label in zip([*aligned, overlay, diff], [*ENGINES, "overlay", "difference"]):
                report.append(image_tag(image, output / f"{suffix}-{index:02}-{label}.png", label))
            report.append("</div><table><tr><th>Measurement</th><th>XeLaTeX</th><th>LuaLaTeX</th><th>Delta</th></tr>")
            for key in delta:
                report.append(f'<tr><td>{key}</td><td>{row_measurements[0][key]:g}</td>'
                              f'<td>{row_measurements[1][key]:g}</td><td>{delta[key]:+.6f}</td></tr>')
            for key in ("fonts", "sizes_bp", "synthetic_strokes_bp"):
                report.append(f'<tr><td>{key}</td><td>{escape(str(pdf[0][key]))}</td>'
                              f'<td>{escape(str(pdf[1][key]))}</td><td>—</td></tr>')
            report.append(f'</table><p>Ink overlap: {scores["ink_intersection_over_union"]:.2%}; '
                          f'mean ink difference: {scores["mean_absolute_ink_difference_0_to_255"]:.2f}/255.</p></div>')
        for document in documents:
            document.close()
        report.append("</section>")
    overview = ["<h2>Comparison summary</h2><table><tr><th>Font</th>"
                "<th>Largest advance difference (pt)</th><th>Lowest ink overlap</th></tr>"]
    for suffix, rows in results.items():
        maximum_width_delta = max(abs(row["delta"]["advance_pt"]) for row in rows)
        minimum_overlap = min(row["raster"]["ink_intersection_over_union"] for row in rows)
        overview.append(f'<tr><td><a href="#{suffix}">{escape(BENGALI_FONTS[suffix])}</a></td>'
                        f"<td>{maximum_width_delta:.6f}</td><td>{minimum_overlap:.2%}</td></tr>")
    overview.append("</table>")
    report.insert(1, "\n".join(overview))
    (output / "measurements.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    (output / "index.html").write_text("\n".join(report) + "</html>\n", encoding="utf-8")
    print(f"Compared 72 style/size samples across six fonts: {output / 'index.html'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
