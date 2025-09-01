"""
hash_s3c_fbcbvb:
a hash table with subtables and three choices,
bucket layout is (low) ... [slot]+ ... (high),
where slot is  (low) ... [signature value] ...     (high),
where signature is (low) [fingerprint choice] .....(high).
signature as bitmask: ccffffffffffffff (choice is at HIGH bits!)

This layout allows fast access because bits are separated.
It is memory-efficient if the number of values is a power of 2,
or just a little less.
"""

import numpy as np
from numpy.random import randint
from numba import njit, uint64, int64, uint32, int32, boolean
from math import log, ceil

from .mathutils import bitsfor, xbitsfor, nextpower
from .lowlevel.bitarray import bitarray
from .lowlevel.intbitarray import intbitarray
from .subtable_hashfunctions import (
    get_hashfunctions,
    hashfunc_tuple_from_str,
    compile_get_subtable_subkey_from_key,
    )
from .srhash import (
    create_SRHash,
    check_bits,
    get_nbuckets,
    get_nfingerprints,
    compile_get_subkey_from_bucket_signature,
    compile_get_subkey_choice_from_bucket_signature,
    )
from .lowlevel import debug  # the global debugging functions
from .lowlevel.llvm import compile_load_value, compile_store_value, compile_prefetch_array_element


def generate_function(function_name, h_name, function_tuple):
    """Generates compiled hash functions"""
    k = len(function_tuple)
    strings = []
    gstring = "global {h_name}_{s}"
    hfstring = "{h_name}_{s} = function_tuple[{s}]"
    for i in range(k):
        strings.append(gstring.format(h_name=h_name, s=i))
        strings.append(hfstring.format(h_name=h_name, s=i))
    strings.append("")
    strings.append("@njit(nogil=True)")
    strings.append(f"def {function_name}(level, key):")
    strings.append("    if level == 0:")
    strings.append(f"        return {h_name}_0(key)")
    s1 = "    elif level == {s}:"
    s2 = "        return {h_name}_{s}(key)"
    for i in range(1, len(function_tuple)):
        strings.append(s1.format(s=i))
        strings.append(s2.format(h_name=h_name, s=i))
    strings.append("    else:")
    strings.append("        raise RuntimeError('Wrong level')")
    f_string = "\n".join(strings)
    my_local_namespace = locals()
    my_global_namespace = globals()
    exec(f_string, my_global_namespace, my_local_namespace)
    return my_local_namespace[function_name]


