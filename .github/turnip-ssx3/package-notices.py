#!/usr/bin/env python3
"""Package deterministic turnip-notices.zip for the ssx3 Turnip release.

Inputs: the Mesa source tree (licenses/ + this script's static notice text).
Output: a byte-deterministic zip (sorted entries, fixed timestamps/permissions,
fixed compression) so the release asset SHA can be pinned in
PS2Recomp tools/ssx3/turnip.json and enforced by build.py.

Usage: package-notices.py <mesa-src> <out-zip>
"""
import pathlib
import sys
import zipfile

FIXED_DATE = (1980, 1, 1, 0, 0, 0)

NOTICE = """SSX3 Turnip notices (ssx3 P1-only series)
==========================================

This driver is Mesa Turnip (Freedreno Vulkan, KGSL) built from the
brad-richardson/mesa fork branch carrying only the UBWC gralloc detection
patch below, on top of upstream Mesa main.

Carried patch (NOT upstream):
  [FS2] u_gralloc: always use ubwc detection path (whitebelyash HACK,
  carried from Turnip_Gen8_V36; FS2 report).
  Original author: whitebelyash <whbexiumwork@gmail.com>.
  Reason: newer Qualcomm vendor grallocs no longer match the driver's
  'gmsm'-magic gate, so imported AHardwareBuffers get no UBWC modifier
  (tiled garbage on Adreno 830 without it).

Mesa itself is distributed under the licenses in licenses/.
See https://www.mesa3d.org/license/ .
"""


def main(src, out):
    src = pathlib.Path(src)
    lic = src / "licenses"
    assert lic.is_dir(), "licenses/ missing"
    entries = {}
    for p in sorted(lic.rglob("*")):
        if p.is_file():
            entries["licenses/" + p.relative_to(lic).as_posix()] = p.read_bytes()
    entries["NOTICE.turnip-ssx3"] = NOTICE.encode()
    with zipfile.ZipFile(out, "w") as z:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.compress_level = 9
            info.external_attr = 0o644 << 16
            z.writestr(info, entries[name])
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: package-notices.py <mesa-src> <out-zip>")
    main(sys.argv[1], sys.argv[2])
