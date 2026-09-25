# Stage 0 of the Pisi GNU/Linux aarch64 bootstrap: a Debian arm64 system that
# runs PiSi natively. Python 2.7, the modules PiSi imports and PiSi itself are
# built from the recipes' own sources and patches (see prepare.py and
# build-stage0.sh). "pisi build" in this image produces aarch64 packages
# without emulation; those packages assemble the first Pisi aarch64 root.
#
# Build (from the repository root):
#   scripts/bootstrap/aarch64/prepare.py
#   docker build --platform linux/arm64 -t pisi-aarch64-stage0 scripts/bootstrap/aarch64/context
FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential autoconf automake autotools-dev libtool pkgconf \
        gettext autopoint intltool texinfo bison flex gawk perl python3 file cpio \
        xz-utils bzip2 zstd patch curl ca-certificates git \
        libssl-dev zlib1g-dev libbz2-dev libsqlite3-dev libreadline-dev \
        libncurses-dev libffi-dev libexpat1-dev libgdbm-dev liblzma-dev \
        libleveldb-dev libcurl4-openssl-dev libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Build dependencies of core recipes for stage 1. Until Pisi aarch64 packages
# exist, recipes build against Debian's tools and headers; only what core
# itself provides later (klibc, the kernel, Python 2 modules) is left to
# stage 2.
RUN apt-get update && apt-get install -y --no-install-recommends \
        meson ninja-build cmake bc gperf help2man re2c scdoc mandoc xsltproc \
        xutils-dev gtk-doc-tools python3-dev python3-build python3-installer \
        python3-wheel python3-setuptools python3-cryptography \
        libpci-dev libpam0g-dev uuid-dev libdbus-1-dev libudev-dev \
        libpcre2-dev libacl1-dev libattr1-dev libmd-dev libestr-dev \
        libgpg-error-dev libtirpc-dev libusb-1.0-0-dev libglib2.0-dev \
        libpipeline-dev libx11-dev libnl-3-dev libnl-genl-3-dev \
        libunistring-dev libgmp-dev libmpfr-dev libmpc-dev libfreetype-dev \
        libfuse3-dev libdevmapper-dev ss-dev comerr-dev libcmocka-dev \
        libaio-dev libpopt-dev swig liblz4-dev libisl-dev libarchive-dev \
        libbsd-dev flit python3-docutils doxygen xcb-proto \
        python3-xcbgen libgc-dev duktape-dev groff-base asciidoc-base \
        libaudit-dev libfastjson-dev libxml2-dev udev rsync \
    && rm -rf /var/lib/apt/lists/*

# Recipes are written for Pisi, where /bin/sh is bash; several use bash-only
# syntax such as brace expansion ("mkdir build-py{2,3}"), which Debian's dash
# does not expand.
RUN ln -sf bash /usr/bin/sh

# PiSi calls the compiler by the Pisi host triplet (aarch64-pc-linux-gnu-gcc);
# Debian names its tools aarch64-linux-gnu-*. pisi.actionsapi.autotools takes
# config.sub/config.guess from the gnuconfig package's directory, which Debian
# ships as autotools-dev under /usr/share/misc.
RUN cd /usr/bin && for tool in aarch64-linux-gnu-*; do \
        ln -sf "$tool" "aarch64-pc-linux-gnu-${tool#aarch64-linux-gnu-}"; \
    done \
    && mkdir -p /usr/share/gnuconfig \
    && ln -sf /usr/share/misc/config.sub /usr/share/gnuconfig/config.sub \
    && ln -sf /usr/share/misc/config.guess /usr/share/gnuconfig/config.guess

COPY . /bootstrap
RUN /bootstrap/build-stage0.sh