def build_hash(universe, n, subtables, choices, bucketsize,
        hashfunc_str, nvalues, update_value, *,
        aligned=False, nfingerprints=-1, init=True,
        maxwalk=-1, prefetch=False, force_h0=None, shm=None):
    """
    Allocate an array and compile access methods for a hash table.
    Return an SRHash object with the hash information.
    """

    assert choices in [2, 3]
    # Get debug printing functions
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    # timestamp0, timestamp1, timestamp2 = debug.timestamp
    U64_MINUSONE = uint64(np.iinfo(np.uint64).max)

    # Basic properties
    hashtype = "new"
    base = 0 # choice-based hash type (choice==0 means empty slot)
    if maxwalk <= 0:
        maxwalk = 500  # reasonable default
    nbuckets = get_nbuckets(ceil(n / subtables), bucketsize)
    sub_universe = universe // (4**(int(log(subtables, 4))))
    nfingerprints = get_nfingerprints(nfingerprints, sub_universe, nbuckets)
    fprbits, ffprbits = xbitsfor(nfingerprints)
    choicebits = bitsfor(choices)
    sigbits = fprbits + choicebits
    valuebits = bitsfor(nvalues)
    check_bits(sigbits, "signature")
    check_bits(valuebits, "value")

    fprmask = uint64(2**fprbits - 1)
    choicemask = uint64(2**choicebits - 1)
    sigmask = uint64(2**sigbits - 1)  # fpr + choice, no values
    slotbits = sigbits + valuebits  # sigbits: bitsfor(fpr x choice)
    neededbits = slotbits * bucketsize  # specific
    bucketsizebits = nextpower(neededbits) if aligned else neededbits
    subtablebits = int(nbuckets * bucketsizebits)
    subtablebits = (subtablebits // 512 + 1) * 512
    tablebits = subtablebits * subtables

    fprloss = bucketsize * nbuckets * (fprbits - ffprbits) / 2**23  # in MB

    # allocate the underlying array
    if init is True:
        hasharray = bitarray(tablebits, alignment=64)  # (#bits, #bytes)
        debugprint2(f"- allocated {hasharray.array.dtype} hash table of shape {hasharray.array.shape}.")
    elif init is False:
        hasharray = bitarray(0)
        debugprint2("- allocated NOTHING, because init=False")
    elif isinstance(init, np.ndarray):
        hasharray = bitarray(init)
        debugprint2("- used existing numpy array")
    else:
        raise ValueError(f"{init=} is not a supported option.")

    hashtable = hasharray.array  # the raw bit array
    hashtable_ptr = hashtable.ctypes.data
    prefetch = compile_prefetch_array_element(bucketsizebits)

    if hashfunc_str == "random" or hashfunc_str == "default":
        if force_h0 is not None:
            firsthashfunc = force_h0
        else:
            # Use the last default hash function
            firsthashfunc = hashfunc_tuple_from_str(
                hashfunc_str, mod_value=subtables, number=4)[-1]

    else:
        firsthashfunc, hashfunc_str = hashfunc_str.split(":", 1)
    get_subtable_subkey_from_key, get_key_from_subtable_subkey \
        = compile_get_subtable_subkey_from_key(firsthashfunc, universe, subtables)

    hashfuncs, get_bf, get_subkey, get_subtable_bucket_fpr, get_key_from_subtale_bucket_fpr \
        = get_hashfunctions(firsthashfunc, hashfunc_str, choices, universe, nbuckets, subtables)

    debugprint1(
        f"- fingerprintbits: {ffprbits} -> {fprbits}; loss={fprloss:.1f} MB\n"
        f"- nbuckets={nbuckets}, slots={bucketsize*nbuckets}, n={n} per subtable\n"
        f"- bits per slot: {slotbits}; per bucket: {neededbits} -> {bucketsizebits}\n"
        f"- subtable bits: {subtablebits};  ({subtablebits/2**23:.1f} MiB, {subtablebits/2**33:.3f} GiB) x {subtables} subtables\n"
        f"- table bits: {tablebits};  MB: {tablebits/2**23:.1f};  GB: {tablebits/2**33:.3f}\n"
        f"- final hash functions: {hashfuncs}",
    )

    get_bs = tuple([compile_getps_from_getpf(get_bf[c], c, fprbits)
            for c in range(choices)])

    get_bucket_fingerprint = generate_function("get_bucket_fingerprint", "get_bf", get_bf)
    get_bucket_signature = generate_function("get_bucket_singature", "get_bs", get_bs)
    compute_key = generate_function("compute_key", "get_subkey", get_subkey)

    get_value_bits = compile_load_value(valuebits)
    get_choice_bits = compile_load_value(choicebits)
    get_sig_bits = compile_load_value(sigbits)

    set_value_bits = compile_store_value(valuebits)
    set_sig_bits = compile_store_value(sigbits)


    # TODO Dummy functions
    get_shortcutbits_at = None
    set_shortcutbit_at = None
    shortcutbits = 0
    compute_shortcut_bits = 0

    @njit(nogil=True, locals=dict(
        bucket=int64, startbit=uint64))
    def prefetch_bucket(subtable, bucket):
        startbit = subtable * subtablebits + bucket * bucketsizebits
        prefetch(hashtable_ptr, startbit)

    # Define private low-level hash table accessor methods
    @njit(nogil=True, locals=dict(
        bucket=int64, slot=uint64, startbit=int64, v=uint64))
    def get_value_at(subtable, bucket, slot):
        """Return the value at the given bucket and slot."""
        if valuebits == 0:
            return 0
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits + sigbits
        v = get_value_bits(hashtable_ptr, startbit)
        return v

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=uint64, startbit=int64, c=uint64))
    def get_choicebits_at(subtable, bucket, slot):
        """Return the choice at the given bucket and slot; choices start with 1."""
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits + fprbits
        c = get_choice_bits(hashtable_ptr, startbit)
        return c

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=uint64, startbit=int64, sig=uint64))
    def get_signature_at(subtable, bucket, slot):
        """Return the signature (choice, fingerprint) at the given bucket and slot."""
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits
        sig = get_sig_bits(hashtable_ptr, startbit)
        return sig

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=uint64, startbit=int64, sig=uint64, v=uint64))
    def get_item_at(subtable, bucket, slot):
        """Return the signature (choice, fingerprint) and value at the given bucket and slot."""
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits
        sig = get_sig_bits(hashtable_ptr, startbit)
        if valuebits > 0:
            v = get_value_bits(hashtable_ptr, startbit + sigbits)
            return (sig, v)
        return (sig, uint64(0))

    @njit(nogil=True, locals=dict(
        sig=uint64, c=uint64, fpr=uint64))
    def signature_to_choice_fingerprint(sig):
        """Return (choice, fingerprint) from signature"""
        fpr = sig & fprmask
        c = (sig >> uint64(fprbits)) & choicemask
        return (c, fpr)

    @njit(nogil=True, locals=dict(
        sig=uint64, choice=uint64, fpr=uint64))
    def signature_from_choice_fingerprint(choice, fpr):
        """Return signature from (choice, fingerprints)"""
        sig = (choice << uint64(fprbits)) | fpr
        return sig

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=int64, sig=uint64))
    def set_signature_at(subtable, bucket, slot, sig):
        """Set the signature at the given bucket and slot."""
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits
        set_sig_bits(hashtable_ptr, startbit, sig)
    
    @njit(nogil=True, locals=dict(
        bucket=int64, slot=int64, value=int64))
    def set_value_at(subtable, bucket, slot, value):

        if valuebits == 0:
            return
        """Set the value at the given bucket and slot."""
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits + sigbits
        set_value_bits(hashtable_ptr, startbit, value)

    @njit(nogil=True, locals=dict(
        bucket=int64, slot=int64, sig=uint64, value=uint64))
    def set_item_at(subtable, bucket, slot, sig, value):
        startbit = subtable * subtablebits + bucket * bucketsizebits + slot * slotbits
        set_sig_bits(hashtable_ptr, startbit, sig)
        if valuebits == 0:
            return
        set_value_bits(hashtable_ptr, startbit + sigbits, value)

    # define the is_slot_empty_at function
    @njit(nogil=True, locals=dict(b=boolean))
    def is_slot_empty_at(subtable, bucket, slot):
        """Return whether a given slot is empty (check by value)"""
        v = get_value_at(subtable, bucket, slot)
        b = (v == 0)
        return b

    # define the get_subkey_from_bucket_signature function
    get_subkey_from_bucket_signature = compile_get_subkey_from_bucket_signature(
        get_subkey, signature_to_choice_fingerprint, base=base)
    get_subkey_choice_from_bucket_signature = compile_get_subkey_choice_from_bucket_signature(
        get_subkey, signature_to_choice_fingerprint, base=base)

    # define the _find_signature_at function
    @njit(nogil=True, locals=dict(
        bucket=uint64, fpr=uint64, choice=uint64,
        query=uint64, slot=int64, v=uint64, s=uint64))
    def _find_signature_at(subtable, bucket, query):
        """
        Attempt to locate signature on a bucket,
        assuming choice == 0 indicates an empty space.
        Return (int64, uint64):
        Return (slot, value) if the signature 'query' was found,
            where 0 <= slot < bucketsize.
        Return (-1, fill) if the signature was not found,
            where fill >= 0 is the number of slots already filled.
        """
        for slot in range(bucketsize):
            if is_slot_empty_at(subtable, bucket, slot):
                return (int64(-1), uint64(slot))  # free slot, only valid if tight!

            s = get_signature_at(subtable, bucket, slot)
            if s == query:
                v = get_value_at(subtable, bucket, slot)
                return (slot, v)

        return (int64(-1), uint64(bucketsize))

    # define the update/store/overwrite functions

    update, update_ssk \
        = compile_update_by_randomwalk(choices, bucketsize,
            get_bucket_signature, _find_signature_at,
            get_item_at, set_item_at, set_value_at,
            get_subkey_from_bucket_signature,
            get_subtable_subkey_from_key,
            prefetch_bucket,
            update_value=update_value, overwrite=False,
            allow_new=True, allow_existing=True,
            maxwalk=maxwalk, prefetch=prefetch)

    update_existing, update_existing_ssk \
        = compile_update_by_randomwalk(choices, bucketsize,
            get_bucket_signature, _find_signature_at,
            get_item_at, set_item_at, set_value_at,
            get_subkey_from_bucket_signature,
            get_subtable_subkey_from_key,
            prefetch_bucket,
            update_value=update_value, overwrite=False,
            allow_new=False, allow_existing=True,
            maxwalk=maxwalk, prefetch=prefetch)

    store_new, store_new_ssk \
        = compile_update_by_randomwalk(choices, bucketsize,
            get_bucket_signature, _find_signature_at,
            get_item_at, set_item_at, set_value_at,
            get_subkey_from_bucket_signature,
            get_subtable_subkey_from_key,
            prefetch_bucket,
            update_value=None, overwrite=True,
            allow_new=True, allow_existing=False,
            maxwalk=maxwalk, prefetch=prefetch)

    overwrite, overwrite_ssk \
        = compile_update_by_randomwalk(choices, bucketsize,
            get_bucket_signature, _find_signature_at,
            get_item_at, set_item_at, set_value_at,
            get_subkey_from_bucket_signature,
            get_subtable_subkey_from_key,
            prefetch_bucket,
            update_value=update_value, overwrite=True,
            allow_new=True, allow_existing=True,
            maxwalk=maxwalk, prefetch=prefetch)

    overwrite_existing, overwrite_existing_ssk \
        = compile_update_by_randomwalk(choices, bucketsize,
            get_bucket_signature, _find_signature_at,
            get_item_at, set_item_at, set_value_at,
            get_subkey_from_bucket_signature,
            get_subtable_subkey_from_key,
            prefetch_bucket,
            update_value=update_value, overwrite=True,
            allow_new=False, allow_existing=True,
            maxwalk=maxwalk, prefetch=prefetch)

    # define the "reading" functions find_index, get_value, etc.

    @njit(nogil=True, locals=dict(
        key=uint64, default=uint64, NOTFOUND=uint64,
        bucket1=uint64, sig1=uint64, slot1=int64, val1=uint64,
        bucket2=uint64, sig2=uint64, slot2=int64, val2=uint64,
        bucket3=uint64, sig3=uint64, slot3=int64, val3=uint64,
        bucketbits=uint32, check2=uint32, check3=uint32))
    def find_index(subtable, subkey, default=U64_MINUSONE):
        """
        Return uint64: the linear table index the given key,
        or the default if the key is not present.
        """
        NOTFOUND = uint64(default)
        bucket, sig = get_bucket_signature(0, subkey)
        prefetch_bucket(subtable, bucket)

        for c in range(1, choices):
            # prefetch next bucket
            next_bucket, next_sig = get_bucket_signature(c, subkey)
            prefetch_bucket(subtable, next_bucket)

            # search signature in current bucket
            (slot, val) = _find_signature_at(subtable, bucket, sig)
            if slot >= 0:
                return uint64(uint64(bucket * bucketsize) + slot)
            if val < bucketsize:
                return NOTFOUND
            bucket = next_bucket
            sig = next_sig

        (slot, val) = _find_signature_at(subtable, bucket, sig)
        if slot >= 0:
            return uint64(uint64(bucket * bucketsize) + slot)
        if val < bucketsize:
            return NOTFOUND

        return NOTFOUND



    @njit(nogil=True, locals=dict(
        subkey=uint64, subtable=uint64, default=uint64, NOTFOUND=uint64,
        bucket1=uint64, sig1=uint64, slot1=int64, val1=uint64,
        bucket2=uint64, sig2=uint64, slot2=int64, val2=uint64,
        bucket3=uint64, sig3=uint64, slot3=int64, val3=uint64,
        bucketbits=uint32, check2=uint32, check3=uint32))
    def get_value_from_st_sk(subtable, subkey, default=uint64(0)):
        """
        Return uint64: the value for the given subkey,
        or the default if the subkey is not present.
        """

        NOTFOUND = uint64(default)
        bucket, sig = get_bucket_signature(0, subkey)
        prefetch_bucket(subtable, bucket)

        for c in range(1, choices):
            # prefetch next bucket
            next_bucket, next_sig = get_bucket_signature(c, subkey)
            prefetch_bucket(subtable, next_bucket)

            # search signature in current bucket
            (slot, val) = _find_signature_at(subtable, bucket, sig)
            if slot >= 0:
                return val
            if val < bucketsize:
                return NOTFOUND
            bucket = next_bucket
            sig = next_sig
        (slot, val) = _find_signature_at(subtable, bucket, sig)
        if slot >= 0:
            return val
        if val < bucketsize:
            return NOTFOUND

        return NOTFOUND

    @njit(nogil=True, locals=dict(
        subkey=uint64, subtable=uint64, default=uint64,
        bucket1=uint64, sig1=uint64, slot1=int64, val1=uint64,
        bucket2=uint64, sig2=uint64, slot2=int64, val2=uint64,
        bucket3=uint64, sig3=uint64, slot3=int64, val3=uint64,
        bucketbits=uint32, check2=uint32, check3=uint32))
    def get_value_and_choice_from_st_sk(subtable, subkey, default=uint64(0)):
        """
        Return (value, choice) for given subkey,
        where value is uint64 and choice is in {1,2,3} if subkey was found,
        but value=default and choice=0 if subkey was not found.
        """

        NOTFOUND = uint64(default)
        bucket, sig = get_bucket_signature(subkey, 0)
        prefetch_bucket(subtable, bucket)

        for c in range(1, choices):
            # prefetch next bucket
            next_bucket, next_sig = get_bucket_signature(subkey, c)
            prefetch_bucket(subtable, next_bucket)

            # search signature in current bucket
            (slot, val) = _find_signature_at(subtable, bucket, sig)
            if slot >= 0:
                return (val, c)
            if val < bucketsize:
                return NOTFOUND
            bucket = next_bucket
            sig = next_sig

        (slot, val) = _find_signature_at(subtable, bucket, sig)
        if slot >= 0:
            return (val, c)
        if val < bucketsize:
            return NOTFOUND

        return NOTFOUND

    @njit(nogil=True)
    def get_value_and_choice(key):
        st, sk = get_subtable_subkey_from_key(key)
        return get_value_and_choice_from_st_sk(st, sk)

    @njit(nogil=True)
    def get_value(key, default=uint64(0)):
        st, sk = get_subtable_subkey_from_key(key)
        return get_value_from_st_sk(st, sk, default=default)

    @njit(nogil=True, locals=dict(
        bucket=uint64, slot=int64, v=uint64, sig=uint64, c=uint64,
        f=uint64, key=uint64, p=uint64, s=int64, fill=uint64))
    def is_tight(ht):
        """
        Return (0,0) if hash is tight, or problem (key, choice).
        In the latter case, it means that there is an empty slot
        for key 'key' on bucket choice 'choice', although key is
        stored at a higher choice.
        """
        # TODO: why does this not iterate over subtables using _ssk functions?
        raise NotImplementedError("WARNING: is_tight is not supported")
        for bucket in range(nbuckets):
            for slot in range(bucketsize):
                sig = get_signature_at(ht, bucket, slot)
                (c, f) = signature_to_choice_fingerprint(sig)  # should be in 0,1,2,3.
                if c <= 1:
                    continue
                # c >= 2
                key = get_key2(bucket, f)
                p, s = get_bs1(key)
                (slot, val) = _find_signature_at(ht, p, s)
                if slot >= 0 or val != bucketsize:
                    return (uint64(key), 1)  # empty slot on 1st choice
                if c >= 3:
                    key = get_key3(bucket, f)
                    p, s = get_bs2(key)
                    (slot, val) = _find_signature_at(ht, p, s)
                    if slot >= 0 or val != bucketsize:
                        return (uint64(key), 2)  # empty slot on 2nd choice
                if c >= 4:
                    return (uint64(key), 9)  # should never happen, c=1,2,3.
        # all done, no problems
        return (0, 0)

    @njit(nogil=True, locals=dict(counter=uint64))
    def count_items(filter_func):
        """
        filter_func(key: uint64, value: uint64) -> bool  # function
        Return number of items satisfying the filter function (uint64).
        """
        counter = 0
        for st in range(subtables):
            for p in range(nbuckets):
                for s in range(bucketsize):
                    if is_slot_empty_at(st, p, s):
                        break
                    sig = get_signature_at(st, p, s)
                    value = get_value_at(st, p, s)
                    subkey = get_subkey_from_bucket_signature(p, sig)
                    key = get_key_from_subtable_subkey(st, subkey)
                    if filter_func(key, value):
                        counter += 1
        return counter

    @njit(nogil=True, locals=dict(pos=uint64))
    def get_items(filter_func, buffer):
        """
        filter_func(key: uint64, value: uint64) -> bool  # function
        buffer: uint64[:]  # buffer for keys
        Return number of items satisfying the filter function (uint64).
        Copy keys satisfying filter_func into buffer until it is full.
        (Additional keys are not copied, but counted.)
        """
        B = buffer.size
        pos = 0
        for st in range(subtables):
            for p in range(nbuckets):
                for s in range(bucketsize):
                    if is_slot_empty_at(st, p, s):
                        continue
                    sig = get_signature_at(st, p, s)
                    value = get_value_at(st, p, s)
                    subkey = get_subkey_from_bucket_signature(p, sig)
                    key = get_key_from_subtable_subkey(st, subkey)
                    if filter_func(key, value):
                        if pos < B:
                            buffer[pos] = key
                        pos += 1
        return pos

    # all methods are defined; return the hash object
    return create_SRHash(locals())


