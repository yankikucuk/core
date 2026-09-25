#!/bin/bash
# Stage 2 of the Pisi GNU/Linux aarch64 bootstrap, part 2: run the package
# scripts (COMAR postInstall) that build-stage2-root.sh had to skip.
#
# Runs inside a container of the imported stage-2 root (see README.md):
#   docker exec pisi-s2 /work/scripts/bootstrap/aarch64/stage2-configure.sh
#
# "pisi configure-pending" needs COMAR, COMAR needs D-Bus, and PiSi talks to
# COMAR through comar-api. comar-api did not build in stage 1 (Debian's
# Python 2 has no dbus module), so it is built here, inside the root, where
# Pisi's own Python 2 and dbus-python are installed. Fetching its source needs
# the CA bundle, which is itself made by ca-certificates' postInstall; that
# one command is run by hand first to break the cycle.
set -e

WORK=/work

echo ">>> starting D-Bus and COMAR"
mkdir -p /run/dbus
dbus-uuidgen --ensure
pgrep -x dbus-daemon > /dev/null || dbus-daemon --system --fork
pgrep -x comar > /dev/null || (/usr/sbin/comar -t 0 -p > /var/log/comar-stage2.log 2>&1 &)
sleep 2

echo ">>> CA bundle (ca-certificates postInstall)"
/usr/sbin/update-ca-certificates --fresh > /dev/null

if ! pisi info comar-api 2>/dev/null | grep -q "^Installed package"; then
    echo ">>> building comar-api inside the root"
    rm -rf /tmp/comar-api && cp -r "$WORK/system/base/comar-api" /tmp/comar-api
    (cd /tmp/comar-api &&
     pisi build --ignore-sandbox --ignore-dependency -y pspec.xml > /var/log/comar-api-build.log 2>&1)
    pisi install --ignore-comar --ignore-dependency -y /tmp/comar-api/comar-api-*.pisi > /dev/null
fi

echo ">>> pisi configure-pending"
pisi configure-pending
pisi list-pending
