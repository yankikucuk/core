from comar.service import *

serviceType = "local"
serviceDesc = _({"en": "Cron Task Scheduler",
                 "tr": "Cron Görev Zamanlayıcı"})
serviceDefault = "on"

@synchronized
def start():
    # crond forks itself and writes its pid file; no -n (foreground) here
    startService(command="/usr/sbin/crond",
                 pidfile="/run/crond.pid",
                 donotify=True)

@synchronized
def stop():
    stopService(pidfile="/run/crond.pid",
                donotify=True)

def status():
    return isServiceRunning("/run/crond.pid")
