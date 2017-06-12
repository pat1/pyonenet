#
# Regular cron jobs for the pyonenet package
#
0 4	* * *	root	[ -x /usr/bin/pyonenet_maintenance ] && /usr/bin/pyonenet_maintenance
