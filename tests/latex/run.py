#!/usr/bin/env python3
"""Compile acceptance specimens inside the pinned TeX Live container.

Run via run.sh from a checkout. Each specimen gets an isolated build directory;
verify.py separately checks the resulting PDF text, fonts and link destinations.
"""
# Copyright 2026 Adib Hasan. LPPL 1.3c or later; see ../../LICENSE.
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import TypedDict

from cases import cases, FIXTURES, REPO, ROOT


class CompilationResult(TypedDict):
    """Per-specimen result, also serialized to build/results.json."""

    exitcodes: list[int]
    seconds: list[float]
    expected_error: str | None
    expected_error_seen: bool
    missing_glyph_count: int
    warnings: list[str]
    pdf: bool


def execute(
    command: list[str], directory: Path, environment: dict[str, str]
) -> tuple[int, str, float]:
    """Capture a tool's output and bound each compilation/backend invocation."""
    start = time.monotonic()
    try:
        process = subprocess.run(
            command,
            cwd=directory,
            env=environment,
            capture_output=True,
            text=True,
            errors="replace",
            timeout=120,
        )
        return (
            process.returncode,
            process.stdout + process.stderr,
            round(time.monotonic() - start, 3),
        )
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b""
        if isinstance(output, bytes):
            output = output.decode(errors="replace")
        return 124, output + "\nTIMEOUT", 120


def compile_case(
    name: str, case, environment: dict[str, str], engine: str, build: Path
) -> CompilationResult:
    directory = build / name
    # Each specimen owns its output directory, including generated subfolders
    # such as minted's cache. Never let an earlier build supply missing output.
    if directory.exists():
        shutil.rmtree(directory)
    directory.mkdir()
    (directory / "main.tex").write_text(case["tex"], encoding="utf-8")
    shutil.copyfile(FIXTURES / "references.bib", directory / "references.bib")
    timings: list[float] = []
    exitcodes: list[int] = []
    output = ""  # Fallback diagnostic when no TeX log is available.
    for pass_number in range(1, case["passes"] + 1):
        command = [
            case.get("engine", engine),
            # Minted in the manual uses TeX Live's allowlisted latexminted tool.
            "-shell-restricted" if case.get("restricted_shell_escape") else "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "main.tex",
        ]
        code, output, elapsed = execute(command, directory, environment)
        (directory / f"pass-{pass_number}.stdout").write_text(output, encoding="utf-8")
        timings.append(elapsed)
        exitcodes.append(code)
        if code:
            break
        if pass_number == 1 and case["backend"]:
            code, backend_output, _ = execute([case["backend"], "main"], directory, environment)
            (directory / "backend.stdout").write_text(backend_output, encoding="utf-8")
            if code:
                exitcodes.append(code)
                break
    log_path = directory / "main.log"
    log = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else output
    warnings = [
        line
        for line in log.splitlines()
        if any(marker in line for marker in ("Warning", "Missing character:", "Error"))
    ]
    return CompilationResult(
        exitcodes=exitcodes,
        seconds=timings,
        expected_error=case["expect_error"],
        expected_error_seen=bool(case["expect_error"] and case["expect_error"] in log),
        missing_glyph_count=log.count("Missing character:"),
        warnings=warnings,
        pdf=(directory / "main.pdf").exists(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("names", nargs="*", help="specimen names; omit to run the complete suite")
    parser.add_argument("--list", action="store_true", help="list available specimens")
    parser.add_argument("--engine", choices=("xelatex", "lualatex"), default="xelatex")
    parser.add_argument("--build-dir", type=Path, default=ROOT / "build",
                        help="Build root; each engine uses its own subdirectory")
    args = parser.parse_args()
    build = args.build_dir.resolve() / args.engine
    specimens = cases()
    if args.list:
        print("\n".join(specimens))
        return 0
    unknown = sorted(set(args.names) - specimens.keys())
    if unknown:
        parser.error("unknown specimens: " + ", ".join(unknown))
    build.mkdir(parents=True, exist_ok=True)
    # Keep font discovery local to the test processes. The trailing TEXINPUTS
    # separator retains TeX's normal package search path after the package source tree.
    environment = dict(
        os.environ,
        TEXINPUTS=".:" + str(REPO / "latexbangla") + ":",
        FONTCONFIG_FILE=str(ROOT / "fonts.conf"),
        OSFONTDIR=str(ROOT / "fonts") + "//:",
        max_print_line="1000",
    )
    version = subprocess.check_output([args.engine, "--version"], text=True)
    (build / "engine.txt").write_text(version, encoding="utf-8")
    results_path = build / "results.json"
    results = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    failures = []
    for name in args.names or specimens:
        case = specimens[name]
        result = compile_case(name, case, environment, args.engine, build)
        results[name] = result
        results_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        if case["expect_error"]:
            passed = any(result["exitcodes"]) and result["expected_error_seen"]
        else:
            passed = (
                len(result["exitcodes"]) == case["passes"]
                and not any(result["exitcodes"])
                and result["pdf"]
            )
        if not passed:
            failures.append(name)
        print(
            f"{name}: exits={result['exitcodes']} seconds={result['seconds']} "
            f"missing={result['missing_glyph_count']} expected_error={result['expected_error_seen']}",
            flush=True,
        )
    if failures:
        print("Unexpected compilation results:", ", ".join(failures))
    return int(bool(failures))


if __name__ == "__main__":
    raise SystemExit(main())
