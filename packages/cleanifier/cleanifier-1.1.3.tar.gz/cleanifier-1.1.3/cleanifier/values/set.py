"""
fastcash.values.count

Provides a value set for counting k-mers up to a given maximum count.

Provides public constants:
- NAME="count"
- NVALUES
- RCMODE
and functions:
- get_value_from_name
- update
- is_compatible

Other provided attributes should be considered private, as they may change.
"""

from collections import namedtuple

from numba import njit, uint64

ValueInfo = namedtuple("ValueInfo", [
    "NAME",
    "NVALUES",
    "RCMODE",
    "get_value_from_name",
    "update",
    "is_compatible",
    "bits",
    ])


def initialize(rcmode="max"):

    def get_value_from_name(name, onetwo=1):
        return 1  # always one count

    @njit(nogil=True, locals=dict(
        old=uint64, new=uint64, updated=uint64))
    def update(old, new):
        return old

    @njit(nogil=True, locals=dict(observed=uint64, stored=uint64))
    def is_compatible(observed, stored):
        return True

    return ValueInfo(
        NAME="set",
        NVALUES=0,
        RCMODE=rcmode,
        get_value_from_name=get_value_from_name,
        update=update,
        is_compatible=is_compatible,
        bits=0,
        )
