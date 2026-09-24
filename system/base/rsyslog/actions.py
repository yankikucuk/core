#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License, version 3.
# See the file http://www.gnu.org/licenses/gpl.txt

from pisi.actionsapi import get
from pisi.actionsapi import autotools
from pisi.actionsapi import pisitools


def setup():
    # 8.26 dropped --enable-cached-man-pages, --enable-pmrfc3164sd,
    # --enable-sm_cust_bindcdr and --enable-zlib (zlib support is unconditional now).
    # libyaml lives in main and is only needed by the mmyaml module: keep core free of it.
    # impstats-push (new, on by default with impstats) needs protobuf-c, also main-only.
    #pisitools.cflags.add('-fpie -DSYSLOGD_PIDNAME=\\"syslogd.pid\\"')
    pisitools.ldflags.add("-pie -Wl,-z,relro -Wl,-z,now")

    autotools.configure("\
                         --sbindir=/usr/bin \
                         --disable-gui \
                         --disable-libyaml \
                         --disable-impstats-push \
                         --disable-mysql \
                         --disable-pgsql \
                         --disable-relp \
                         --disable-gnutls \
                         --disable-static \
                         --disable-rfc3195 \
                         --disable-omjournal \
                         --disable-testbench \
                         --disable-mmnormalize \
                         --disable-gssapi-krb5 \
                         --disable-generate-man-pages \
                         --disable-uuid \
                         --enable-mail \
                         --enable-imdiag \
                         --enable-imfile \
                         --enable-imptcp \
                         --enable-mmanon \
                         --enable-omprog \
                         --enable-mmaudit \
                         --enable-pmsnare \
                         --enable-impstats \
                         --enable-omstdout \
                         --enable-omuxsock \
                         --enable-largefile \
                         --enable-pmlastmsg \
                         --enable-mmjsonparse \
                         --enable-pmcisconames \
                         --enable-unlimited-select \
                         --enable-pmaixforwardedfrom \
                         --with-systemdsystemunitdir=no \
                        ")

    pisitools.dosed("libtool", " -shared ", " -Wl,-O1,--as-needed -shared ")

def build():
    autotools.make()

def install():
    autotools.rawInstall("DESTDIR=%s" % get.installDIR())

    pisitools.dodoc("COPYING*", "README", "AUTHORS", "ChangeLog")
    
    # create needed directory
    pisitools.dodir("/var/spool/rsyslog")
    pisitools.dodir("/var/empty/dev")
