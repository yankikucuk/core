#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/copyleft/gpl.txt

from pisi.actionsapi import get
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import shelltools

#WorkDir="grub-%s" % (get.srcVERSION().replace("_", "~"))



# GRUB platforms per architecture. The main source tree is configured for
# MAIN_PLATFORM/MAIN_TARGET; when EFI_TARGET is set, a copy of the tree is
# built for EFI as well and only its modules are installed.
#   x86_64:  BIOS (pc, i386 target) + UEFI (x86_64-efi)
#   aarch64: UEFI only (arm64-efi), the one firmware interface arm64 has
if get.isAARCH64():
    MAIN_PLATFORM, MAIN_TARGET, EFI_TARGET = "efi", "arm64", None
else:
    MAIN_PLATFORM, MAIN_TARGET, EFI_TARGET = "pc", "i386", "x86_64"

def configure_platform(platform, target):
    autotools.configure("--disable-werror \
                         --with-bootdir='/boot' \
                         --with-grubdir=grub2 \
                         --program-transform-name='s,grub,grub2,'\
                         --program-prefix= \
                         --with-platform=%s \
                         --target='%s' \
                         --htmldir='/usr/share/doc/grub2/html' " % (platform, target))

def setup():
    shelltools.export("PYTHON", "/usr/bin/python3")
    shelltools.copy("../unifont*.bdf", "./unifont.bdf")
    # shelltools.export("GRUB_CONTRIB", "%s/grub-2.06/grub-extras" % (get.workDIR()))

    pisitools.cflags.remove("-fstack-protector", "-fasynchronous-unwind-tables", "-fexceptions", "-fPIC")
    pisitools.cflags.sub("\s?(-O[\ds]|-D_FORTIFY_SOURCE=\d)\s?", " ")

    #pisitools.dosed('util/grub-mkconfig.in', 'GRUB_DISABLE_OS_PROBER="true"', 'GRUB_DISABLE_OS_PROBER="false"')
    #shelltools.system("./linguas.sh")
    #shelltools.system("./bootstrap")
    #shelltools.system('echo "Make translations reproducible..."')
    #shelltools.system("sed -i '1i /^PO-Revision-Date:/ d' po/*.sed")
    if EFI_TARGET:
        shelltools.copytree("../grub-%s" % (get.srcVERSION().replace("_", "~")), "../grub-%s-efi" % get.srcVERSION())

    autotools.autoreconf("-fi")
    configure_platform(MAIN_PLATFORM, MAIN_TARGET)

    if EFI_TARGET:
        shelltools.cd("../grub-%s-efi" % get.srcVERSION())
        autotools.autoreconf("-fi")
        configure_platform("efi", EFI_TARGET)


    shelltools.cd("..")


def build():
    #make-dist for creating all updated translation files
    #autotools.make("dist")
    autotools.make()

    if EFI_TARGET:
        shelltools.cd("../grub-%s-efi" % get.srcVERSION())
        autotools.make()
        shelltools.cd("..")

def install():
    # Install unicode.pf2 using downloaded font source.
    #shelltools.system("./grub-mkfont -o unicode.pf2 unifont.bdf")

    # Create directory for grub.cfg file
    #pisitools.dodir("/boot/grub2")

    #pisitools.insinto("/boot/grub2", "unicode.pf2")

    # Insall our theme
    pisitools.insinto("/usr/share/grub/themes/pisilinux","themes/Pisilinux2.4-Grub2-Themes-1.3/*")

    #remove -r 0x0-0x7F entries to fix ugly fonts or find a suitable range parameter -r ***
    shelltools.system("./grub-mkfont -o DejaVuSans-10.pf2 -r 0x0-0x7F -s 10 /usr/share/fonts/dejavu/DejaVuSans.ttf")
    shelltools.system("./grub-mkfont -o DejaVuSans-12.pf2 -r 0x0-0x7F -s 12 /usr/share/fonts/dejavu/DejaVuSans.ttf")
    shelltools.system("./grub-mkfont -o DejaVuSans-14.pf2 -r 0x0-0x7F -s 14 /usr/share/fonts/dejavu/DejaVuSans.ttf")
    shelltools.system("./grub-mkfont -o DejaVuSans-16.pf2 -r 0x0-0x7F -s 16 /usr/share/fonts/dejavu/DejaVuSans.ttf")
    shelltools.system("./grub-mkfont -o DejaVuSans-Bold-14.pf2 -r 0x0-0x7F -s 14 /usr/share/fonts/dejavu/DejaVuSans-Bold.ttf")
    shelltools.system("./grub-mkfont -o DejaVuSans-Mono-14.pf2 -r 0x0-0x7F -s 14 /usr/share/fonts/dejavu/DejaVuSansMono.ttf")
    shelltools.copy("ascii.pf2","%s/usr/share/grub/themes/pisilinux" % get.installDIR())

    # Do not install auto generated dejavu* fonts
    fonts=["DejaVuSans-10.pf2" , "DejaVuSans-12.pf2" , "DejaVuSans-14.pf2" , "DejaVuSans-16.pf2" , "DejaVuSans-Mono-14.pf2", "DejaVuSans-Bold-14.pf2"]
    for font in fonts:
        shelltools.copy(font,"%s/usr/share/grub/themes/pisilinux" % get.installDIR())

    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("ABOUT-NLS", "AUTHORS", "BUGS", "COPYING", "TODO", "README")
    
    if EFI_TARGET:
        # the second tree only contributes its EFI modules
        shelltools.cd("../grub-%s-efi" % get.srcVERSION())
        autotools.rawInstall("DESTDIR=%s/efi" % get.installDIR())
        shelltools.copytree("/%s/efi/usr/lib/grub/%s-efi" % (get.installDIR(), EFI_TARGET), "%s/usr/lib/grub/%s-efi" % (get.installDIR(), EFI_TARGET))
        pisitools.removeDir("/efi")



