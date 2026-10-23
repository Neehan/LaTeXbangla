#!/bin/sh
set -eu
test_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$test_dir/../.." && pwd)
python3 "$test_dir/fetch-fonts.py"
image_ref=texlive/texlive@sha256:7334b00bf8e7a0996f7ddd65482363aaf7711d372e569f3ea78509619e3083ff
docker run --rm --network none \
  --mount "type=bind,source=$repo_dir,target=/work" \
  --workdir /work --entrypoint sh "$image_ref" -c '
    set -eu
    # Fontconfig is sufficient for XeTeX. Luaotfload needs the same downloaded
    # fixtures in its own database; install them only in this disposable container.
    for argument do
      case "$argument" in
        lualatex|--engine=lualatex)
          mkdir -p /usr/local/share/fonts/latexbangla-tests
          for font_file in tests/latex/fonts/*.ttf tests/latex/fonts/*.otf tests/latex/fonts/*.ttc; do
            [ ! -f "$font_file" ] || cp "$font_file" /usr/local/share/fonts/latexbangla-tests/
          done
          fc-cache -f
          luaotfload-tool --update --force >/tmp/latexbangla-font-cache.log 2>&1
          break ;;
      esac
    done
    exec python3 tests/latex/run.py "$@"
  ' sh "$@"
