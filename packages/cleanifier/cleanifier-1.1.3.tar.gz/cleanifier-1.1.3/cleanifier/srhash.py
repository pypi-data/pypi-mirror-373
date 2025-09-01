"""
Module fastcash.srhash

This module provides
*  SRHash, a namedtuple to store hash information

It provides factory functions to build an SRHash
that are jit-compiled.

"""

from math import ceil
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from numba import njit, uint64, int64, boolean

from .mathutils import nextodd, print_histogram
from .lowlevel import debug


# An SRHash namedtuble is created at the end of build_hash()
# in each concrete hash implementation. e.g. hash_3c_fbcbvb, etc.
# The definition here specifies the attributes and public methods of SRHash
# that must be implemented by any hash type implementation.
SRHash = namedtuple("SRHash", [
    # attributes
    "hashtype",
    "choices",
    "aligned",
    "universe",
    "n",
    "subtables",
    "nbuckets",
    "bucketsize",
    "nfingerprints",
    "nvalues",
    "mem_bytes",
    "shortcutbits",
    "hashfuncs",
    "maxwalk",
    "hashtable",

    # public API methods
    "update",  # (table, key: uint64, value: uint64) -> (int32, uint64)
    "update_existing",  # (table, key: uint64, value: uint64) -> (int32, uint64)
    "store_new",  # (table, key: uint64, value: uint64) -> (int32, uint64)
    "overwrite",  # (table, key: uint64, value: uint64) -> (int32, uint64)
    "overwrite_existing",  # (table, key: uint64, value: uint64) -> (int32, uint64)

    "get_value",  # (table, key: uint64) -> uint64
    "get_value_and_choice",  # (table, key: uint64) -> (uint64, int32)
    "find_index",  # (table, key: uint64) -> uint64; index where key is present or U64_MINUSONE

    "slots_nonempty",
    "slots_with_value",
    # "get_statistics",  # (table) -> tuple of histograms (arrays)
    "is_tight",  # (table) -> boolean
    "compute_shortcut_bits",  # (table) -> None
    "count_items",
    "get_items",
    # private API methods (see below)
    "private",   # hides private API methods (e.g., h.private.get_signature_at())
    ])


SRHash_private = namedtuple("SRHash_private", [
    # private API methods, may change !
    "base",    # 0:
    "get_bf",  # method tuple (get_bf1, get_bf2, ...)
    "get_bs",  # method tuple (get_bs1, get_bs2, ...)
    "is_slot_empty_at",  # returns True iff the given (bucket, slot) is empty
    "get_signature_at",  # returns a single int, unpack with signature_to_choice_fingerprint
    "set_signature_at",
    "get_value_at",
    "set_value_at",
    "get_choicebits_at",    # get raw choice bits as stored
    "get_item_at",
    "set_item_at",
    "get_shortcutbits_at",  # get ALL shortcut bits
    "set_shortcutbit_at",   # set ONE of the shortcut bits

    "get_subtable_subkey_from_key",  # (key: uint64) -> (uint64, uint64)
    "get_key_from_subtable_subkey",  # (uint64, uint64) -> uint64

    "get_value_from_st_sk",
    "get_value_and_choice_from_st_sk",

    "signature_to_choice_fingerprint",  # signature -> (choice, fingerprint)
    "signature_from_choice_fingerprint",   # (choice, fingerprint) -> signature
    "get_subkey_from_bucket_signature",
    "get_subkey_choice_from_bucket_signature",
    "prefetch_bucket",

    # Copies of the public functions but with subtable/subkey interface
    # (only defined for hashes with subtables; otherwise None)
    "update_ssk",  # (table, subtable:uint64, subkey: uint64, value: uint64) -> (int32, uint64)
    "update_existing_ssk",  # (table, subtable:uint64, subkey: uint64, value: uint64) -> (int32, uint64)
    "store_new_ssk",  # (table, subtable:uint64, subkey: uint64, value: uint64) -> (int32, uint64)
    "overwrite_ssk",  # (table, subtable:uint64, subkey: uint64, value: uint64) -> (int32, uint64)
    "overwrite_existing_ssk",  # (table, subtable:uint64, subkey: uint64, value: uint64) -> (int32, uint64)
    "shm",  # We need to save the shared memory object.
    ])


