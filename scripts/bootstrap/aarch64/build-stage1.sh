#!/bin/bash
# Stage 1 of the aarch64 bootstrap: build core recipes into aarch64 packages
# inside the stage-0 image (see README.md).
#
# Usage, inside a container of pisi-aarch64-stage0 with the repository at
# /work (read-only) and an output directory at /out:
#   build-stage1.sh [recipe directory ...]
# Without arguments every recipe of the repository is built. For each recipe
# the packages go to /out/packages, the build log to /out/logs/<name>.log and
# one line per recipe to /out/status (PASS, FAIL, EXCLUDED or SKIP-DONE).
# Recipes that already have a PASS line are skipped, so the script can be
# rerun after fixing failures.
set -u
WORK=/work
OUT=/out
mkdir -p "$OUT/packages" "$OUT/logs"
touch "$OUT/status"

if [ $# -eq 0 ]; then
    set -- $(cd "$WORK" && find . -name pspec.xml -not -path './.git/*' \
             -not -path './scripts/*' | sed 's|^\./||; s|/pspec.xml$||' | sort)
fi

for recipe in "$@"; do
    name=$(basename "$recipe")
    if grep -q "^PASS $recipe\$" "$OUT/status"; then
        continue
    fi
    # /work is read-only, so the recipe is built from a copy. The copy keeps
    # the repository layout and every component.xml above the recipe:
    # PiSi takes the package's component (PartOf) from them.
    build="/tmp/build/$recipe"
    rm -rf "$build" && mkdir -p "$(dirname "$build")" && cp -r "$WORK/$recipe" "$build"
    dir=$(dirname "$recipe")
    while [ "$dir" != . ]; do
        [ -f "$WORK/$dir/component.xml" ] && cp "$WORK/$dir/component.xml" "/tmp/build/$dir/"
        dir=$(dirname "$dir")
    done
    (
        cd "$build" &&
        # Tests are skipped in stage 1: these packages only seed stage 2,
        # where everything is rebuilt against Pisi's own libraries and tested.
        pisi build --ignore-sandbox --ignore-safety --ignore-dependency \
                   --ignore-check -y pspec.xml
    ) > "$OUT/logs/$name.log" 2>&1
    if ls "$build"/*.pisi >/dev/null 2>&1; then
        mv "$build"/*.pisi "$OUT/packages/"
        result=PASS
    elif grep -q "avoids this package from building" "$OUT/logs/$name.log"; then
        result=EXCLUDED
    else
        result=FAIL
    fi
    sed -i "\| $recipe\$|d" "$OUT/status"
    echo "$result $recipe" >> "$OUT/status"
    echo "$result $recipe"
    rm -rf "$build" /var/pisi/"$name"-*
done
