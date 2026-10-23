#!/usr/bin/env python3
"""Fetch checksum-pinned Bengali fonts for the acceptance tests.

Noto comes from Ubuntu 22.04; SolaimanLipi and Siyam Rupali from OmicronLab.
Other families come from Google Fonts, author releases and font archives.
Kohinoor Bangla is tested only with a locally supplied copy.
Overleaf documents this Ubuntu release as its Noto font source. Keep the test
assets reproducible without installing fonts on the host or redistributing them
as part of the LaTeX package. Existing files are reused only after hash checks.
"""

import argparse
import hashlib
import io
from pathlib import Path
import shutil
import subprocess
import tarfile
import urllib.request
import zipfile

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
ANEK_BASE_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "95f4904fc8bcf26d3420fe315560c96417c6dec7/ofl/anekbangla/"
)
ANEK_FILES = {
    "AnekBangla-VF.ttf": (
        "AnekBangla%5Bwdth%2Cwght%5D.ttf",
        "8b4ec2eaf7400ea9903718a4addf3135475292e6e0b04db7735d0f999289d919",
    ),
    "AnekBangla-OFL.txt": (
        "OFL.txt",
        "de62be758bba267e653a5f457dfebb4680957e2c343eb3e7de15aff4746bed05",
    ),
}
TIRO_BASE_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "8b0a1d0f5983c89bc2b93f1b5fb55f9e252744b5/ofl/tirobangla/"
)
TIRO_FILES = {
    "TiroBangla-Regular.ttf": (
        "TiroBangla-Regular.ttf",
        "a763523dc3f90a71962cb8d9400b8f0a86b40b2cb01676f165101a2967127ae4",
    ),
    "TiroBangla-Italic.ttf": (
        "TiroBangla-Italic.ttf",
        "deb8330a56697cfabef8ff393c6d36af60531229b138bf9a3ffe834330cb03e1",
    ),
    "TiroBangla-OFL.txt": (
        "OFL.txt",
        "2ed6051706542c5d6d96480318152b17900bb6d4dbadb11d7d5d6464d8b3e0dd",
    ),
}
GALADA_BASE_URL = (
    "https://raw.githubusercontent.com/google/fonts/"
    "8d688a5ee4b997b5e31a9242eb7a670890d506fa/ofl/galada/"
)
GALADA_FILES = {
    "Galada-Regular.ttf": (
        "Galada-Regular.ttf",
        "acc22b41ee470dc542e15b5f8907c7fbebef1b9c01eb20e4127bdbf052b006ee",
    ),
    "Galada-OFL.txt": (
        "OFL.txt",
        "6a809aeba8af2115ca4b4c3597b1fbeb836a45f0489070f330f9c2dff870da8d",
    ),
}