def create_SRHash(d):
    """Return SRHash initialized from values in dictionary d"""
    # The given d does not need to provide mem_bytes; it is computed here.
    # The given d is copied and reduced to the required fields.
    # The hashfuncs tuple is reduced to a single ASCII bytestring.
    d0 = dict(d)
    d0['mem_bytes'] = d0['hashtable'].nbytes
    d0['slots_nonempty'] = compile_slots_nonempty(d)
    d0['slots_with_value'] = compile_slots_with_value(d)
    private = {name: d0[name] for name in SRHash_private._fields}
    d0['private'] = SRHash_private(**private)
    d1 = {name: d0[name] for name in SRHash._fields}
    d1['hashfuncs'] = (':'.join(d1['hashfuncs']))
    return SRHash(**d1)


# Basic functions #########################################

def get_nbuckets(n, bucketsize, fill=1.0):
    return nextodd(ceil(n / fill / bucketsize))
    # must be an odd number for equidistribution
    # TODO: write a more detailed reason


def get_nfingerprints(nfingerprints, universe, nbuckets):
    if nfingerprints < 0:
        nfingerprints = int(ceil(universe / nbuckets))
    elif nfingerprints == 0:
        nfingerprints = 1
    return nfingerprints


def check_bits(nbits, name, threshold=64):
    if threshold < 0:
        threshold = abs(threshold)
        if nbits < threshold:
            raise RuntimeError(f"cannot deal with {nbits} < {threshold} {name} bits")
    else:
        if nbits > threshold:
            raise RuntimeError(f"cannot deal with {nbits} > {threshold} {name} bits")


# Factories / makers for checking if a slot is empty ###################

# move, remove
def compile_is_slot_empty_at_v(get_value_at, get_choicebits_at):
    """
    Factory for VALUE-controlled hash table layouts.
    Return a compiled function 'is_slot_empty_at(table, bucket, slot)'
    that returns whether a given slot is empty (check by vaue)
    """
    @njit(nogil=True, locals=dict(b=boolean))
    def is_slot_empty_at(table, bucket, slot):
        """Return whether a given slot is empty (check by value)"""
        v = get_value_at(table, bucket, slot)
        b = (v == 0)
        return b
    return is_slot_empty_at

# Makers for get_bucketstatus ####################################


# modify, remove
def compile_get_bucketstatus_v(bucketsize,
            get_value_at, get_signature_at,
            signature_parts, signature_full):
    """
    Factory for VALUE-controlled hash tables ('_v').
    [An empty slot is indicated by value == 0].
    Return a compiled function 'get_bucketstatus(table, bucket, fpr, choice)'.
    """
    @njit(nogil=True, locals=dict(
        bucket=uint64, fpr=uint64, choice=int64,
        query=uint64, slot=int64, v=uint64, s=uint64))
    def get_bucketstatus(table, bucket, fpr, choice):
        """
        Attempt to locate a (fingerprint, choice) pair on a bucket,
        assuming value == 0 indicates an empty space.
        Return (int64, uint64):
        Return (slot, value) if the fingerprint 'fpr' was found,
            where 0 <= slot < bucketsize.
        Return (-1, fill)    if the fingerprint was not found,
            where fill >= 0 is the number of slots already filled.
        Note: Return type is always (int64, uint64) !
        """
        query = signature_full(choice, fpr)
        for slot in range(bucketsize):
            v = get_value_at(table, bucket, slot)
            if v == 0:
                return (-1, uint64(slot))  # free slot, only valid if tight!
            s = get_signature_at(table, bucket, slot)
            if s == query:
                return (slot, v)
        return (-1, uint64(bucketsize))
    return get_bucketstatus


# Makers for is_tight #########################################

