#!/bin/bash
# Stage 0 of the aarch64 bootstrap, run inside the Debian arm64 image.
#
# Builds Python 2.7, the Python modules PiSi imports and PiSi itself from the
# sources and patches that prepare.py collected from the recipes. Each step
# mirrors the build() and install() of the recipe named in its comment.
set -euo pipefail

CONTEXT=/bootstrap
WORK=/tmp/stage0
mkdir -p "$WORK"

# unpack <name>: extract the recipe's archive and enter its top directory
unpack() {
    local archive
    archive=$(ls "$CONTEXT/sources/$1"/*)
    rm -rf "$WORK/$1" && mkdir -p "$WORK/$1" && cd "$WORK/$1"
    case "$archive" in
        *.zip) python3 -m zipfile -e "$archive" . ;;
        *) tar -xf "$archive" ;;
    esac
    cd "$(ls -d */ | head -1)"
}

# patch_recipe <name>: apply the recipe's patches in pspec.xml order. PiSi
# detects the strip level itself; the level in pspec.xml is only a hint.
patch_recipe() {
    local series="$CONTEXT/patches/$1/series" hint compression file level
    [ -s "$series" ] || return 0
    while read -r hint compression file; do
        local path="$CONTEXT/patches/$1/$file" reader=cat
        [ "$compression" = xz ] && reader="xz -dc"
        local applied=no
        for level in "$hint" 1 0 2; do
            if $reader "$path" | patch -p"$level" --dry-run -s -f >/dev/null 2>&1; then
                $reader "$path" | patch -p"$level" -s -f
                applied=yes
                break
            fi
        done
        [ "$applied" = yes ] || { echo "patch does not apply: $1/$file"; return 1; }
    done < "$series"
}

# --- python (system/base/python)
unpack python && patch_recipe python
# The recipe's gcc15 patch assumes C23 (bool/false are keywords), the default
# of the GCC Pisi builds with; Debian's GCC 14 defaults to C17.
CFLAGS="-O2 -std=gnu23" ./configure --prefix=/usr --enable-shared \
    --with-system-expat --with-system-ffi --enable-unicode=ucs4 \
    --with-dbmliborder=gdbm:ndbm >/dev/null
make -j"$(nproc)" >/dev/null && make install >/dev/null
ldconfig && ln -sf python2.7 /usr/bin/python
python -c "import ssl, zlib, bz2, sqlite3, readline, ctypes"

# --- setuptools (system/devel/python-setuptools): bootstrap.py, then install
unpack setuptools && patch_recipe setuptools
python bootstrap.py >/dev/null && python setup.py -q install

# --- six (system/base/python-six); urlgrabber's setup.py imports it
unpack six && patch_recipe six && python setup.py -q install

# --- piksemel (system/base/piksemel)
unpack piksemel && patch_recipe piksemel && python setup.py -q install

# --- pyliblzma (system/base/python-pyliblzma), provides the "lzma" module
unpack pyliblzma && patch_recipe pyliblzma && python setup.py -q install

# --- cython (system/devel/cython), needed to build plyvel
unpack cython && patch_recipe cython && python setup.py -q install

# --- plyvel (system/base/plyvel): the recipe's build() runs make (cython)
unpack plyvel && patch_recipe plyvel && make >/dev/null && python setup.py -q install

# --- pycurl (system/base/pycurl): OpenSSL backend, pre-C23 sources
unpack pycurl && patch_recipe pycurl
PYCURL_SSL_LIBRARY=openssl \
CFLAGS="-std=gnu99 -Wno-error=declaration-missing-parameter-type" \
    python setup.py -q install --curl-config=/usr/bin/curl-config

# --- urlgrabber (system/base/urlgrabber)
unpack urlgrabber && patch_recipe urlgrabber && python setup.py -q install

# --- file (system/base/file): only its Python binding, magic.py
unpack file && patch_recipe file && (cd python && python setup.py -q install)

# --- pisi (system/base/pisi): v2.7.2 plus every patch of the recipe
unpack pisi && patch_recipe pisi
python setup.py -q install --install-lib=/usr/lib/pisilinux
echo /usr/lib/pisilinux > "$(python -c 'import site; print(site.getsitepackages()[0])')/pisilinux.pth"
ln -sf pisi-cli /usr/bin/pisi
mkdir -p /etc/pisi
cp pisi.conf-aarch64 /etc/pisi/pisi.conf
cp "$CONTEXT/mirrors.conf" /etc/pisi/mirrors.conf

python -c "import pisi.archinfo, piksemel, plyvel, lzma, magic, urlgrabber; print('stage 0 ready: pisi on %s' % pisi.archinfo.machine())"
rm -rf "$WORK"
