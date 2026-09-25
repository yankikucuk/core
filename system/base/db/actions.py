#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

WorkDir = "db-%s/build_unix" % get.srcVERSION()

def setup():
    # atomic.h declares its own __atomic_compare_exchange, which collides
    # with the GCC built-in of the same name; every distribution renames
    # it. Done with dosed because the build runs from build_unix and PiSi
    # applies patches relative to that directory.
    pisitools.dosed("../src/dbinc/atomic.h", "__atomic_compare_exchange\\(", "__atomic_compare_exchange_db(")
    # 5.3 predates C23: its headers declare functions with empty parameter
    # lists, which GCC 15's default dialect reads as (void); build as C17.
    pisitools.cflags.add("-std=gnu17")

    # The 2013 release ships a config.guess that predates aarch64 ("cannot
    # guess build type"); use the current one from gnuconfig.
    for f in ("config.guess", "config.sub"):
        shelltools.copy("/usr/share/gnuconfig/%s" % f, "../dist/%s" % f)

    pisitools.ldflags.add("-Wl,--default-symver -lpthread")
    shelltools.system("../dist/configure \
                       --prefix=/usr \
                       --mandir=/usr/share/man \
                       --infodir=/usr/share/info \
                       --datadir=/usr/share \
                       --sysconfdir=/etc \
                       --localstatedir=/var/lib \
                       --libdir=/usr/lib \
                       --with-mutex=POSIX/pthreads \
                       --enable-compat185 \
                       --with-uniquename \
                       --enable-cxx \
                       --enable-dbm \
                       --disable-tcl \
                       --disable-java \
                       --disable-static \
                       --disable-test")

def build():
    autotools.make()

def install():
    autotools.install('libdir="%s/usr/lib"' % get.installDIR())

    # Move docs
    pisitools.domove("/usr/docs/", "/usr/share/doc/%s/html/" % get.srcNAME())
