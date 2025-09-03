"""
example.py 2025-08-12 v 1.0

Author: Brent Goode

example code showing how to use micropytimer library

"""

from micropytimer import setup_timer, check_timers, show_timers
import time

timers = {"one_shot":{"interval":10,
                      "action":"fire_one_shot",
                      "library":"example_util",
                      "running":"True",
                      "long":"True",
                      "args":42},
          "repeating":{"interval":5,
                       "action":"fire_repeating",
                       "library":"example_util",
                       "running":1,
                       "long":1,
                       "args":[1,2]},
          "flipflop_A":{"interval":2,
                        "action":"fire_flipflop_A",
                        "library":"example_util",
                        "running":True,
                        "long":True}}
   
for name,timer_def in timers.items():
    setup_timer(name,timer_def)


# create a fixed time at the next time a new minute rolls over, and set a timer to fire at that time
now = time.localtime()
expiration_time = time.mktime((now[0], now[1], now[2], now[3], now[4], 0, now[6], now[7],now[8])) + 60

setup_timer('zero_seconds',{"expiration":expiration_time,
                            "action":"mark_minute",
                            "library":"example_util",
                            "running":True,
                            "long":True})

show_timers()

while True:
    check_timers()