# TODO: move and remove once we have a value-based hash!
# This is just a placeholder for a real implementation; it does not work.
# DOESNTWORK!
def compile_is_tight_v(nbuckets, bucketsize,
        get_value_at, get_signature_at, signature_parts,
        get_key, get_bf, _get_bucketstatus):
    """
    Factory for VALUE-controlled hash tables ('_v').
    [Empty slots are indicated by value == 0.]
    Return compiled 'is_tight(hashtable)' function.
    """
    choices = len(get_bf)
    if choices > 3:
        raise ValueError("compile_is_tight currently supports only up to 3 hash functions")
    if choices <= 1:  # hash is always tight for a single hash func.
        @njit(nogil=True)
        def is_tight(ht):
            """return (0,0) if hash is tight, or problem (key, choice)"""
            return (uint64(0), 0)
        return is_tight

    (get_bf1, get_bf2, get_bf3) = get_bf
    (get_key1, get_key2, get_key3) = get_key

    @njit(nogil=True, locals=dict(
        bucket=uint64, slot=int64, v=uint64, sig=uint64, c=uint64,
        f=uint64, key=uint64, p=uint64, s=int64, fill=uint64))
    def is_tight(ht):
        """return (0,0) if hash is tight, or problem (key, choice)"""
        for subtable in range(subtables):
            for bucket in range(nbuckets):
                for slot in range(bucketsize):
                    v = get_value_at(ht, subtable, bucket, slot)
                    if v == 0:
                        continue
                    sig = get_signature_at(ht, subtable, bucket, slot)
                    (c, f) = signature_parts(sig)
                    if c == 0:
                        continue
                    if c == 1:
                        key = get_key2(bucket, f)
                        (p, f) = get_bf1(key)
                        (s, fill) = _get_bucketstatus(ht, subtable, p, f, 0)
                        if s >= 0 or fill != bucketsize:
                            return (uint64(key), 1)  # empty slot on 1st choice
                        continue  # ok
                    if c == 2:
                        key = get_key3(bucket, f)
                        p, f = get_bf2(key)
                        (s, fill) = _get_bucketstatus(ht, subtable, p, f, 1)
                        if s >= 0 or fill != bucketsize:
                            return (uint64(key), 2)  # empty slot on 2nd choice
                        p, f = get_bf1(key)
                        (s, fill) = _get_bucketstatus(ht, subtable, p, f, 0)
                        if s >= 0 or fill != bucketsize:
                            return (uint64(key), 1)  # empty slot on 1st choice
                        continue  # ok
                    return (uint64(key), 9)  # should never happen, c=0,1,2
        # all done, no problems
        return (uint64(0), 0)
    return is_tight


# Compile functions to compute subkey (and choice) from bucket number and signature

def compile_get_subkey_from_bucket_signature(
        get_subkey, signature_to_choice_fingerprint, *, base=0):
    """
    Factory function for both VALUE- and CHOICE-controlled hashes.
    [For VALUE-controlled hashes, use base=0; for CHOICE-controlled hashes, base=1.]
    Return a compiled function 'get_key_from_signature(bucket, signature)'
    that returns the kmer code (key) given a bucket number and a signature.
    A signature is the pair (choice, fingerprint).
    """
    choices = len(get_subkey)
    if choices < 1 or choices > 4:
        raise ValueError("Only 1 to 4 hash functions are supported.")
    (get_subkey1, get_subkey2, get_subkey3, get_subkey4) = (get_subkey + (njit(nogil=True)(lambda x, y: uint64(0)),)*4)[:4]

    @njit(nogil=True, locals=dict(
        bucket=uint64, sig=uint64, c=int64, fpr=uint64, key=uint64))
    def get_subkey_from_bucket_signature(bucket, sig):
        """
        Return the kmer-code (key) for a given bucket and signature.
        The signature 'sig' encodes both choice and fingerprint.
        """
        (c, fpr) = signature_to_choice_fingerprint(sig)
        c = c + 1 - base
        # assert 1 <= c <= choices
        if c == 1:
            key = get_subkey1(bucket, fpr)
        elif c == 2:
            key = get_subkey2(bucket, fpr)
        elif c == 3:
            key = get_subkey3(bucket, fpr)
        elif c == 4:
            key = get_subkey4(bucket, fpr)
        else:
            key = uint64(0)
        return key
    return get_subkey_from_bucket_signature


