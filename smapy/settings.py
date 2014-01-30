# -*- coding: utf-8 -*-
#!/usr/bin/env python

"""smapy preferences"""

# Current local time offset in seconds
import time
def local_time_offset(t=None):
    '''Return offset of local zone from GMT, either at present or at time t.'''
    if t is None:
        t = time.time()

    if time.localtime(t).tm_isdst and time.daylight:
        return -time.altzone
    else:
        return -time.timezone

# If script works on server - correct timezone by hands
ADDITIONAL_TIME_OFFSET = 0

TIME_OFFSET = local_time_offset() + ADDITIONAL_TIME_OFFSET

u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s] %(message)s'
u'[%(asctime)s] %(levelname)-8s %(message)s'

# Logging basics
import logging
logging.basicConfig(format = u'[%(asctime)s] %(levelname)-8s %(message)s',
                    level = logging.DEBUG)