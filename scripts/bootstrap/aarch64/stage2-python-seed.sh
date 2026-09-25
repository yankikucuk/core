#!/bin/bash
# Stage 2 of the Pisi GNU/Linux aarch64 bootstrap: seed for the Python 3
# build chain.
#
# PiSi builds Python 3 recipes with "python3 -m build" and installs them with
# "python3 -m installer" (pisi.actionsapi.python3modules). Those modules are
# packaged themselves (python3-build, python3-installer, ... in main) and are
# built the same way, and python3-setuptools removes its vendored copies and
# depends on the separately packaged ones, which in turn build with
# setuptools. A fresh system therefore cannot build any of them.
#
# The seed breaks the cycle the way other distributions do: the pure-Python
# build tools are built from the sources their recipes use (URL and sha1sum
# from each pspec.xml) with their own in-tree backends and installed into the
# system site-packages, without PiSi. The recipes of the chain then build
# normally and their packages overwrite the seed files.
#
#   stage2-python-seed.sh           install the seed, record its files in
#                                   /var/lib/python-seed.files
#   stage2-python-seed.sh --check   list seed files that no package owns yet;
#                                   exits 1 if there are any
#   stage2-python-seed.sh --clean   delete the seed files no package owns
#
# The seed is temporary like the stage-1 library bridge. Once the chain is
# built, what no package owns is seed-only: bytecode compiled from the seed,
# and setuptools' vendored copies, which the Pisi recipe removes on purpose.
# --clean deletes those, and --check must then come back empty.
set -e

CORE=/work
MAIN=/main
SEED=/opt/python-seed
FILES=/var/lib/python-seed.files
SITE=$(python3 -c 'import sysconfig; print(sysconfig.get_path("purelib"))')

if [ "$1" = --check ] || [ "$1" = --clean ]; then
    unowned=0
    while read -r file; do
        [ -f "$file" ] || continue
        if ! pisi search-file "$file" 2> /dev/null | grep -q "has file"; then
            if [ "$1" = --clean ]; then
                rm -f "$file"
            else
                echo "not owned by any package: $file"
                unowned=1
            fi
        fi
    done < "$FILES"
    # directories the removed files leave empty
    [ "$1" = --clean ] && find "$SITE" -depth -type d -empty -delete
    exit $unowned
fi

# recipe directory and the Python package (import name) it provides, in the
# order they can be built: flit_core builds itself, all but setuptools use
# flit_core as their backend, setuptools builds itself with the build
# frontend installed before it.
RECIPES="
$MAIN/programming/language/python3/python3-flit-core flit_core
$MAIN/programming/language/python3/python3-installer installer
$CORE/programming/language/python3/python3-packaging packaging
$MAIN/programming/language/python3/python3-pyproject-hooks pyproject_hooks
$MAIN/programming/language/python3/python3-build build
$CORE/programming/language/python3/python3-setuptools setuptools
$MAIN/programming/language/python3/python3-wheel wheel
"

# Fetch and unpack the first archive of a recipe into $SEED/<module>.
fetch_source() {
    local recipe=$1 module=$2 sha1 url archive
    read -r sha1 url < <(python3 - "$recipe/pspec.xml" <<'EOF'
import sys
import xml.etree.ElementTree as ET
archive = ET.parse(sys.argv[1]).getroot().find("Source/Archive")
print(archive.get("sha1sum"), archive.text.strip())
EOF
)
    archive="$SEED/archives/$module.tar"
    if [ ! -f "$archive" ] || ! echo "$sha1  $archive" | sha1sum -c --quiet 2> /dev/null; then
        # curl is not in the root yet (it did not build in stage 1)
        python3 -c 'import sys, urllib.request; urllib.request.urlretrieve(sys.argv[1], sys.argv[2])' "$url" "$archive"
        echo "$sha1  $archive" | sha1sum -c --quiet
    fi
    rm -rf "${SEED:?}/$module" && mkdir -p "$SEED/$module"
    tar -xf "$archive" -C "$SEED/$module" --strip-components=1
}

mkdir -p "$SEED/archives" "$SEED/wheels"
while read -r recipe module; do
    [ -n "$recipe" ] && fetch_source "$recipe" "$module"
done <<< "$RECIPES"

before=$(mktemp)
find "$SITE" /usr/bin | sort > "$before"

while read -r recipe module; do
    [ -n "$recipe" ] || continue
    # rerunnable: a module that is already importable (seeded before, or
    # installed as a package) is left alone
    if python3 -c "import $module" 2> /dev/null; then
        echo ">>> seed: $module (already present)"
        continue
    fi
    echo ">>> seed: $module"
    source_dir="$SEED/$module"
    # flit's monorepo keeps flit_core in a subdirectory
    [ "$module" = flit_core ] && source_dir="$SEED/$module/flit_core"
    rm -f "$SEED"/wheels/*.whl
    if [ "$module" = setuptools ]; then
        # setuptools is its own backend; build, packaging and
        # pyproject_hooks are installed by now
        (cd "$source_dir" && python3 -m build --wheel --no-isolation \
                                              --outdir "$SEED/wheels" > /dev/null)
    else
        # every other seed uses the flit_core backend, whose own wheel
        # builder needs no build frontend
        (cd "$source_dir" && python3 -m flit_core.wheel --outdir "$SEED/wheels" > /dev/null)
    fi
    # installer is used from its source tree until it is installed itself
    PYTHONPATH="$SEED/installer/src" python3 -m installer "$SEED"/wheels/*.whl
done <<< "$RECIPES"

touch "$FILES"
find "$SITE" /usr/bin | sort | comm -13 "$before" - | sort -u - "$FILES" -o "$FILES"
rm -f "$before"
echo "seed installed: $(wc -l < "$FILES") files recorded in $FILES"
