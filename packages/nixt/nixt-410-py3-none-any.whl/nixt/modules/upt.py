# This file is placed in the Public Domain.


"uptime"


import time


from ..runtime import STARTTIME
from ..command import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
