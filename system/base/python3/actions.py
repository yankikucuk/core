#!/usr/bin/python
# -*- coding: utf-8 -*-
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from pisi.actionsapi import get
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools

def setup():
    #shelltools.system("echo -e '\033[0;36mBuilding Bzip2\033[0m' ")
    #shelltools.makedirs("%s/temp/lib" %get.workDIR())
    #shelltools.cd("bzip2-1.0.8")
    #autotools.make('CC=%s AR=%s RANLIB=%s CFLAGS="%s -D_FILE_OFFSET_BITS=64 -fPIC" libbz2.a' % (get.CC(), get.AR(), get.RANLIB(), get.CFLAGS()))
    #shelltools.system("cp libbz2.a %s/temp/lib/libbz2.a" % get.workDIR())
    #shelltools.cd("..")
    
    pisitools.flags.add("-fwrapv")

    # Only the bundled expat is left to remove: the macOS-only _ctypes
    # directories (darwin, libffi_osx) were dropped from the source tree.
    shelltools.unlinkDir("Modules/expat")
    # shelltools.unlinkDir("Modules/_decimal/libmpdec")
    
    #shelltools.export("CFLAGS", "-I%s/temp/include -O3" %get.workDIR())
    #shelltools.export("LDFLAGS", "-L%s/temp/lib -lbz2 -lpthread -ldl" %get.workDIR())
    # fix unused direct dependency analysis; the host triplet comes from
    # pisi.conf so the same line works on every architecture
    autotools.rawConfigure("LDSHARED='%s-gcc -Wl,-O1,--as-needed -shared -lpthread'\
                            --prefix=/usr \
                            --enable-shared \
                            --with-computed-gotos \
                            --enable-ipv6 \
                            --with-system-expat \
                            --with-dbmliborder=gdbm:ndbm \
                            --with-system-ffi \
                            --enable-loadable-sqlite-extensions \
                            --with-tzpath=/usr/share/zoneinfo \
                            --without-ensurepip" % get.HOST())
                            # --with-system-libmpdec \

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())
    # 2to3 and the cgi module were removed from the standard library in 3.13,
    # so there is nothing to delete or to patch any more.
    pisitools.dodoc("LICENSE", "README.*")
    
    pisitools.removeDir("/usr/lib/python3.14/idlelib")
    pisitools.removeDir("/usr/lib/python3.14/tkinter")
    pisitools.removeDir("/usr/lib/python3.14/turtledemo")
    pisitools.remove("/usr/bin/idle3*")
    # pisitools.remove("/usr/lib/libpython3.14.a")
