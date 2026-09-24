#!/usr/bin/python

import os
import os.path

def postInstall(fromVersion, fromRelease, toVersion, toRelease):
    # crontab must run setuid root to edit spool files it does not own;
    # the spool itself is only readable by root, as with vixie-cron
    os.system("/bin/chown root:root /usr/bin/crontab")
    os.system("/bin/chmod 04755 /usr/bin/crontab")
    os.system("/bin/chown root:root /var/spool/cron")
    os.system("/bin/chmod 0700 /var/spool/cron")
    os.system("/bin/chmod 0755 /etc/cron.d /etc/cron.hourly /etc/cron.daily /etc/cron.weekly /etc/cron.monthly")
    os.system("/bin/chmod 0644 /etc/pam.d/crond /etc/crontab")
