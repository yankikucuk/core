#!/usr/bin/env python3
"""Collect the sources and patches for the aarch64 stage-0 image from the recipes.

Stage 0 builds Python 2.7 and PiSi on a Debian arm64 system. To stay faithful
to the distribution it does not pin its own versions: for every recipe listed
in RECIPES this script reads pspec.xml, downloads the first <Archive>,
verifies its sha1sum, and copies the recipe's patches with their strip-level
hints into the Docker build context. It also copies mirrors.conf from the pisi
recipe.

Usage:
    scripts/bootstrap/aarch64/prepare.py [context directory]

The context defaults to scripts/bootstrap/aarch64/context (ignored by git).
Runs on Python 3 with the standard library only.
"""

import hashlib
import os
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ElementTree

HERE = os.path.dirname(os.path.abspath(__file__))
REPOSITORY = os.path.abspath(os.path.join(HERE, "..", "..", ".."))

# Recipes stage 0 builds, in build order. The keys are the names build-stage0.sh uses.
RECIPES = [
    ("python", "system/base/python"),
    ("setuptools", "system/devel/python-setuptools"),
    ("six", "system/base/python-six"),
    ("piksemel", "system/base/piksemel"),
    ("pyliblzma", "system/base/python-pyliblzma"),
    ("cython", "system/devel/cython"),
    ("plyvel", "system/base/plyvel"),
    ("pycurl", "system/base/pycurl"),
    ("urlgrabber", "system/base/urlgrabber"),
    ("file", "system/base/file"),
    ("pisi", "system/base/pisi"),
]

# SourceForge answers browser-like clients with a bot page; identify as the
# fetcher PiSi itself uses.
USER_AGENT = "urlgrabber/4.0.0"

MIRRORS = {
    "gnu": "https://ftp.gnu.org/gnu/",
    "sourceforge": "https://downloads.sourceforge.net/",
    "cpan": "https://cpan.metacpan.org/",
    "gnome": "https://download.gnome.org/sources/",
    "kernel": "https://mirrors.edge.kernel.org/pub/",
}


def resolve(url):
    """Expand PiSi's mirrors:// scheme to a real URL."""
    if url.startswith("mirrors://"):
        name, rest = url[len("mirrors://"):].split("/", 1)
        return MIRRORS[name] + rest
    return url


def download(url, target):
    request = urllib.request.Request(resolve(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response, open(target, "wb") as out:
        shutil.copyfileobj(response, out)


def sha1(path):
    digest = hashlib.sha1()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def collect(name, recipe, context):
    spec = ElementTree.parse(os.path.join(REPOSITORY, recipe, "pspec.xml")).getroot()
    archive = spec.find("Source/Archive")
    url = archive.text.strip()
    expected = archive.get("sha1sum")
    source_dir = os.path.join(context, "sources", name)
    os.makedirs(source_dir, exist_ok=True)
    target = os.path.join(source_dir, os.path.basename(url.rstrip("/")))
    if not os.path.exists(target) or sha1(target) != expected:
        download(url, target)
    if sha1(target) != expected:
        raise SystemExit("%s: sha1 mismatch for %s" % (recipe, url))

    patch_dir = os.path.join(context, "patches", name)
    shutil.rmtree(patch_dir, ignore_errors=True)
    os.makedirs(patch_dir)
    series = []
    for index, patch in enumerate(spec.iter("Patch")):
        relative = patch.text.strip()
        flat = "%03d-%s" % (index, relative.replace("/", "_"))
        shutil.copy(os.path.join(REPOSITORY, recipe, "files", relative),
                    os.path.join(patch_dir, flat))
        compression = patch.get("compressionType", "")
        series.append("%s %s %s" % (patch.get("level", "0"), compression or "-", flat))
    with open(os.path.join(patch_dir, "series"), "w") as handle:
        handle.write("\n".join(series) + ("\n" if series else ""))
    print("%-11s %-40s %2d patches" % (name, os.path.basename(target), len(series)))


def main():
    context = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "context")
    for name, recipe in RECIPES:
        collect(name, recipe, context)
    shutil.copy(os.path.join(REPOSITORY, "system/base/pisi/files/mirrors.conf"),
                os.path.join(context, "mirrors.conf"))
    for helper in ("Dockerfile", "build-stage0.sh"):
        shutil.copy(os.path.join(HERE, helper), os.path.join(context, helper))
    print("context ready: %s" % context)


if __name__ == "__main__":
    main()
