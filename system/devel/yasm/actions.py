#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get


# 64-bit targets need position-independent code for the shared library.
# yasm 1.3 names enum constants false/true, which are keywords in C23 (the
# default of GCC 15 and later), so the sources are compiled as C17.
flags = "%s -std=gnu17%s" % (get.CFLAGS(), "" if get.isI686() else " -fPIC")

def setup():
    shelltools.export("CFLAGS", flags)
    
    # shelltools.system("./autogen.sh")

    autotools.configure("--enable-nls \
                         --disable-rpath")
                         # --enable-python \
                         # --enable-python-bindings \

def build():
    autotools.make()

# FIXME: python tests fail, others fail in 64bit, gentoo says tests are wrong
def check():
    autotools.make("-j1 check")

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("AUTHORS", "ChangeLog", "COPYING", "BSD.txt", "GNU_GPL-2.0", "GNU_LGPL-2.0", "Artistic.txt")

