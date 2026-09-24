#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt.

from pisi.actionsapi import get
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import pythonmodules

def build():
    # suppress compiler warnings
    pisitools.cflags.add("-Wno-stringop-truncation")
    # fix unused direct dependency analysis
    shelltools.export("LDSHARED", "%s-gcc -Wl,-O1,--as-needed -shared -lbz2 -lpthread -ldl" % get.HOST())
    pythonmodules.compile()

def install():
    pythonmodules.install()