def compile_get_subkey_choice_from_bucket_signature(
        get_subkey, signature_to_choice_fingerprint, *, base=0):
    """
    Factory function for both VALUE- and CHOICE-controlled hashes.
    [For VALUE-controlled hashes, use base=0; for CHOICE-controlled hashes, base=1.]
    Return a compiled function 'get_key_choice_from_signature(bucket, signature)'
    that returns the pair (key, choice), given a bucket number and a signature.
    A signature is the pair (choice, fingerprint).
    """    
    choices = len(get_subkey)
    if choices < 1 or choices > 4:
        raise ValueError("Only 1 to 4 hash functions are supported.")
    (get_subkey1, get_subkey2, get_subkey3, get_subkey4) =  (get_subkey + (njit(nogil=True)(lambda x, y: uint64(0)),)*4)[:4]

    @njit(nogil=True, locals=dict(
        bucket=uint64, sig=uint64, c=int64, fpr=uint64, key=uint64))
    def get_subkey_choice_from_bucket_signature(bucket, sig):
        """
        Return pair (key, choice) for the given bucket and signature,
        where choice is in {0,1,2} or -1 when empty.
        """
        (c, fpr) = signature_to_choice_fingerprint(sig)
        c = c + 1 - base
        # assert 1 <= c <= choices
        if c == 1:
            key = get_subkey1(bucket, fpr)
        elif c == 2:
            key = get_subkey2(bucket, fpr)
        elif c == 3:
            key = get_subkey3(bucket, fpr)
        elif c == 4:
            key = get_subkey4(bucket, fpr)
        else:
            key = uint64(0)
        return (key, c)
    return get_subkey_choice_from_bucket_signature


# Define get_statistics ###################################
# This stays here in srhash, because it is generic.
def get_statistics_ptr(h, nvalues):
    """
    Return a tuple of arrays (valuehist, fillhist, choicehist, shortcuthist), where
    valuehist[v] is the number of items with value v,
    fillhist[i] is the number of buckets with i items filled,
    choicehist[i] is the number of slots with choice i,
    shortcuthist[i] is the number of shortcutbits with value i.
    """

    base = h.private.base
    if base not in (0, 1):
        raise ValueError("ERROR: The hash table is neither value-based nor choice-based.")
    ctrl_value = (base == 0)  # base 0 means value-based hash
    ctrl_choice = (base == 1)  # base 1 means choice-based hash

    subtables = h.subtables
    choices = h.choices
    nbuckets = h.nbuckets
    bucketsize = h.bucketsize
    shortcutbits = h.shortcutbits
    get_value_at = h.private.get_value_at
    get_signature_at = h.private.get_signature_at
    signature_parts = h.private.signature_to_choice_fingerprint
    get_shortcutbits_at = h.private.get_shortcutbits_at

    valuehist = np.zeros((subtables, nvalues + 1), dtype=np.int64)
    fillhist = np.zeros((subtables, bucketsize + 1), dtype=np.int64)
    choicehist = np.zeros((subtables, choices + 1), dtype=np.int64)
    shortcuthist = np.zeros((subtables, 2**shortcutbits), dtype=np.int64)
    MAXVALUE = nvalues - 1 if nvalues > 0 else 0

    @njit(nogil=True, locals=dict(
          bucket=uint64, last=int64, slot=int64, x=uint64, c=uint64, v=uint64, vv=uint64))
    def _get_statistics_for_subtable(table, subtable, valuehist, fillhist, choicehist, shortcuthist):
        """
        For each element or page in the specific subtable fill the corresponding table with the provided information.
        """
        for bucket in range(nbuckets):
            last = -1
            if shortcutbits != 0:
                shortcuthist[get_shortcutbits_at(subtable, bucket)] += 1
            for slot in range(bucketsize):
                if ctrl_choice:
                    sig = get_signature_at(subtable, bucket, slot)
                    c = signature_parts(sig)[0]  # no +1 !
                    choicehist[c] += 1
                    if c != 0:
                        last = slot
                        v = min(get_value_at(subtable, bucket, slot), MAXVALUE)
                        valuehist[v] += 1
                elif ctrl_value:
                    v = get_value_at(subtable, bucket, slot)

                    vv = min(v, MAXVALUE)
                    valuehist[vv] += 1
                    if v == 0:
                        c = 0
                    else:
                        last = slot
                        sig = get_signature_at(subtable, bucket, slot)
                        c = 1 + signature_parts(sig)[0]  # 1+ is correct!
                    choicehist[c] += 1
                else:
                    pass  # other controls than choice/value not implemented
            fillhist[last + 1] += 1
        return subtable

    with ThreadPoolExecutor(max_workers=subtables) as executor:
        futures = [executor.submit(
            _get_statistics_for_subtable,
            h.hashtable, st,
            valuehist[st], fillhist[st], choicehist[st], shortcuthist[st]
            ) for st in range(subtables)]
        for fut in as_completed(futures):
            ex = fut.exception()
            if ex is not None:
                raise Exception(f"ERROR: Exception in {fut}: {ex}")

    return (valuehist, fillhist, choicehist, shortcuthist)

