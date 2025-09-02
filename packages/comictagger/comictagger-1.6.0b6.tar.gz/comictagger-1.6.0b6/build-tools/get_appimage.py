from __future__ import annotations

import argparse
import os
import pathlib
import platform

try:
    import niquests as requests
except ImportError:
    import requests

arch = platform.machine()
parser = argparse.ArgumentParser()
parser.add_argument("APPIMAGETOOL", default=f"build/appimagetool-{arch}.AppImage", type=pathlib.Path, nargs="?")

opts = parser.parse_args()
opts.APPIMAGETOOL = opts.APPIMAGETOOL.absolute()


def urlretrieve(url: str, dest: pathlib.Path) -> None:
    resp = requests.get(url)
    if resp.status_code == 200:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(resp.content)


if opts.APPIMAGETOOL.exists():
    raise SystemExit(0)

urlretrieve(
    f"https://github.com/AppImage/appimagetool/releases/latest/download/appimagetool-{arch}.AppImage",
    opts.APPIMAGETOOL,
)
os.chmod(opts.APPIMAGETOOL, 0o0700)

if not opts.APPIMAGETOOL.exists():
    raise SystemExit(1)
