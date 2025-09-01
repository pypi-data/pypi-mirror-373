"""
filter_windowed_cuckoo:
a cuckoo filter with window (overlapping) layout
"""


from collections import namedtuple
from math import ceil

import numpy as np
from numpy.random import randint
from numba import njit, int64, uint64

from .mathutils import bitsfor
from .cuckoo_filter_utils import compile_lookup, compile_get_empty_slot, compile_load_value, compile_store_value
from .lowlevel import debug  # the global debugging functions
from .lowlevel.bitarray import bitarray
from .hashfunctions import compile_get_bucket
from .subtable_hashfunctions import populate_hashfunc_tuple

WindowedCuckooFilter = namedtuple("WindowedCuckooFilter", [
    # attributes
    "universe",
    "target_fpr",
    "nsubfilters",
    "nwindows_per_subfilter",
    "nslots",
    "windowsize",
    "subfilter_hashfunc_str",
    "fingerprint_hashfunc_str",
    "window_hashfunc_str",
    "offset_hashfunc_str",
    "maxsteps",
    "filtertype",
    "filterbits",
    "mem_bytes",
    "array",

    # public API methods; example: f.store_new(f.array, canonical_code)
    "insert",  # (filter:uint64[:], key:uint64, value:uint64)
    "lookup",  # (filter:uint64[:], key:uint64) -> boolean
    "get_value",  # (filter:uint64[:], key:uint64) -> boolean
    "get_fpr",  # (filter:uint64[:]) -> float[:]
    "get_fill",  # (filter:uint64[:]) -> float[:]
    "print_statistics",  # (filter:uint64[:]) -> None

    # private API methods (see below)
    "private",
])

WindowedCuckooFilter_private = namedtuple("WindowedCuckooFilter_private", [
    # private API methods, may change !
    "is_slot_empty_at",
    "get_empty_slot",
    "set_offset_choice_fingerprint_at",
    "get_offset_choice_fingerprint_at",
    "compute_windows_for_key",
    "compute_windows_for_fingerprint",
    "insert_in_window",
    "store_fingerprint",
    "get_slot_bits",
    "get_window_bits",
    "get_subfilter",
    "lookup_in_subfilter",  # (table:uint64[:], subfilter:uint64, key:uint64) -> uint64
    "insert_in_subfilter",  # (table:uint64[:], subfilter:uint64, key:uint64, value:uint64)
    "lookup_and_insert_in_subfilter",  # (table:uint64[:], subfilter:uint64, key:uint64, value:uint64)
    "window_bits",
    "shm",  # shared memory object
    # API methods to replace hash table by cuckoo filter
    "update_ssk"
])


def create_WindowedCuckooFilter(d):
    """Return CuckooFilter initialized from values in dictionary d"""
    # The given d does not need to provide mem_bytes; it is computed here.
    # The given d is copied and reduced to the required fields.
    # The hashfuncs tuple is reduced to a single ASCII bytestring.
    d0 = dict(d)
    mem_bytes = 0
    mem_bytes += d0['array'].nbytes
    d0['mem_bytes'] = mem_bytes
    private = {name: d0[name] for name in WindowedCuckooFilter_private._fields}
    d0['private'] = WindowedCuckooFilter_private(**private)
    d1 = {name: d0[name] for name in WindowedCuckooFilter._fields}
    return WindowedCuckooFilter(**d1)


def build_from_info(filterinfo, init=True, shm=None):
    assert filterinfo['filtertype'] == "windowed_cuckoo"
    universe = filterinfo['universe']
    nsubfilters = filterinfo['nsubfilters']
    nslots = filterinfo['nslots']
    windowsize = filterinfo['windowsize']
    target_fpr = filterinfo['target_fpr']
    maxsteps = filterinfo['maxsteps']
    subfilter_hashfunc_str = filterinfo['subfilter_hashfunc_str']
    fingerprint_hashfunc_str = filterinfo['fingerprint_hashfunc_str']
    window_hashfunc_str = filterinfo['window_hashfunc_str']
    offset_hashfunc_str = filterinfo['offset_hashfunc_str']
    fltr = build_filter(
        universe, nsubfilters, nslots, windowsize, target_fpr,
        maxsteps=maxsteps,
        subfilter_hashfunc_str=subfilter_hashfunc_str,
        fingerprint_hashfunc_str=fingerprint_hashfunc_str,
        window_hashfunc_str=window_hashfunc_str,
        offset_hashfunc_str=offset_hashfunc_str,
        init=init, shm=shm,
    )
    return fltr


