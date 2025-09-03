"""
example.py 2025-08-12 v 1.0

Author: Brent Goode

external utils code for example code showing how to use micropytimer library

"""

from micropytimer import setup_timer, start_timer

def fire_one_shot(arg):
    print(f'one shot timer fired with arg of {arg}')

def fire_repeating(a,b):
    print(f'repeating timer fired with two args {a} and {b}')
    start_timer('repeating')

def mark_minute():
    print('A new minute has turned over')

def fire_flipflop_A():
    print('flipflop timer A fires')
    start_timer('flipflop_B')

def fire_flipflop_B():
    print('flipflop timer B fires')
    start_timer('flipflop_A')

# Timers can be defined anywhere and don't have to be running to start with
setup_timer('flipflop_B',{"interval":2,
                          "action":"fire_flipflop_B",
                          "library":"example_util",
                          "long":True})


