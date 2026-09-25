#!/bin/bash
# Stage 2 of the Pisi GNU/Linux aarch64 bootstrap, part 3: rebuild recipes
# inside the stage-2 root with Pisi's own toolchain and libraries.
#
# Runs inside a container of the configured stage-2 root (see README.md):
#   docker exec pisi-s2 /work/scripts/bootstrap/aarch64/build-stage2.sh \
#       [--passes N] core:system/base/zlib main:programming/...
#
# Recipes are named "core:<path>" or "main:<path>"; core is mounted at /work,
# main at /main, output goes to /out (packages/, logs/, status). The stage-1
# packages are expected in /out/stage1-packages for rollbacks.
#
# Unlike stage 1, every package that builds is installed into the root right
# away (with its package scripts), so later recipes link against the rebuilt
# Pisi libraries instead of the stage-1 bridge. The sandbox (catbox) is on.
# Dependencies are still not enforced: the root does not contain every
# build dependency yet, and the order is given by the caller.
#
# --passes N     repeat failed recipes up to N times; a recipe that failed
#                because something later in the list was missing then gets
#                another chance (default 1).
set -e

OUT=/out
passes=1

while [ $# -gt 0 ]; do
    case "$1" in
        --passes) passes=$2; shift 2 ;;
        *) break ;;
    esac
done

mkdir -p "$OUT/packages" "$OUT/logs"
touch "$OUT/status"

# PiSi must keep working after every install: its own Python modules and the
# libraries behind them come from core packages that are being rebuilt.
pisi_works() {
    pisi --version > /dev/null &&
        python -c "import pisi, plyvel, piksemel, pycurl, urlgrabber, comar"
}

# Reinstall the stage-1 builds of the packages in the given .pisi files.
restore_stage1() {
    local file package stage1
    for file in "$@"; do
        package=$(basename "$file" | sed -E 's/-[^-]+-[0-9]+-p[0-9]+-[^-]+\.pisi$//')
        stage1=$(ls "$OUT/stage1-packages/$package"-[0-9]*.pisi 2> /dev/null | tail -1)
        [ -n "$stage1" ] && pisi install --reinstall --ignore-dependency -y "$stage1"
    done
}

build_one() {
    local spec=$1 repo=${1%%:*} recipe=${1#*:} base name build dir result
    case "$repo" in
        core) base=/work ;;
        main) base=/main ;;
        *) echo "unknown repository in $spec" >&2; return 1 ;;
    esac
    name=$(basename "$recipe")
    build="/tmp/stage2/$repo/$recipe"
    # /work and /main are read-only: build from a copy that keeps the
    # repository layout and every component.xml above the recipe (PiSi
    # reads the package's PartOf from them).
    rm -rf "/tmp/stage2/$repo" && mkdir -p "$(dirname "$build")"
    cp -r "$base/$recipe" "$build"
    dir=$(dirname "$recipe")
    while [ "$dir" != . ]; do
        [ -f "$base/$dir/component.xml" ] && cp "$base/$dir/component.xml" "/tmp/stage2/$repo/$dir/"
        dir=$(dirname "$dir")
    done
    log="$OUT/logs/$repo-$name.log"
    # retries append, so the first failure's reason is kept
    echo "===== $(date -u '+%F %T') attempt $spec" >> "$log"
    (
        cd "$build" &&
        pisi build --ignore-safety --ignore-dependency -y pspec.xml
    ) >> "$log" 2>&1 || true
    if ls "$build"/*.pisi > /dev/null 2>&1; then
        # Install what was built before the next recipe needs it.
        if ! pisi install --ignore-dependency -y "$build"/*.pisi >> "$log" 2>&1; then
            result=INSTALL-FAIL
        elif ! pisi_works >> "$log" 2>&1; then
            # A rebuilt library broke PiSi itself (it happened with plyvel
            # linked against a leveldb the root cannot load). Put the stage-1
            # packages back and keep going.
            restore_stage1 "$build"/*.pisi >> "$log" 2>&1
            result=BREAKS-PISI
        else
            result=PASS
        fi
        mv "$build"/*.pisi "$OUT/packages/"
    elif grep -q "avoids this package from building" "$OUT/logs/$repo-$name.log"; then
        result=EXCLUDED
    else
        result=FAIL
    fi
    sed -i "\| $spec\$|d" "$OUT/status"
    echo "$result $spec" >> "$OUT/status"
    echo "$result $spec"
    rm -rf "/tmp/stage2/$repo" /var/pisi/"$name"-*
    [ "$result" = PASS ] || [ "$result" = EXCLUDED ]
}

pending=("$@")
for ((pass = 1; pass <= passes && ${#pending[@]} > 0; pass++)); do
    failed=()
    for spec in "${pending[@]}"; do
        grep -q "^PASS $spec\$" "$OUT/status" && continue
        build_one "$spec" || failed+=("$spec")
    done
    [ ${#failed[@]} -lt ${#pending[@]} ] || break   # no progress
    pending=("${failed[@]}")
done