def build_filter(
    universe, nsubfilters, nslots, windowsize, target_fpr, *,
    maxsteps=5_000,
    subfilter_hashfunc_str=None,
    fingerprint_hashfunc_str=None,
    window_hashfunc_str=None,
    offset_hashfunc_str=None,
    init=True, shm=None,
):
    """
    Allocate an array and compile access methods for a cuckoo filter.
    Return an CuckooFilter object.
    """

    # Get debug printing functions and set basic properties
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    filtertype = "windowed_cuckoo"

    fingerprint_size = uint64(target_fpr)
    assert fingerprint_size < 62  # 1 bit to store which hash position is used and 1 bit for offset
    nfingerprints = uint64(2**fingerprint_size - 1)  # 0...0 for empty slots
    # bits: msb:choice_bit,offset_bits,fingerprint_bits:lsb, fpr = 2**fingerprint_size
    window_bits = bitsfor(windowsize)
    fingerprint_mask = uint64(2**fingerprint_size - 1)
    choice_mask = uint64(2**(fingerprint_size + window_bits))
    slot_mask = uint64((2**(window_bits) - 1) << fingerprint_size)

    debugprint1(f"- Using {nsubfilters} subfilters.")
    nslots_per_subfilter = uint64(ceil(nslots / nsubfilters))
    nwindows_per_subfilter = uint64(nslots_per_subfilter - windowsize + 1)
    nslots = uint64(nslots_per_subfilter * nsubfilters)
    debugprint1(f"- Using {nslots_per_subfilter} slots per subfilter; split into {nwindows_per_subfilter} windows.")

    bits_per_slot = uint64(fingerprint_size + window_bits + 1)  # +1 to store at which choice we are and window bits bits for window offset
    bits_per_window = uint64(bits_per_slot * windowsize)
    bits_per_subfilter = nslots_per_subfilter * bits_per_slot
    bits_per_subfilter += 512 - (bits_per_subfilter % 512)
    bits_per_subfilter = uint64(bits_per_subfilter)
    assert bits_per_subfilter % 512 == 0
    debugprint1(f"- Using {bits_per_subfilter} bits per subfilter.")
    filterbits = uint64(nsubfilters * bits_per_subfilter)
    debugprint1(f"- Using {filterbits} bits for the filter.")

    # allocate the underlying array
    if init is True:
        flt = bitarray(filterbits + 128, alignment=64)
        debugprint2(f"- allocated {flt.array.dtype} filter of shape {flt.array.shape}.")
    elif init is False:
        flt = bitarray(0)
        debugprint2("- allocated NOTHING, because init=False")
    elif isinstance(init, np.ndarray):
        flt = bitarray(init)
        debugprint2("- used existing numpy array")
    else:
        raise ValueError(f"{init=} is not a supported option.")

    # get all hash functions for the filters
    # Get the hash function which determines the subfilter
    subfilter_hashfunc_str = 'random' if subfilter_hashfunc_str is None else subfilter_hashfunc_str
    if subfilter_hashfunc_str == 'random':
        subfilter_hashfunc_str = populate_hashfunc_tuple((subfilter_hashfunc_str,), mod_value=nsubfilters)[0]
    debugprint2(f"- using {subfilter_hashfunc_str=}")
    get_subfilter = compile_get_bucket(subfilter_hashfunc_str, universe, nsubfilters)

    # Get fingerprint hash function
    fingerprint_hashfunc_str = 'random' if fingerprint_hashfunc_str is None else fingerprint_hashfunc_str
    if fingerprint_hashfunc_str == 'random':
        fingerprint_hashfunc_str = populate_hashfunc_tuple((fingerprint_hashfunc_str,), mod_value=nfingerprints)[0]
    debugprint2(f"- using {fingerprint_hashfunc_str=}")

    # Use fingerprint size - 1 so 0 is an empty slot
    fingerprint_hash_off = compile_get_bucket(fingerprint_hashfunc_str, universe, nfingerprints)
    compute_fingerprint = njit('uint64(uint64)', nogil=True)(lambda x: fingerprint_hash_off(x) + 1)

    # Get the hash function "hash"
    window_hashfunc_str = 'random' if window_hashfunc_str is None else window_hashfunc_str
    if window_hashfunc_str == 'random':
        window_hashfunc_str = populate_hashfunc_tuple((window_hashfunc_str, ), mod_value=nwindows_per_subfilter)[0]
    debugprint2(f"- using {window_hashfunc_str=}")
    get_window = compile_get_bucket(window_hashfunc_str, universe, nwindows_per_subfilter)

    offset_hashfunc_str = 'random' if offset_hashfunc_str is None else offset_hashfunc_str
    if offset_hashfunc_str == 'random':
        offset_hashfunc_str = populate_hashfunc_tuple((offset_hashfunc_str, ), mod_value=nwindows_per_subfilter - windowsize + 1, min_value=nwindows_per_subfilter)[0]
    debugprint2(f"- using {offset_hashfunc_str=}")
    get_offset = compile_get_bucket(offset_hashfunc_str, universe, nwindows_per_subfilter - windowsize + 1)

    get_window_bits = compile_load_value(bits_per_window)
    get_slot_bits = compile_load_value(bits_per_slot)
    store_fingerprint = compile_store_value(bits_per_slot)

    @njit(nogil=True, locals=dict(subfilter_offset=uint64,
        window_start=uint64, pos=uint64))
    def set_offset_choice_fingerprint_at(fltr, sf, window, slot, choice_offset_fingerprint):
        subfilter_offset = sf * bits_per_subfilter
        pos = subfilter_offset + (window + slot) * bits_per_slot
        store_fingerprint(fltr, pos, choice_offset_fingerprint)

    @njit(nogil=True, locals=dict(subfilter_offset=uint64,
        window_start=uint64, pos=uint64))
    def get_offset_choice_fingerprint_at(fltr, sf, window, slot):
        subfilter_offset = sf * bits_per_subfilter
        pos = subfilter_offset + (window + slot) * bits_per_slot
        return get_slot_bits(fltr, pos)

    @njit(nogil=True, locals=dict(subfilter_offset=uint64,
        window_start=uint64, pos=uint64))
    def is_slot_empty_at(fltr, sf, window, slot):
        subfilter_offset = sf * bits_per_subfilter
        pos = subfilter_offset + (window + slot) * bits_per_slot
        if get_slot_bits(fltr, pos) == 0:
            return True
        return False

    @njit(nogil=True, locals=dict(slot=int64))
    def get_empty_slot_slow(fltr, sf, window, start_slot=0):
        for slot in range(start_slot, windowsize):
            if is_slot_empty_at(fltr, sf, window, slot):
                return slot
        return windowsize

    @njit(nogil=True, locals=dict(subfilter_offset=uint64,
        pos=uint64, windowbits=uint64))
    def get_empty_slot_fast(fltr, sf, window, start_slot=0):
        subfilter_offset = sf * bits_per_subfilter
        pos = subfilter_offset + window * bits_per_slot
        windowbits = get_window_bits(fltr, pos)
        return find_empty_slot(windowbits)

    @njit(nogil=True, locals=dict(slot=int64, offset_choice_fingerprint=uint64))
    def insert_in_window(fltr, sf, window, choice_fingerprint, start_slot=0):
        slot = get_empty_slot(fltr, sf, window, start_slot=start_slot)
        if slot < windowsize:
            offset_choice_fingerprint = choice_fingerprint | (slot << fingerprint_size)
            set_offset_choice_fingerprint_at(fltr, sf, window, slot, offset_choice_fingerprint)
            return True
        return False

    @njit(nogil=True, locals=dict(window1=int64,
        next_window_offset=uint64, window2=int64))
    def compute_windows_for_key(key, fingerprint):
        window1 = get_window(key)
        next_window_offset = get_offset(fingerprint)
        window2 = (window1 + next_window_offset) % nwindows_per_subfilter
        return window1, window2

    @njit(nogil=True, locals=dict(next_window_offset=uint64, window2=int64))
    def compute_windows_for_fingerprint(fingerprint, choice, fingerprint_slot, current_slot, window1):
        if fingerprint_slot != current_slot:
            window1 += (current_slot - fingerprint_slot)
        next_window_offset = (1 - 2 * choice) * get_offset(fingerprint)
        window2 = (window1 + next_window_offset) % nwindows_per_subfilter
        return window1, window2

    @njit(nogil=True, locals=dict(fingerprint=uint64, choice_fingerprint=uint64, offset_choice_fingerprint=uint64,
        removed_offset_choice_fingerprint=uint64, window1=int64, window2=int64, next_window_offset=uint64,
        slot=int64, empty_slot=int64, step=uint64, offset=int64, maxsteps=uint64, choice=uint64))
    def insert_in_subfilter(fltr, sf, key):
        fingerprint = compute_fingerprint(key)
        window, window2 = compute_windows_for_key(key, fingerprint)
        fingerprint2 = fingerprint ^ choice_mask

        # try to insert fingerprint in both windows
        if insert_in_window(fltr, sf, window, fingerprint):
            return True, uint64(0)
        if insert_in_window(fltr, sf, window2, fingerprint2):
            return True, uint64(0)

        # get a random slot
        slot = randint(windowsize)
        offset_choice_fingerprint = fingerprint | (slot << fingerprint_size)
        step = 0
        while step <= maxsteps:
            # get the fingerprint that is stored in the slot and insert the current fingerprint
            removed_offset_choice_fingerprint = get_offset_choice_fingerprint_at(fltr, sf, window, slot)
            set_offset_choice_fingerprint_at(fltr, sf, window, slot, offset_choice_fingerprint)

            fingerprint = removed_offset_choice_fingerprint & fingerprint_mask
            choice = removed_offset_choice_fingerprint & choice_mask
            fingerprint_slot = (removed_offset_choice_fingerprint & slot_mask) >> fingerprint_size
            window1, window2 = compute_windows_for_fingerprint(fingerprint, choice >> (fingerprint_size + window_bits), fingerprint_slot, slot, window)
            # check if the 1st or 2nd window has an empty slot, if yes the fingerprint is inserted
            if insert_in_window(fltr, sf, window1, fingerprint | choice, start_slot=fingerprint_slot):
                return True, step
            fingerprint2 = fingerprint | (choice_mask ^ choice)
            if insert_in_window(fltr, sf, window2, fingerprint2):
                return True, step

            # pick a new random slot
            slot = randint(windowsize)
            window = window2
            offset_choice_fingerprint = fingerprint2 | (slot << fingerprint_size)

            step += 1
        return False, step

    @njit(nogil=True)
    def insert(fltr, key):
        subfilter = get_subfilter(key)
        return insert_in_subfilter(fltr, subfilter, key)[0]

    @njit(nogil=True, locals=dict(fingerprint=uint64,
        subfilter_offset=uint64, pos=uint64,
        window_bits1=uint64, window_bits2=uint64,
        window1=int64, window2=int64,))
    def lookup_in_subfilter_fast(fltr, sf, key):
        fingerprint = compute_fingerprint(key)
        window1, window2 = compute_windows_for_key(key, fingerprint)
        subfilter_offset = sf * bits_per_subfilter

        pos = subfilter_offset + window1 * bits_per_slot
        window_bits1 = get_window_bits(fltr, pos)
        if lookup_fp_in_window(window_bits1, fingerprint):
            return True

        pos = subfilter_offset + window2 * bits_per_slot
        window_bits2 = get_window_bits(fltr, pos)
        fingerprint ^= choice_mask
        if lookup_fp_in_window(window_bits2, fingerprint):
            return True
        return False

    @njit(nogil=True, locals=dict(fingerprint=uint64,
        subfilter_offset=uint64, pos=uint64,
        window_bits1=uint64, window_bits2=uint64,
        window1=int64, window2=int64,))
    def lookup_in_subfilter_fast_combined(fltr, sf, key):
        fingerprint = compute_fingerprint(key)
        window1, window2 = compute_windows_for_key(key, fingerprint)
        subfilter_offset = sf * bits_per_subfilter

        pos = subfilter_offset + window1 * bits_per_slot
        pos2 = subfilter_offset + window2 * bits_per_slot
        window_bits = get_window_bits(fltr, pos)
        window_bits = (window_bits << bits_per_window) | get_window_bits(fltr, pos2)
        return lookup_fp_in_window(window_bits, fingerprint)

    @njit(nogil=True, locals=dict(fingerprint=uint64, choice_fingerprint=uint64, offset_choice_fingerprint=uint64,
        stored_choice_fingerprint=uint64,
        window1=int64, window2=int64, window=int64,))
    def lookup_in_subfilter_slow(fltr, sf, key):
        fingerprint = compute_fingerprint(key)
        window1, window2 = compute_windows_for_key(key, fingerprint)
        fingerprint2 = fingerprint ^ choice_mask

        for slot in range(windowsize):
            stored_choice_fingerprint = get_offset_choice_fingerprint_at(fltr, sf, window1, slot)
            offset_choice_fingerprint = fingerprint | (slot << fingerprint_size)
            if stored_choice_fingerprint == offset_choice_fingerprint:
                return True
        for slot in range(windowsize):
            stored_choice_fingerprint = get_offset_choice_fingerprint_at(fltr, sf, window2, slot)
            offset_choice_fingerprint = fingerprint2 | (slot << fingerprint_size)
            if stored_choice_fingerprint == offset_choice_fingerprint:
                return True
        return False

    @njit(nogil=True)
    def lookup_and_insert_in_subfilter(fltr, subfilter, key):
        if not lookup_in_subfilter(fltr, subfilter, key):
            return insert_in_subfilter(fltr, subfilter, key)[0]
        return True

    @njit(nogil=True)
    def lookup(fltr, key):
        subfilter = get_subfilter(key)
        return lookup_in_subfilter(fltr, subfilter, key)

    @njit(nogil=True)
    def update_ssk(fltr, sf, key, value=1):
        if not lookup_in_subfilter(fltr, sf, key):
            return insert_in_subfilter(fltr, sf, key)
        return True, uint64(0)

    @njit(nogil=True)
    def get_fill(fltr):
        count = 0
        for sf in range(nsubfilters):
            for window in range(nwindows_per_subfilter + windowsize - 1):
                if not is_slot_empty_at(fltr, sf, window, 0):
                    count += 1
        return count / nslots

    @njit(nogil=True)
    def get_fpr(fltr):
        return 1 / (2**fingerprint_size)

    @njit(nogil=True, locals=dict(empty=uint64, filled=uint64, slots=uint64))
    def print_statistics(fltr, level=0):
        empty, filled = 0, 0
        for sf in range(nsubfilters):
            for window in range(nwindows_per_subfilter + windowsize - 1):
                if is_slot_empty_at(fltr, sf, window, 0):
                    empty += 1
                else:
                    filled += 1
        slots = empty + filled

        print("# Statistics")
        print(f"# Total filterbits: {filterbits}")
        print(f"# Slots per window: {windowsize}")
        print(f"# Bits per slot: {bits_per_slot}")
        print(f"# Target FPR: {target_fpr}")
        print(f"# Total slots: {slots}")
        print(f"# Filled slots: {filled}")
        print(f"# Empty slots: {empty}")


    if bits_per_slot * windowsize * 2 <= 64:
        lookup_fp_in_window = compile_lookup(bits_per_slot, windowsize, windowed=True, choice=True)
        lookup_in_subfilter = lookup_in_subfilter_fast_combined
        find_empty_slot = compile_get_empty_slot(bits_per_slot, windowsize)
        get_empty_slot = get_empty_slot_fast
    elif bits_per_slot * windowsize <= 64:
        lookup_fp_in_window = compile_lookup(bits_per_slot, windowsize, windowed=True, choice=False)
        lookup_in_subfilter = lookup_in_subfilter_fast
        find_empty_slot = compile_get_empty_slot(bits_per_slot, windowsize)
        get_empty_slot = get_empty_slot_fast
    else:
        lookup_in_subfilter = lookup_in_subfilter_slow
        get_empty_slot = get_empty_slot_slow

    array = flt.array
    update = insert
    get_value = lookup
    return create_WindowedCuckooFilter(locals())
