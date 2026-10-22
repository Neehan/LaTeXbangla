#!/bin/sh
set -eu
test_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$test_dir/../.." && pwd)
python3 "$test_dir/fetch-fonts.py"
image_ref=texlive/texlive@sha256:7334b00bf8e7a0996f7ddd65482363aaf7711d372e569f3ea78509619e3083ff
docker run --rm --network none \
  --mount "type=bind,source=$repo_dir,target=/work" \
  --workdir /work --entrypoint python3 "$image_ref" \
  tests/xelatex/run.py "$@"
