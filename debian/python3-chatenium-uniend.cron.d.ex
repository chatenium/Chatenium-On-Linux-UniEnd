#
# Regular cron jobs for the python3-chatenium-uniend package.
#
0 4	* * *	root	[ -x /usr/bin/python3-chatenium-uniend_maintenance ] && /usr/bin/python3-chatenium-uniend_maintenance
