#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    autotools.autoreconf("-vfi")
    # less 710 installs lessecho and the OSC 8 helper under libexecdir;
    # the repository rule is --libexecdir=/usr/lib.
    autotools.configure("--libexecdir=/usr/lib")

def build():
    autotools.make()

def install():
    autotools.rawInstall('DESTDIR="%s"' % get.installDIR())

    # Since less 582 there is no lesskey binary: less reads .lesskey files
    # itself; the lesskey(1) manual is installed by "make install" as lesskey.5.
    pisitools.newman("less.nro", "less.1")

    pisitools.dodoc("NEWS", "README", "COPYING")