# Additional upstream assets; downloaded only into the ignored test directory.
ADDITIONAL_FILES = {
    "JamrulNormal.ttf": (
        "https://www.nongnu.org/freebangfont/dl/JamrulNormal.ttf",
        "0d98610301a7f508e8d9bb9b2b2920afcafc690e17705bff272ae3bf20914fdd",
    ),
    "LikhanNormal.ttf": (
        "https://www.nongnu.org/freebangfont/dl/LikhanNormal.ttf",
        "2eea5b6d374c96249839c7df96acd3c34a0f6b57af18bf8ae281f55a72b55971",
    ),
    "Shimanto.ttf": (
        "https://banglacode.com/fonts/Shimanto.ttf",
        "5d39f704b82649b62ae64f4c636f744ab85f23a56f4c065caec0b2a5a22ae040",
    ),
    "BalooDa2-OFL.txt": (
        "https://raw.githubusercontent.com/EkType/Baloo2/1.640/OFL.txt",
        "71553532f1a32adcd610d11a79535fae28c56df4e3e877c5ae3b585633e36efc",
    ),
    "HindSiliguri-Regular.ttf": (
        "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl/hindsiliguri/HindSiliguri-Regular.ttf",
        "45071a7da902a74877f432722f525d00502d61aef71fca4cab3da8a23156c33d",
    ),
    "HindSiliguri-Bold.ttf": (
        "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl/hindsiliguri/HindSiliguri-Bold.ttf",
        "d135765781d1a4aebc7dd4a2af221427ec8689060121d8a48b19bca3eeb3977e",
    ),
    "HindSiliguri-OFL.txt": (
        "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl/hindsiliguri/OFL.txt",
        "4b255eb44f613a8e426e195f0d0b7e10fcba1af7eb6047d9a7f4f3c449940e19",
    ),
    "Lohit-Bengali.ttf": (
        "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl/lohitbengali/Lohit-Bengali.ttf",
        "609aefb344d7c7e5b082f7dad501c5479f668896088a93b198675bf6213e8ee1",
    ),
    "Lohit-Bengali-OFL.txt": (
        "https://raw.githubusercontent.com/google/fonts/e7db6ca603fd4862010383ff17ffd6cc4ffac1c0/ofl/lohitbengali/OFL.txt",
        "e88691a5e0a8a3f788f31db959701ec90a1d5e7505f1cc53c5663180a7d23c81",
    ),
    "Nikosh.ttf": (
        "https://www.navy.mil.bd/public/backend/ckfinder/core/connector/php/files/Nikosh.ttf",
        "fcebcd9cae1a833a62ae32787dbe03e71df2bc76b4dbc07c1d51cab461bdd4ca",
    ),
    "mukti.otf": (
        "https://github.com/mitradranirban/fonts-mukti/releases/download/v3.4.3/mukti.otf",
        "38e8c89c7b64ecf8a59e9b049ee9c80cc0d58115371db42aa3c94c755e0b2c79",
    ),
    "muktibold.otf": (
        "https://github.com/mitradranirban/fonts-mukti/releases/download/v3.4.3/muktibold.otf",
        "ea721c4d78354b38de6d0dbe8b1198af887284f747b66199bbab2481b3b67118",
    ),
    "muktiita.otf": (
        "https://github.com/mitradranirban/fonts-mukti/releases/download/v3.4.3/muktiita.otf",
        "8cdb72c0030a4d0dbe803f2ed92f86c9d31117030291504a97c34c57eacacc34",
    ),
    "muktibi.otf": (
        "https://github.com/mitradranirban/fonts-mukti/releases/download/v3.4.3/muktibi.otf",
        "be92daf654ec906ed94f4886d0b790f9c55310d0b85ed65b6aa95b133d340946",
    ),
    "Mukti-LICENCE.txt": (
        "https://raw.githubusercontent.com/mitradranirban/fonts-mukti/v3.4.3/LICENCE",
        "e197b622b786220bf9ab4ab009f512addaeff979cab07575c32278ba191bd345",
    ),
    "Mukti-copyright.txt": (
        "https://raw.githubusercontent.com/mitradranirban/fonts-mukti/v3.4.3/copyright",
        "f7b3c0548573de3690cee9f183924e2f6cf7d0aa6bd7a4560e99b00bd6d6fec0",
    ),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def prepare_noto(local_archive: Path | None):
    if all(
        (DIRECTORY / name).exists()
        and digest((DIRECTORY / name).read_bytes()) == expected
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


def prepare_pinned_files(base_url, files):
    DIRECTORY.mkdir(exist_ok=True)
    for name, (remote_name, expected) in files.items():
        path = DIRECTORY / name
        if path.exists() and digest(path.read_bytes()) == expected:
            continue
        with urllib.request.urlopen(base_url + remote_name, timeout=60) as response:
            data = response.read()
        if digest(data) != expected:
            raise SystemExit(f"Font checksum mismatch: {name}")
        path.write_bytes(data)


def prepare_baloo():
    """Use the author's static Regular/Bold release for portable face discovery."""
    files = {
        "BalooDa2-Regular.ttf": "2f9a3eed04975aefc79a636a023aa4f7923251e3289ad2e861ea3fa26e0cda47",
        "BalooDa2-Bold.ttf": "0d7fd3408d6161088736403bc9407c36765081e2520ea5aa43d29825c2bb01b1",
    }
    if all(
        (DIRECTORY / name).exists()
        and digest((DIRECTORY / name).read_bytes()) == expected
        for name, expected in files.items()
    ):
        return
    url = "https://github.com/EkType/Baloo2/releases/download/1.640/Baloo2_1.640.zip"
    with urllib.request.urlopen(url, timeout=60) as response:
        data = response.read()
    if (
        digest(data)
        != "1f810c51d46a826294d2b9974db0a981a20b06bb629af4aab2f9687e15fd77c1"
    ):
        raise SystemExit("Baloo release checksum mismatch.")
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name, expected in files.items():
            data = archive.read("Bangla/" + name)
            if digest(data) != expected:
                raise SystemExit(f"Font checksum mismatch: {name}")
            (DIRECTORY / name).write_bytes(data)


def prepare_kohinoor(source):
    """Use a local licensed copy when available; never fetch this system font."""
    target = DIRECTORY / "KohinoorBangla.ttc"
    if source.is_file() and source.resolve() != target.resolve():
        shutil.copyfile(source, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archive", type=Path, help="use an already downloaded Noto .deb"
    )
    parser.add_argument(
        "--kohinoor-font",
        type=Path,
        default=Path("/System/Library/Fonts/KohinoorBangla.ttc"),
        help="optional local Kohinoor Bangla collection for testing",
    )
    args = parser.parse_args()
    prepare_noto(args.archive)
    prepare_omicronlab()
    prepare_pinned_files(ANEK_BASE_URL, ANEK_FILES)
    prepare_pinned_files(TIRO_BASE_URL, TIRO_FILES)
    prepare_pinned_files(GALADA_BASE_URL, GALADA_FILES)
    prepare_pinned_files("", ADDITIONAL_FILES)
    prepare_baloo()
    prepare_kohinoor(args.kohinoor_font)
    print("Pinned font files verified; local Kohinoor included when available.")


if __name__ == "__main__":
    main()
