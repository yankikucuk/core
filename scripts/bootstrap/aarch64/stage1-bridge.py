#!/usr/bin/env python3
"""Find the shared libraries a Pisi root needs but does not contain.

Stage-1 packages were built on Debian, so some of their programs link
against libraries only Debian has (libtinfo.so.6, libaio.so.1t64, ...) or
against libraries of recipes that did not build in stage 1. This script
scans every ELF file under the root, collects its DT_NEEDED entries and
reports those that no file in the root's library directories provides.

    stage1-bridge.py ROOT            list what is missing, exit 1 if anything is
    stage1-bridge.py ROOT --copy     copy the missing libraries (and what they
                                     need in turn) from this host into
                                     ROOT/usr/lib/stage1-bridge

The bridge only lets stage-1 programs run long enough to rebuild core inside
the root. After the rebuild the bridge is deleted and the plain listing must
come back empty: then nothing in the root depends on Debian any more.
"""

import os
import subprocess
import sys

LIBRARY_DIRS = ("lib", "usr/lib")
BRIDGE_DIR = "usr/lib/stage1-bridge"


def is_elf(path):
    """True for regular files that start with the ELF magic number."""
    if os.path.islink(path) or not os.path.isfile(path):
        return False
    with open(path, "rb") as handle:
        return handle.read(4) == b"\x7fELF"


def needed_libraries(path):
    """DT_NEEDED sonames of one ELF file, read with readelf."""
    output = subprocess.run(["readelf", "-d", path], capture_output=True,
                            text=True).stdout
    sonames = []
    for line in output.splitlines():
        if "(NEEDED)" in line:
            sonames.append(line.split("[", 1)[1].split("]", 1)[0])
    return sonames


def provided_libraries(root):
    """File names (including symlinks) under the root's library dirs."""
    names = set()
    for directory in LIBRARY_DIRS:
        for current, _, files in os.walk(os.path.join(root, directory)):
            names.update(files)
    return names


def missing_libraries(root):
    """Map each soname nobody provides to the files that need it."""
    provided = provided_libraries(root)
    missing = {}
    for current, directories, files in os.walk(root):
        # Pseudo file systems and the build area are not part of the root.
        directories[:] = [d for d in directories
                          if os.path.join(current, d)[len(root):] not in
                          ("/proc", "/sys", "/dev", "/var/pisi")]
        for name in files:
            path = os.path.join(current, name)
            if not is_elf(path):
                continue
            for soname in needed_libraries(path):
                if soname not in provided:
                    missing.setdefault(soname, []).append(path[len(root):])
    return missing


def host_library(soname):
    """Path of an aarch64 library with this soname on the host, or None."""
    output = subprocess.run(["ldconfig", "-p"], capture_output=True,
                            text=True).stdout
    for line in output.splitlines():
        fields = line.split()
        if fields and fields[0] == soname and "AArch64" in line:
            return fields[-1]
    return None


def copy_bridge(root):
    """Copy missing libraries into the bridge until nothing new is missing.

    Libraries copied into the bridge have needs of their own, so the scan
    repeats until it reaches a fixed point. Sonames the host does not have
    either are reported and left missing.
    """
    bridge = os.path.join(root, BRIDGE_DIR)
    os.makedirs(bridge, exist_ok=True)
    unavailable = set()
    while True:
        missing = missing_libraries(root)
        todo = [soname for soname in missing if soname not in unavailable]
        if not todo:
            return missing
        for soname in todo:
            source = host_library(soname)
            if source is None:
                unavailable.add(soname)
                continue
            subprocess.run(["cp", "-L", source, os.path.join(bridge, soname)],
                           check=True)
            print("bridged %s from %s" % (soname, source))


def main():
    if len(sys.argv) not in (2, 3) or (len(sys.argv) == 3 and
                                       sys.argv[2] != "--copy"):
        sys.exit(__doc__)
    root = os.path.abspath(sys.argv[1])
    if len(sys.argv) == 3:
        missing = copy_bridge(root)
    else:
        missing = missing_libraries(root)
    for soname, users in sorted(missing.items()):
        print("missing %s (needed by %s%s)" % (
            soname, ", ".join(sorted(users)[:3]),
            ", ..." if len(users) > 3 else ""))
    sys.exit(1 if missing else 0)


if __name__ == "__main__":
    main()