def get_statistics(h, nvalues):
    """
    Return a tuple of arrays (valuehist, fillhist, choicehist, shortcuthist), where
    valuehist[v] is the number of items with value v,
    fillhist[i] is the number of buckets with i items filled,
    choicehist[i] is the number of slots with choice i,
    shortcuthist[i] is the number of shortcutbits with value i.
    """

    base = h.private.base
    if base not in (0, 1):
        raise ValueError("ERROR: The hash table is neither value-based nor choice-based.")
    ctrl_value = (base == 0)  # base 0 means value-based hash
    ctrl_choice = (base == 1)  # base 1 means choice-based hash

    subtables = h.subtables
    choices = h.choices
    nbuckets = h.nbuckets
    bucketsize = h.bucketsize
    shortcutbits = h.shortcutbits
    get_value_at = h.private.get_value_at
    get_signature_at = h.private.get_signature_at
    signature_parts = h.private.signature_to_choice_fingerprint
    get_shortcutbits_at = h.private.get_shortcutbits_at

    valuehist = np.zeros((subtables, nvalues + 1), dtype=np.int64)
    fillhist = np.zeros((subtables, bucketsize + 1), dtype=np.int64)
    choicehist = np.zeros((subtables, choices + 1), dtype=np.int64)
    shortcuthist = np.zeros((subtables, 2**shortcutbits), dtype=np.int64)
    MAXVALUE = nvalues - 1 if nvalues > 0 else 0

    @njit(nogil=True, locals=dict(
          bucket=uint64, last=int64, slot=int64, x=uint64, c=uint64, v=uint64))
    def _get_statistics_for_subtable(table, subtable, valuehist, fillhist, choicehist, shortcuthist):
        """
        For each element or page in the specific subtable fill the corresponding table with the provided information.
        """
        for bucket in range(nbuckets):
            last = -1
            if shortcutbits != 0:
                shortcuthist[get_shortcutbits_at(table, subtable, bucket)] += 1
            for slot in range(bucketsize):
                if ctrl_choice:
                    sig = get_signature_at(table, subtable, bucket, slot)
                    c = signature_parts(sig)[0]  # no +1 !
                    choicehist[c] += 1
                    if c != 0:
                        last = slot
                        v = min(get_value_at(table, subtable, bucket, slot), MAXVALUE)
                        valuehist[v] += 1
                elif ctrl_value:
                    v = min(get_value_at(table, subtable, bucket, slot), MAXVALUE)
                    valuehist[v] += 1
                    if v == 0:
                        c = 0
                    else:
                        last = slot
                        sig = get_signature_at(table, subtable, bucket, slot)
                        c = 1 + signature_parts(sig)[0]  # 1+ is correct!
                    choicehist[c] += 1
                else:
                    pass  # other controls than choice/value not implemented
            fillhist[last + 1] += 1
        return subtable

    with ThreadPoolExecutor(max_workers=subtables) as executor:
        futures = [executor.submit(
            _get_statistics_for_subtable,
            h.hashtable, st,
            valuehist[st], fillhist[st], choicehist[st], shortcuthist[st]
            ) for st in range(subtables)]
        for fut in as_completed(futures):
            ex = fut.exception()
            if ex is not None:
                raise Exception(f"ERROR: Exception in {fut}: {ex}")

    return (valuehist, fillhist, choicehist, shortcuthist)


