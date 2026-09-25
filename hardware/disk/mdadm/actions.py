#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import get
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools

# mdadm.static for the initramfs, statically linked against glibc. (It was
# meant to use dietlibc through $GCC, but mdadm's Makefile only reads $CC,
# so it has always been a glibc build.)
def buildstatic():
    autotools.make("clean")
    autotools.make("CXFLAGS='%s -DNO_LIBUDEV' mdadm.static" % get.CFLAGS())
    #autotools.make("mdassemble.static")

    pisitools.insinto("/sbin", "mdadm.static")
    #pisitools.insinto("/sbin", "mdassemble.static")

def build():
    # fix build with gcc-4.9.0
    pisitools.dosed("Makefile", "(Wall) -Werror", "\\1")
    # Not sure about MDASSEMBLE_AUTO=1. Need to investigate.
    autotools.make("CXFLAGS='%s -DNO_LIBUDEV' SYSCONFDIR=/%s MDASSEMBLE_AUTO=1 mdadm mdmon" % (get.CFLAGS(), get.confDIR()))

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # Remove the udev file as its shipped with udev package
    # pisitools.remove("/lib/udev/rules.d/*")

    # Install config file
    pisitools.insinto("/etc", "documentation/mdadm.conf-example", "mdadm.conf")

    buildstatic()

    pisitools.dodoc("CHANGELOG*", "COPYING", "documentation/mdadm.conf-example", "misc/*")

