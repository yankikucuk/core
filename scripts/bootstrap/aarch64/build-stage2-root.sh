#!/bin/bash
# Stage 2 of the Pisi GNU/Linux aarch64 bootstrap, part 1: assemble a Pisi
# root from the stage-1 packages and pack it as a tarball that Docker can
# import as an image.
#
# Runs inside the stage-0 container (see README.md):
#   docker exec pisi-a64 /work/scripts/bootstrap/aarch64/build-stage2-root.sh
#
# Input:  /out/packages/*.pisi  (stage 1)
# Output: /out/stage2-root.tar
#
# What it does, in order:
#   1. indexes the stage-1 packages as a local repository;
#   2. installs every package into an empty root, except the kernel image,
#      modules, firmware and initramfs tools, which a build root does not
#      need. COMAR is not running here, so package scripts are skipped
#      (--ignore-comar) and run later inside the root with
#      "pisi configure-pending" (stage2-configure.sh);
#      dependencies are not enforced because 33 recipes are still missing;
#   3. places baselayout's special files (passwd, group, ld.so.conf, ...),
#      the first step of baselayout's own postInstall, so that the root can
#      start D-Bus and COMAR at all;
#   4. copies the Debian libraries that stage-1 programs still link against
#      into /usr/lib/stage1-bridge (stage1-bridge.py). The bridge is removed
#      once core has been rebuilt inside the root.
set -e

HERE=$(dirname "$(readlink -f "$0")")
OUT=/out
REPO=/tmp/stage2-repo
ROOT=/tmp/stage2-root

echo ">>> indexing stage-1 packages"
rm -rf "$REPO" && mkdir -p "$REPO"
ln -s "$OUT"/packages/*.pisi "$REPO"/
pisi index --skip-signing --skip-sources -o "$REPO/pisi-index.xml" "$REPO" > /dev/null

echo ">>> installing into $ROOT"
rm -rf "$ROOT" && mkdir -p "$ROOT"
pisi add-repo stage1 "$REPO/pisi-index.xml.xz" -D "$ROOT" -y > /dev/null
packages=$(python3 - "$REPO/pisi-index.xml" <<'EOF'
import re
import sys
import xml.etree.ElementTree as ET

# Not needed to build packages: the kernel image and its documentation,
# out-of-tree modules, firmware, and the initramfs generators initrd and
# mkinitramfs, which conflict with busybox-mkinitcpio (only one of them can
# be installed). kernel-headers (the userspace API headers every C program
# needs) and kernel-module-headers stay.
skip = re.compile(r"^(kernel$|kernel-docs$|linux-firmware|module-|rtl88|initrd$|mkinitramfs$)")
index = ET.parse(sys.argv[1]).getroot()
names = sorted({package.findtext("Name") for package in index.findall("Package")})
print(" ".join(name for name in names if not skip.match(name)))
EOF
)
pisi install -D "$ROOT" --ignore-comar --ignore-dependency -y $packages > "$OUT/logs/stage2-install.log" 2>&1
pisi remove-repo stage1 -D "$ROOT" > /dev/null

echo ">>> baselayout special files"
for file in passwd shadow group fstab hosts ld.so.conf resolv.conf; do
    [ -e "$ROOT/etc/$file" ] || cp "$ROOT/usr/share/baselayout/$file" "$ROOT/etc/"
done

echo ">>> stage-1 library bridge"
echo /usr/lib/stage1-bridge > "$ROOT/etc/ld.so.conf.d/zz-stage1-bridge.conf"
python3 "$HERE/stage1-bridge.py" "$ROOT" --copy || true
ldconfig -r "$ROOT"

echo ">>> packing $OUT/stage2-root.tar"
tar -C "$ROOT" -cf "$OUT/stage2-root.tar" .
echo "stage-2 root ready"
