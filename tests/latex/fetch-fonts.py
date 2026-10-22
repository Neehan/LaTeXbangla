#!/usr/bin/env python3
"""Fetch checksum-pinned Bengali fonts for the XeLaTeX acceptance tests.

Noto comes from Ubuntu 22.04; SolaimanLipi and Siyam Rupali from OmicronLab.
Overleaf documents this Ubuntu release as its Noto font source. Keep the test
assets reproducible without installing fonts on the host or redistributing them
as part of the LaTeX package. Existing files are reused only after hash checks.
"""
import argparse
import hashlib
import io
from pathlib import Path
import subprocess
import tarfile
import urllib.request

DIRECTORY = Path(__file__).resolve().parent / "fonts"
NOTO_URL = "https://archive.ubuntu.com/ubuntu/pool/main/f/fonts-noto/fonts-noto-core_20201225-1build1_all.deb"
NOTO_ARCHIVE_SHA256 = "653d237d5c4e8fcebb2710129ebbd7bf9bc248d03dfff23fcf261b0372fded69"
NOTO_FILES = {
    "NotoSansBengali-Regular.ttf": "9bb35b3547829ecc42041b6017e87fd4c5f1da1edcd00f59171777050f346018",
    "NotoSansBengali-Bold.ttf": "22c9ff99baca4d31c531ce450a1369beed889467e1ad964f4b8a6f810aa46955",
    "NotoSerifBengali-Regular.ttf": "32b4aeb731e3819d7a31216c885208a96e402ceeebb30fc39723b99220708fef",
    "NotoSerifBengali-Bold.ttf": "96cc17640329810e2ac1b53d61ec4f429ba9bf729d4f37623a296581d79a5133",
    "copyright": "075f91382875da1c4b491f1facf2586f55448705133264d98ce15cab6211b125",
}
OMICRONLAB_FONTS = {
    "Siyamrupali.ttf": "54a85c66ad1e6f0c50d3bda85eba5a4975fe49d06819d23230a15f3d7f0573ae",
    "SolaimanLipi_20-04-07.ttf": "16bbf4f0140dab8fcf53ab34a923674ea8c9de2f8583d110c7e62b0094a22fe6",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare_noto(local_archive: Path | None):
    if all(
        (DIRECTORY / name).exists() and digest((DIRECTORY / name).read_bytes()) == expected
        for name, expected in NOTO_FILES.items()
    ):
        print("Pinned Noto Bengali test fonts verified.")
        return
    DIRECTORY.mkdir(exist_ok=True)
    archive_path = local_archive or DIRECTORY / "fonts-noto-core.deb"
    if not local_archive:
        with urllib.request.urlopen(NOTO_URL, timeout=60) as response:
            archive_path.write_bytes(response.read())
    if digest(archive_path.read_bytes()) != NOTO_ARCHIVE_SHA256:
        raise SystemExit("Noto package checksum mismatch; refusing to extract it.")
    # ar is available on both the macOS host and the Linux test image. Extract
    # only named regular files from the tar payload, never arbitrary paths.
    payload = subprocess.check_output(["ar", "-p", str(archive_path), "data.tar.xz"])
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:xz") as archive:
        for name, expected in NOTO_FILES.items():
            member_path = (
                "./usr/share/doc/fonts-noto-core/copyright"
                if name == "copyright"
                else "./usr/share/fonts/truetype/noto/" + name
            )
            member = archive.getmember(member_path)
            if not member.isfile():
                raise SystemExit(f"Unexpected archive member: {member_path}")
            extracted_file = archive.extractfile(member)
            if extracted_file is None:
                raise SystemExit(f"Cannot read archive member: {member_path}")
            with extracted_file:
                data = extracted_file.read()
            if digest(data) != expected:
                raise SystemExit(f"Font checksum mismatch: {name}")
            (DIRECTORY / name).write_bytes(data)
    print("Prepared four Noto Bengali font files and their license notice.")


def prepare_omicronlab():
    DIRECTORY.mkdir(exist_ok=True)
    for name, expected in OMICRONLAB_FONTS.items():
        path = DIRECTORY / name
        if path.exists() and digest(path.read_bytes()) == expected:
            continue
        url = "https://www.omicronlab.com/download/fonts/" + name
        with urllib.request.urlopen(url, timeout=60) as response:
            data = response.read()
        if digest(data) != expected:
            raise SystemExit(f"Font checksum mismatch: {name}")
        path.write_bytes(data)
    print("Pinned SolaimanLipi and Siyam Rupali test fonts verified.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, help="use an already downloaded Noto .deb")
    args = parser.parse_args()
    prepare_noto(args.archive)
    prepare_omicronlab()


if __name__ == "__main__":
    main()
