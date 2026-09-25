#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

def build():
    shelltools.export("KCONFIG_NOTIMESTAMP", "1")
    # files/config is written for x86_64 (-march=x86-64 in
    # CONFIG_EXTRA_CFLAGS); other architectures need their own baseline.
    if get.isAARCH64():
        pisitools.dosed(".config", "-march=x86-64", "-march=armv8-a")
    autotools.make()

def install():
    pisitools.insinto("/usr/lib/initcpio", "busybox")
