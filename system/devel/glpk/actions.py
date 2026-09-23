#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    if get.buildTYPE() != "emul32":
        pisitools.flags.add("-fPIC")

    autotools.configure("--disable-static \
                         --with-gmp")

    pisitools.dosed("libtool", " -shared ", " -Wl,-O1,--as-needed -shared ")

def build():
    # The bundled minisat declares "typedef int bool", which is an error
    # under the C23 default of GCC 15; build with the C17 dialect.
    autotools.make("CFLAGS=\"-O2 -std=gnu17\" LDFLAGS=-s")

def install():
    autotools.install()

    pisitools.dodoc("README", "ChangeLog", "NEWS", "COPYING", "AUTHORS")

