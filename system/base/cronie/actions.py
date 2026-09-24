#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file https://www.gnu.org/licenses/gpl-3.0.txt

from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools
from pisi.actionsapi import get

def setup():
    # cronie 1.7 still declares callbacks with empty parameter lists, which
    # C23 (the GCC 15 default) reads as "no arguments"; build as C17 and
    # keep the one incompatible-pointer-type in src/user.c a warning.
    pisitools.cflags.add("-std=gnu17 -Wno-error=incompatible-pointer-types")

    # No systemd here: cronie is started by the COMAR service script, so the
    # unit directory is left out. anacron is enabled to run the daily, weekly
    # and monthly directories on machines that are not up around the clock.
    autotools.configure("--sbindir=/usr/sbin \
                         --sysconfdir=/etc \
                         --localstatedir=/var \
                         --with-pam \
                         --with-inotify \
                         --enable-anacron \
                         --enable-pie \
                         --enable-relro \
                         --without-selinux \
                         --without-systemd")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    # the directories run by /etc/crontab and anacron
    for directory in ("cron.d", "cron.hourly", "cron.daily", "cron.weekly", "cron.monthly"):
        pisitools.dodir("/etc/%s" % directory)
    pisitools.dodir("/var/spool/cron")
    pisitools.dodir("/var/spool/anacron")

    # anacron itself is triggered hourly from cron; contrib ships the hook
    pisitools.insinto("/etc/cron.hourly", "contrib/0anacron")
    pisitools.dodoc("AUTHORS", "COPYING", "COPYING.anacron", "ChangeLog", "NEWS", "README", "README.anacron")
