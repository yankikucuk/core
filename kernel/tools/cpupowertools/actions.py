#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

# directory name of the x86 debug tools under tools/power/cpupower/debug
cpupower_arch = get.kernelARCH()

def build():
    # Build cpupowertools
    shelltools.cd("tools/power/cpupower")
    autotools.make("CPUFREQ_BENCH=false")
    # centrino-decode and powernow-k8-decode read Intel/AMD MSRs: x86 only
    if get.isX86():
        autotools.make("-C debug/%s centrino-decode powernow-k8-decode" % cpupower_arch)

def install():
    # Install cpupowertools stuff
    shelltools.cd("tools/power/cpupower")
    autotools.install("DESTDIR=%s libdir=/usr/lib mandir=/%s CPUFREQ_BENCH=false" % (get.installDIR(), get.manDIR()))

    # built only on x86, see build()
    if get.isX86():
        pisitools.dobin("debug/%s/centrino-decode" % cpupower_arch)
        pisitools.dobin("debug/%s/powernow-k8-decode" % cpupower_arch)