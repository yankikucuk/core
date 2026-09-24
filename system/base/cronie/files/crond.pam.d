#%PAM-1.0
# PAM stack for crond: account and session checks for the job owner, as
# vixie-cron had, plus limits from pam_limits.
account required        pam_unix.so
auth    required        pam_unix.so
session required        pam_limits.so
session required        pam_unix.so