#######################################################################


def compile_getps_from_getpf(get_bfx, choice, fprbits):
    @njit(nogil=True, locals=dict(
        p=uint64, f=uint64, sig=uint64))
    def get_bsx(code):
        (p, f) = get_bfx(code)
        sig = uint64((choice << uint64(fprbits)) | f)
        return (p, sig)
    return get_bsx


def compile_update_by_randomwalk(
        choices, bucketsize,
        get_bucket_signature, _find_signature_at,
        get_item_at, set_item_at,
        set_value_at,
        get_subkey_from_bucket_signature,
        get_subtable_subkey_from_key,
        prefetch_bucket,
        *,
        update_value=None, overwrite=False,
        allow_new=False, allow_existing=False,
        maxwalk=1000, prefetch=False):
    """return a function that stores or modifies an item"""
    U64_MINUSONE = uint64(np.iinfo(np.uint64).max)

    LOCATIONS = choices * bucketsize
    if LOCATIONS < 2:
        raise ValueError(f"ERROR: Invalid combination of bucketsize={bucketsize} * choices={choices}")

    if (update_value is None or overwrite) and allow_existing:
        update_value = njit(nogil=True, locals=dict(
            old=uint64, new=uint64)
            )(lambda old, new: new)
    if not allow_existing:
        update_value = njit(nogil=True,
            locals=dict(old=uint64, new=uint64)
            )(lambda old, new: old)

    @njit(nogil=True, locals=dict(
        subkey=uint64, value=uint64, v=uint64,
        bucket1=uint64, sig1=uint64, slot1=int64, val1=uint64,
        bucket2=uint64, sig2=uint64, slot2=int64, val2=uint64,
        bucket3=uint64, sig3=uint64, slot3=int64, val3=uint64,
        c=uint64, bucket=uint64, steps=uint64,
        xsig=uint64, xval=uint64))
    def update_ssk(subtable, subkey, value):
        """
        Attempt to store given subkey with given value in hash table.
        If the subkey exists, the existing value may be updated or overwritten,
        or nothing may happen, depending on how this function was compiled.
        If the subkey does not exist, it is stored with the provided value,
        or nothing may happen, depending on how this function was compiled.

        Returns (status: int32, result: uint64).

        status: if status == 0, the subkey was not found,
            and, if allow_new=True, it could not be inserted either.
            If (status & 127 =: c) != 0, the subkey exists or was inserted w/ choice c.
            If (status & 128 != 0), the subkey was aleady present.

        result: If the subkey was already present (status & 128 != 0),
            then result is the new value that was stored.
            Otherwise (if status & 128 == 0), result is the walk length needed 
            to store the new (subkey, value) pair.
        """

        steps = 0
        bucket, sig = get_bucket_signature(0, subkey)
        prefetch_bucket(subtable, bucket)
        for c in range(1, choices):
            steps += 1
            next_bucket, next_sig = get_bucket_signature(c, subkey)
            prefetch_bucket(subtable, next_bucket)

            (slot, val) = _find_signature_at(subtable, bucket, sig)
            if slot != -1:  # found on bucket/choice
                v = update_value(val, value)
                if v != val:
                    set_value_at(subtable, bucket, slot, v)
                return (int32(128 | 1), v)
            elif val < bucketsize:  # not found, but space available at slot val1
                if allow_new:
                    v = update_value(0, value)
                    set_item_at(subtable, bucket, val, sig, v)
                    return (int32(1), steps)
                return (int32(0), steps)
            bucket, sig = next_bucket, next_sig

        (slot, val) = _find_signature_at(subtable, bucket, sig)
        if slot != -1:  # found on bucket/choice
            v = update_value(val, value)
            if v != val:
                set_value_at(subtable, bucket, slot, v)
            return (int32(128 | 1), v)
        elif val < bucketsize:  # not found, but space available at slot val1
            if allow_new:
                v = update_value(0, value)
                set_item_at(subtable, bucket, val, sig, v)
                return (int32(1), steps)
            return (int32(0), steps)

        if not allow_new:
            return (int32(0), steps)

        # Pick a random location;
        # store item there and continue with evicted item.
        location = randint(LOCATIONS)
        slot = location // choices
        c = location % choices
        bucket, sig = get_bucket_signature(c, subkey)
        xsig, xval = get_item_at(subtable, bucket, slot)
        v = update_value(0, value)
        set_item_at(subtable, bucket, slot, sig, v)
        subkey = get_subkey_from_bucket_signature(bucket, xsig)
        return do_random_walk(subtable, subkey, xval, bucket, location, steps)

    @njit(nogil=True, locals=dict(
        subkey=uint64, value=uint64,
        bucket1=uint64, sig1=uint64, slot1=int64, val1=uint64,
        bucket2=uint64, sig2=uint64, slot2=int64, val2=uint64,
        bucket3=uint64, sig3=uint64, slot3=int64, val3=uint64,
        c=uint64, bucket=uint64, steps=uint64,
        oldbucket=uint64, lastlocation=uint64,
        xsig=uint64, xval=uint64))
    def do_random_walk(subtable, subkey, value, oldbucket, lastlocation, steps):
        while steps <= maxwalk:
            bucket, sig = get_bucket_signature(0, subkey)
            for c in range(1, choices):
                next_bucket, next_sig = get_bucket_signature(c, subkey)
                prefetch_bucket(subtable, next_bucket)

                steps += (bucket != oldbucket)
                (slot, val) = _find_signature_at(subtable, bucket, sig)
                if slot != -1:
                    print(slot)
                assert slot == -1  # -1 means empty slot or full buckets
                if val < bucketsize:  # not found, but space available at slot val1
                    set_item_at(subtable, bucket, val, sig, value)
                    return (int32(1), steps)

                bucket, sig = next_bucket, next_sig

            steps += (bucket != oldbucket)
            (slot, val) = _find_signature_at(subtable, bucket, sig)
            if slot != -1:
                print(slot)
            assert slot == -1  # -1 means empty slot or full buckets
            if val < bucketsize:  # not found, but space available at slot val1
                set_item_at(subtable, bucket, val, sig, value)
                return (int32(1), steps)

            location = randint(LOCATIONS)
            while location == lastlocation:
                location = randint(LOCATIONS)
            lastlocation = location
            slot = location // choices
            c = location % choices
            bucket, sig = get_bucket_signature(c, subkey)
            oldbucket = bucket
            xsig, xval = get_item_at(subtable, bucket, slot)
            set_item_at(subtable, bucket, slot, sig, value)
            subkey = get_subkey_from_bucket_signature(bucket, xsig)
            value = xval

        return (int32(0), steps)

    @njit(nogil=True, locals=dict(
        subtable=uint64, subkey=uint64))
    def update(key, value):
        subtable, subkey = get_subtable_subkey_from_key(key)
        return update_ssk(subtable, subkey, value)

    return update, update_ssk
