#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file https://www.gnu.org/licenses/gpl-3.0.txt

from pisi.actionsapi import mesontools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

def setup():
    # The search path must list every directory the distribution installs
    # .pc files into; /usr/share/pkgconfig holds architecture-independent ones.
    mesontools.configure("-Dwith-pkg-config-dir=/usr/lib/pkgconfig:/usr/share/pkgconfig \
                          -Dwith-system-libdir=/usr/lib \
                          -Dwith-system-includedir=/usr/include")

def build():
    mesontools.build()

def install():
    mesontools.install()

    # pkg-config compatibility: build systems and the recipes in this
    # repository call pkg-config, which pkgconf implements when invoked
    # under that name.
    pisitools.dosym("pkgconf", "/usr/bin/pkg-config")
    pisitools.dosym("pkgconf.1", "/usr/share/man/man1/pkg-config.1")

    # the directory for architecture-independent .pc files must exist even
    # when empty, so that packages installing into it do not own it twice
    pisitools.dodir("/usr/share/pkgconfig")

    pisitools.dodoc("AUTHORS", "COPYING", "README.md", "NEWS")
