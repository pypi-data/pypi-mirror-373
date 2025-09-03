# micropytimer

Micropython friendly library to create timers that trigger functions

# Overview

This package implements a simple timer functionality for both python and micropython. Timers trigger a function when they expire. Timers can be set to expire either at an interval after they start or at a fixed expiration time. Useful for triggering an action after a period of inaction, checking for updates to some state, or causing actions to happen at fixed times of day.

Timers come in two types: Long and Short. Long timers have intervals in seconds or expirations in seconds since the beginning of the epoch. Short timers only work under micropython, and have intervals in milliseconds. Fixed expirations are trickier for short timers, since the time is measured since the device was turned on or the last time the device clock rolled over. Regardless of the timer type, the functions for interacting with them (``setup_timer``, ``start_timer``, etc.) are common to both.

By default, timers are one-shot. If a looping timer is needed, the the function that the timer triggers should include a call to the ``start_timer`` function.

# Installation

``pip install micropytimer``

# Example Setup

Examples of how to set up and use timers are shown in the ``example.py`` and ``example_util.py`` files included with the packing on GitHub, [here](https://github.com/goodeb/micropytimer). Timers should not be instantiated directly. For the functionality to work properly they need to be in the library's ``timer_registry``.  The ``setup_timer``  function should be used to create and register timers.

# Library Functions

All setup and interaction with timers should be done through the following functions.

* ``check_timers()``: Iterates through all registered timers and, if they are running and have expired, triggers their action. Called from program's main loop.

* ``setup_timer(name,timer_def)``: Adds a new timer to the timer registry. ``name`` is a string used to reference this timer in other functions like ``start_timer``. ``timer_def``  is a dictionary of the timer's attributes described in more detail in the next section.

* ``start_timer(name)``: Starts the timer given by ``name``.

* ``stop_timer(name)``: Stops the timer given by ``name`` without triggering its action.

* ``trigger_timer(name)``: Triggers the action for timer given by ``name`` before it expires and stops the timer.

* ``override_timer_expiration(name, interval)``: Overrides previous expiration time for timer given by ``name``and sets a new expiration time at a time from when the function is called given by ``interval``. Useful to sync a timer's expiration to the rollover of a unit of time like a minute or at the top of the hour.

* ``force_restart()``: Iterates through all registered timers and restarts any that are running.

* ``show_timers()``: Prints the names and attributes of all registered timers.

# Timer Definitions

Each timer is set up with a name and dictionary that contains all of its attributes. The possible attributes are:

* ``action: str`` The name of the function to be executed when the timer expires

* ``library: str`` The name of the library or local python file where the function to be executed can be found. If a local file do not include .py.

* ``args: str | list | dict | int | float`` The argument, or arguments if given as a list, for the function given by action. Because of how the code handles multiple arguments as a list, if the function needs a single list as an argument, it should be passed as a list of that list.

* ``running: str | bool | int`` Whether the timer is running when it is defined. Timers that are not running are not checked. A timer can be started at any time after it is defined using the ``start_timer()`` function.

* ``long: str | bool | int`` Whether the timer in question is a long timer with its interval measured in seconds. If not the timer is short, with an interval in milliseconds. Note that short timers only work under micropython.

+ ``interval: int`` The number of seconds for a long timer or millisecond for a short timer after starting when the timer will fire. Will override expiration.

* ``expiration: int | float`` For a long timer, a fixed clock time in seconds since epoch start when the timer will fire. For a short timer, a fixed clock time in milliseconds since the internal clock started or last rolled over. Will not be used if interval is also given.

