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
