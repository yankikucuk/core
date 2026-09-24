#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools
from pisi.actionsapi import get

docdir = "/%s/%s" % (get.docDIR(), get.srcNAME())

shelltools.export("LC_ALL", "C")

def setup():
    # autoreconf breaks linker, graaaaaaaaggggghhhhhhh
    autotools.autoreconf("-fi")
    autotools.configure("--without-emacs \
                         --libexecdir=/usr/lib \
                         --enable-nls \
                         --disable-static \
                         --enable-shared \
                         --with-pic \
                         --disable-rpath \
                         --with-included-libcroco")

def build():
    autotools.make("GMSGFMT=../src/msgfmt")

def install():
    autotools.rawInstall("DESTDIR=%s docdir=/%s/html" % (get.installDIR(), docdir))

    # gettextize moved to gettext-tools/wizard in 1.0 and "make install"
    # places it in /usr/bin itself; copying it by hand is no longer needed.

    # Remove C# & Java stuff
    pisitools.remove("%s/html/examples/build-aux/csharp*" % docdir)
    pisitools.remove("%s/html/examples/build-aux/java*" % docdir)
    pisitools.removeDir("%s/html/examples/*java*" % docdir)
    pisitools.removeDir("%s/html/*java*" % docdir)

    pisitools.dodoc("AUTHORS", "COPYING", "ChangeLog*", "HACKING", "NEWS", "README*", "THANKS")