def print_statistics(h, level, *, show_values=True, show_fill=True, show_choices=True, ptr=False):
    # TODO: shortcut bits? walkstats?
    show_statistics = (level != 'none') and (show_values or show_fill or show_choices)
    if not show_statistics:
        return
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    nsubtables = h.subtables

    timestamp0(msg="\n## Statistics")
    # TODO: walkstats
    # print_histogram_tail(walkstats, [1, 2, 10], title="### Extreme walk lengths:", shorttitle="walk", average=True)
    if show_values is True:
        show_values = h.nvalues
    elif show_values is False:
        show_values = 0
    assert isinstance(show_values, int)
    show_values = max(0, min(show_values, h.nvalues))
    if ptr:
        valuehist, fillhist, choicehist, shortcuthist = get_statistics_ptr(h, show_values)
    else:
        valuehist, fillhist, choicehist, shortcuthist = get_statistics(h, show_values)
    if level == "full":
        for st in range(nsubtables):
            debugprint0(f"\n## Statistics for subtable {st}")
            if show_values:
                print_histogram(valuehist[st], title=f"### Value statistics {st}", shorttitle="values", fractions="%")
            if show_fill:
                print_histogram(fillhist[st], title=f"### Page fill statistics {st}", shorttitle="fill", fractions="%", average=True, nonzerofrac=True)
            if show_choices:
                print_histogram(choicehist[st], title=f"### Choice statistics {st}", shorttitle="choice", fractions="%+", average="+")
            # if scb > 0:
            #     print_histogram(shortcuthist[i], title="### Shortcut bit statistics", shorttitle="shortcutbits", fractions="%")
    debugprint0("\n## Combined statsitcs for all subtables")
    if show_values:
        print_histogram(np.sum(valuehist, axis=0), title="### Value statistics", shorttitle="values", fractions="%")
    if show_fill:
        print_histogram(np.sum(fillhist, axis=0), title="### Page fill statistics", shorttitle="fill", fractions="%", average=True, nonzerofrac=True)
    if show_choices:
        print_histogram(np.sum(choicehist, axis=0), title="### Choice statistics", shorttitle="choice", fractions="%+", average="+")
    debugprint1("- Done with statistics.")


def compile_slots_nonempty(kwargs):
    """compile the slots_nonempty function"""
    subtables = kwargs['subtables']
    nbuckets = kwargs['nbuckets']
    bucketsize = kwargs['bucketsize']
    is_slot_empty_at = kwargs['is_slot_empty_at']

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=int64, empty=int64))
    def slots_nonempty(ht):
        """Return number of nonempty slots"""
        empty = 0
        for subtable in range(subtables):
            for bucket in range(nbuckets):
                for slot in range(bucketsize):
                    empty += is_slot_empty_at(ht, subtable, bucket, slot)
        return int64(int64(subtables * nbuckets * bucketsize) - empty)

    return slots_nonempty


def compile_slots_with_value(kwargs):
    """compile the slots_with_value function"""
    subtables = kwargs['subtables']
    nbuckets = kwargs['nbuckets']
    bucketsize = kwargs['bucketsize']
    is_slot_empty_at = kwargs['is_slot_empty_at']
    get_value_at = kwargs['get_value_at']

    @njit(nogil=True,
        locals=dict(bucket=int64, slot=int64, n=int64))
    def slots_with_value(ht, myvalue):
        """Return number of slots with a specific value"""
        n = 0
        for subtable in range(subtables):
            for bucket in range(nbuckets):
                for slot in range(bucketsize):
                    if is_slot_empty_at(ht, subtable, bucket, slot):
                        continue
                    if get_value_at(ht, subtable, bucket, slot) == myvalue:
                        n += 1
        return n

    return slots_with_value
