"""
function.py - Defines built-in functions usable in query expressions.

This module provides a set of predefined utility functions that can be invoked from
within query expressions. These functions enable common operations such as determining
the length of a value or obtaining the current time.

Functions:
    - length(x): Returns the length of a string, list, or IP range/network.
    - now(): Returns the current UTC datetime.

These functions are registered in the `predefined_functions` dictionary and are
automatically available during query evaluation.

Example usage in query:
    length(some_field) > 3 or now() > 2024-01-01T00:00:00Z
"""

import datetime

from ipranges import IP4, IP6, IP4Net, IP4Range, IP6Net, IP6Range


def length(x):
    if isinstance(x, (list, str, IP4, IP4Net, IP4Range, IP6, IP6Net, IP6Range)):
        return len(x)
    raise TypeError(f"Function length is not defined for value {x}")


def now():
    return datetime.datetime.now(datetime.timezone.utc)


predefined_functions = {
    "length": length,
    "len": length,
    "now": now,
}
