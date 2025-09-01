"""
hashio.py:
module for saving and loading hash tables with dimension and value information.

- The hash table itself is a flat uint64[:] numpy array
  and saved into a file with extension `.hash`.
- Hash-table-related information is stored separately in an `.info` file
  with the same name; this is a collection of pickled variables.
  1. hashinfo dictionary
     Required keys are those from the SRHash tuple or equivalent information.
     - hashtype: str
     - choices: int
     - nvalues: int
     - aligned: bool
     - universe: int
     - nslots: int (true number of slots, corresponding to --fill 1.0)
     - subtables: int
     - nbuckets: int
     - bucketsize: int
     - nfingerprints: int == -1
     - mem_bytes
     - shortcutbits: int
     - hashfuncs: tuple[str]
  2. valueinfo: tuple[str] (like ('count', '16')),
     contains sufficient information about the used value set:
     the name first, and then any parameters (as strings!) required for that value set
  3. optinfo dictionary, contains optional hash table data, e.g. about construction:
     - walkseed: int (the random seed used for construction)
     - maxwalk: int (the maxwalk parameter used for construciton)
     - maxfailures: int (maximum number of failures tolerated during construction)
  4. appinfo dictionary, arbitrary application-specific information;
     e.g. the following information is necessary if k-mers are stored:
     - rcmode: str
     - mask: Mask (k, w, maskstring, masktuple), such that 4**k == universe
     Other applications may define and use their own additional keys.
"""

import pickle  # for binary files
import json  # for text files
from importlib import import_module
from os import stat as osstat
from os.path import basename
from multiprocessing import resource_tracker
from multiprocessing.shared_memory import SharedMemory

import numpy as np
import numba as nb
from numba import njit

from ..mathutils import bitsfor, nextpower as nextpow2
from ..lowlevel import debug
from ..lowlevel.aligned_arrays import aligned_zeros
from ..lowlevel.intbitarray import intbitarray
from ..lowlevel.libc import write_block, write_uint64, write_dna


_ATTRS_TO_SAVE = "hashtype choices nvalues subtables aligned universe nslots=n nbuckets bucketsize nfingerprints mem_bytes shortcutbits hashfuncs".split()
_ATTR_PAIRS = [((name if '=' not in name else name.split("=")[0]), (name if '=' not in name else name.split("=")[1])) for name in _ATTRS_TO_SAVE]
# TODO: see comment in save_hash on how to get rid of these


def write_array(fname, arr):
    """
    Write a single numpy array to disk, fast, using `a.tofile(fid)`.
    [See also the discussion at https://github.com/divideconcept/fastnumpyio:
    The problem with their save and pack approach is that it copies the data
    at least once (from a numpy buffer to bytes), increasing memory requirements by 2x.
    We cannot afford to do that.]
    The .tofile method just writes bytes, so files are not transferable between
    machines with different endianness.
    AMD Ryzen, Apple M1/M2, Intel Core processors all use little endian.
    Compute and return a simple checksum of the first 256 elements.
    """
    with open(fname, "wb") as fout:
        arr.tofile(fout)
    checksum = int(arr[:256].sum())
    return checksum


def load_array(fname, check=None, byte_alignment=64):
    """
    Load and return an array from fname (uint64[:]) only.
    Optionally specify a checksum of the first 256 values.
    """
    fsize = osstat(fname).st_size  # file size in bytes
    assert fsize % 8 == 0
    n_uint64 = fsize // 8
    arr = aligned_zeros(n_uint64, byte_alignment=byte_alignment)  # allocate uint64[:]
    b = arr.view(np.uint8)         # view it as byte array
    assert b.size == fsize
    with open(fname, "rb") as fin:
        fin.readinto(b)
    if check is not None:
        checksum = int(arr[:256].sum())
        if checksum != check:
            raise RuntimeError(f"- ERROR: hashio.load_array: {checksum=} does not match expected {check}")
    return arr


def load_array_into(fname, arr, *, check=None, allow_short=False):
    # Load the numpy array stored in the file named `fname`
    # into the existing numpy array `arr`,
    # which must be the same size as the file (unless allow_short=True),
    # and of dtype uint64.
    # If `check` is a given integer, compare it against a computed checksum
    # from the file. Return whether we made a check.
    # (If we make a check and it fails, we raise a RuntimeError.)
    dtype, size = arr.dtype, arr.size
    fsize = osstat(fname).st_size  # file size in bytes
    assert fsize % 8 == 0
    n_uint64 = fsize // 8
    if dtype != np.uint64:
        raise RuntimeError(f"ERROR: hashio.load_array_into: Provided array's {dtype=} does not match uint64")
    if (size > n_uint64) or ((not allow_short) and size != n_uint64):
        raise RuntimeError(f"ERROR: hashio.load_array_into: Provided array's {size=} does not match file's {n_uint64=}")
    with open(fname, "rb") as fin:
        fin.readinto(arr.view(np.uint8))  # file reading uses bytes, not uint64s.
    if check is not None:
        checksum = int(arr[:256].sum())
        if checksum != check:
            raise RuntimeError(f"ERROR: hashio.load_array_into: {checksum=} does not match given {check}")
        return True  # successful check
    return False  # no check was done


def save_hash(outname, h, valueinfo, optinfo=dict(), appinfo=dict(), *, _pairs=_ATTR_PAIRS):
    """
    Save the hash table `h` in `{outname}.hash` (array only)
    and `{outname}.info` (dicts with information).
    (If outname already ends with .info, .hash, or just ., remove that suffix.)
    """
    # TODO: At some point, get rid of _pairs, and just store all attributes defined in SRHash, using _fields (except .hashtable of course).
    if outname.endswith((".", ".info", ".hash")):
        outname = outname.rsplit(".", 1)[0]
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    if outname.casefold() in ("/dev/null", "null", "none"):
        debugprint0(f"- not writing special null output file '{outname}'")
        return None
    startout = timestamp0(msg=f"- saving hash table '{outname}'")
    debugprint0(f"- writing output files '{outname}.hash', '{outname}.info'...")
    hashinfo = {name: getattr(h, hname) for (name, hname) in _pairs}
    obj = (hashinfo, valueinfo, optinfo, appinfo)
    pickle.dumps(obj)  # dummy export to string: test if it works before writing huge array
    checksum = write_array(f"{outname}.hash", h.hashtable)
    hashinfo['checksum'] = checksum
    with open(f"{outname}.info", "wb") as fout:
        pickle.dump(obj, fout)
    timestamp0(startout, msg="- writing output: wall time")
    return checksum


def load_hash(filename, *, shared_memory=False, info_only=False, quiet=False):
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp

    if filename.endswith((".", ".info", ".hash")):
        filename = filename.rsplit(".", 1)[0]

    if not info_only:
        if not quiet:
            startload = timestamp0(msg=f"- loading hash table {filename}")
            debugprint0(f"- hash files '{filename}.info', '{filename}.hash'...")
        else:
            startload = timestamp1(msg=f"- loading hash table {filename}")
            debugprint1(f"- hash files '{filename}.info', '{filename}.hash'...")
    else:
        debugprint1(f"- loading hash info '{filename}.info'")

    with open(f"{filename}.info", "rb") as finfo:
        infotup = pickle.load(finfo)
    (hashinfo, valueinfo, optinfo, appinfo) = infotup
    debugprint1(f"- importing value set {valueinfo}.")
    vmodule = import_module(f"..values.{valueinfo[0]}", __package__)
    values = vmodule.initialize(*(valueinfo[1:]))
    if info_only:
        return None, values, infotup

    update_value = values.update
    hashtype = hashinfo['hashtype']
    subtables = hashinfo['subtables']
    aligned = bool(hashinfo['aligned'])
    universe = hashinfo['universe']
    n = hashinfo['nslots']
    shortcutbits = hashinfo['shortcutbits']
    # nbuckets = hashinfo['nbuckets']
    bucketsize = hashinfo['bucketsize']
    # assert (nbuckets-2)*bucketsize < n <= nbuckets*bucketsize,\
    #     f"Error: nbuckets={nbuckets}, bucketsize={bucketsize}: {nbuckets*bucketsize} vs. {n}"
    nfingerprints = hashinfo['nfingerprints']
    nvalues = hashinfo['nvalues']
    assert nvalues == values.NVALUES, f"Error: inconsistent nvalues (info: {nvalues}; valueset: {values.NVALUES})"
    hashfuncs = hashinfo['hashfuncs']
    if isinstance(hashfuncs, bytes):
        hashinfo['hashfuncs'] = hashfuncs = hashfuncs.decode("ASCII")
        if not quiet:
            debugprint0("- WARNING: Converting hashfuncs from bytes to str")
    checksum = hashinfo['checksum']

    debugprint1(f"- hash functions: {hashfuncs}")
    maxwalk = optinfo.get('maxwalk', -1)
    debugprint1(f"- building hash table of type '{hashtype}'...")
    m = import_module(f"..hash_{hashtype}", __package__)

    init = True
    shm = None
    if shared_memory:
        filename = basename(filename)
        shm = SharedMemory(name=filename, create=False)
        resource_tracker.unregister(shm._name, "shared_memory")
        shm_buf = shm.buf
        assert shm_buf.shape[0] % 8 == 0
        assert shm_buf.itemsize == 1
        init = np.ndarray(shm_buf.shape[0] // 8, dtype=np.uint64, buffer=shm_buf)

    if hashtype == 'new':
        choices = hashinfo['choices']
        h = m.build_hash(universe, n, subtables, choices,
            bucketsize, hashfuncs, nvalues, update_value,
            aligned=aligned, nfingerprints=nfingerprints,
            init=init, maxwalk=maxwalk, shm=shm)
    else:
        h = m.build_hash(universe, n, subtables,
            bucketsize, hashfuncs, nvalues, update_value,
            aligned=aligned, nfingerprints=nfingerprints,
            init=init, maxwalk=maxwalk, shortcutbits=shortcutbits, shm=shm)
    if not shared_memory:
        debugprint1(f"- loading '{filename}.hash' into array")
        checked = load_array_into(f"{filename}.hash", h.hashtable, check=checksum)
        if checked:
            debugprint2(f"- checksum {checksum} successfully verified. Nice.")
    else:  # checksum for shared memory load
        check = h.hashtable[:256].sum()
        if check != checksum:
            raise RuntimeError(f"ERROR loading '{filename}.hash' into shared memory: {checksum=} does not match expected {check}")
        else:
            debugprint2(f"- checksum {checksum} successfully verified. Nice.")
    if not quiet:
        timestamp0(startload, msg=f"- time to load '{filename}'")
    else:
        timestamp1(startload, msg=f"- time to load '{filename}'")
    return h, values, (hashinfo, valueinfo, optinfo, appinfo)


# #########################################################
# functions for single array exports ######################

_nbytes = {1: 1, 2: 1, 4: 1, 8: 1, 16: 2, 32: 4, 64: 8}
_npdtypes = {1: np.uint8, 2: np.uint8, 4: np.uint8, 8: np.uint8, 16: np.uint16, 32: np.uint32, 64: np.uint64}
_nbdtypes = {1: nb.uint8, 2: nb.uint8, 4: nb.uint8, 8: nb.uint8, 16: nb.uint16, 32: nb.uint32, 64: nb.uint64}


def compile_text_exporter(h, f, nvalues, infotup):
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    hp = h.private
    is_slot_empty_at = hp.is_slot_empty_at
    get_item_at = hp.get_item_at
    # signature_to_choice_fingerprint = hp.signature_to_choice_fingerprint
    get_subkey_choice_from_bucket_signature = hp.get_subkey_choice_from_bucket_signature
    get_key_from_subtable_subkey = hp.get_key_from_subtable_subkey
    nsubtables, nbuckets, bucketsize = h.subtables, h.nbuckets, h.bucketsize
    universe, choices = h.universe, h.choices
    bits = (bitsfor(universe), bitsfor(choices), bitsfor(nvalues))
    debugprint1(f"- bits for (keys, choices, values): {bits}")
    powbits = tuple(nextpow2(b) for b in bits)
    NBK, NBC, NBV = [_nbytes[pb] for pb in powbits]
    _keytype, _choicetype, _valuetype = [_nbdtypes[pb] for pb in powbits]
    uint64 = nb.uint64

    @njit(nogil=True)
    def exporter(ht, buf, fdk, fdc, fdv):
        total = 0
        for st in range(nsubtables):
            for bucket in range(nbuckets):
                for slot in range(bucketsize):
                    if is_slot_empty_at(ht, st, bucket, slot):
                        break  # go to next bucket
                    sig, val = get_item_at(ht, st, bucket, slot)
                    sbk, chc = get_subkey_choice_from_bucket_signature(bucket, sig)
                    key = get_key_from_subtable_subkey(st, sbk)
                    if not f(key, chc, val):
                        continue  # go to next slot if filter not satisfied
                    write_uint64(fdk, uint64(key), buf)
                    write_uint64(fdc, uint64(chc), buf)
                    write_uint64(fdv, uint64(val), buf)
                    total += 1
        return total

    _buffer = np.zeros((2, 128), dtype=np.uint8)
    return exporter, bits, _buffer


def compile_dna_exporter(h, f):
    hp = h.private
    is_slot_empty_at = hp.is_slot_empty_at
    get_item_at = hp.get_item_at
    get_subkey_choice_from_bucket_signature = hp.get_subkey_choice_from_bucket_signature
    get_key_from_subtable_subkey = hp.get_key_from_subtable_subkey
    nsubtables, nbuckets, bucketsize = h.subtables, h.nbuckets, h.bucketsize
    bits = bitsfor(h.universe)
    assert bits % 2 == 0
    k = bits // 2  # k-mer length
    uint64 = nb.uint64

    @njit(nogil=True)
    def exporter(ht, buf, vbuf, fd):
        total = 0
        for st in range(nsubtables):
            for bucket in range(nbuckets):
                for slot in range(bucketsize):
                    if is_slot_empty_at(ht, st, bucket, slot):
                        break  # go to next bucket
                    sig, val = get_item_at(ht, st, bucket, slot)
                    sbk, chc = get_subkey_choice_from_bucket_signature(bucket, sig)
                    key = get_key_from_subtable_subkey(st, sbk)
                    if not f(key, chc, val):
                        continue  # go to next slot if filter not satisfied
                    write_dna(fd, uint64(key), buf)
                    write_uint64(fd, uint64(val), vbuf)
                    total += 1
        return total

    _buffer = np.zeros(k + 1, dtype=np.uint8)
    _buffer[k] = 32  # space
    _vbuffer = np.zeros((2, 128), dtype=np.uint8)
    return exporter, k, _buffer, _vbuffer


def compile_data_exporter(h, f, nvalues, infotup, packed):
    # (hashinfo, valueinfo, optinfo, appinfo) = infotup
    # f is a compiled filter function
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    hp = h.private
    is_slot_empty_at = hp.is_slot_empty_at
    get_item_at = hp.get_item_at
    # signature_to_choice_fingerprint = hp.signature_to_choice_fingerprint
    get_subkey_choice_from_bucket_signature = hp.get_subkey_choice_from_bucket_signature
    get_key_from_subtable_subkey = hp.get_key_from_subtable_subkey
    nsubtables, nbuckets, bucketsize = h.subtables, h.nbuckets, h.bucketsize
    universe, choices = h.universe, h.choices
    bits = (bitsfor(universe), bitsfor(choices), bitsfor(nvalues))
    debugprint1(f"- bits for (keys, choices, values): {bits}")
    # define buffers
    N = 2**14  # N: buffer size in items: 16K or 2**14
    if packed:
        assert N % 64 == 0, f"ERROR: {N=} must be divisible by 64!"
        # Note: number of uint64: b * (N//64)
        ibuffers = tuple(intbitarray(N, b) for b in bits)
        setk, setc, setv = [b.set for b in ibuffers]
        buffers = [b.array for b in ibuffers]
    else:
        powbits = tuple(nextpow2(b) for b in bits)
        NBK, NBC, NBV = [_nbytes[pb] for pb in powbits]
        _keytype, _choicetype, _valuetype = [_nbdtypes[pb] for pb in powbits]
        buffers = tuple(np.empty(N, dtype=_npdtypes[pb]) for pb in powbits)

    if packed:  # packed arrays
        @njit(nogil=True)
        def exporter(ht, bufk, bufc, bufv, fdk, fdc, fdv):
            total = p = 0
            for st in range(nsubtables):
                for bucket in range(nbuckets):
                    for slot in range(bucketsize):
                        if is_slot_empty_at(ht, st, bucket, slot):
                            break  # go to next bucket
                        sig, val = get_item_at(ht, st, bucket, slot)
                        sbk, chc = get_subkey_choice_from_bucket_signature(bucket, sig)
                        key = get_key_from_subtable_subkey(st, sbk)
                        if not f(key, chc, val):
                            continue  # go to next slot if filter not satisfied
                        setk(bufk, p, key)
                        setc(bufc, p, chc)
                        setv(bufv, p, val)
                        p += 1
                        if p >= N:
                            total += p
                            write_block(fdk, bufk, (N // 8) * bits[0])
                            write_block(fdc, bufc, (N // 8) * bits[1])
                            write_block(fdv, bufv, (N // 8) * bits[2])
                            p = 0
            total += p
            write_block(fdk, bufk, (N // 8) * bits[0])
            write_block(fdc, bufc, (N // 8) * bits[1])
            write_block(fdv, bufv, (N // 8) * bits[2])
            return total

    else:  # normal arrays
        @njit(nogil=True)
        def exporter(ht, bufk, bufc, bufv, fdk, fdc, fdv):
            total = p = 0
            for st in range(nsubtables):
                for bucket in range(nbuckets):
                    for slot in range(bucketsize):
                        if is_slot_empty_at(ht, st, bucket, slot):
                            break  # go to next bucket
                        sig, val = get_item_at(ht, st, bucket, slot)
                        sbk, chc = get_subkey_choice_from_bucket_signature(bucket, sig)
                        key = get_key_from_subtable_subkey(st, sbk)
                        if not f(key, chc, val):
                            continue  # go to next slot if filter not satisfied
                        bufk[p] = _keytype(key)
                        bufc[p] = _choicetype(chc)
                        bufv[p] = _valuetype(val)
                        p += 1
                        if p >= N:
                            total += p
                            write_block(fdk, bufk, N * NBK)
                            write_block(fdc, bufc, N * NBC)
                            write_block(fdv, bufv, N * NBV)
                            p = 0
            total += p
            write_block(fdk, bufk, p * NBK)
            write_block(fdc, bufc, p * NBC)
            write_block(fdv, bufv, p * NBV)
            return total

    return exporter, bits, buffers


def export_hash(h, nvalues, infotup, prefix, fmt, filterfunc):
    FORMATS = ("native", "packed", "text", "dna")
    if fmt == "text":
        return _export_to_textfiles(h, nvalues, infotup, prefix, filterfunc)
    elif fmt == "dna":
        return _export_to_dnafile(h, prefix, filterfunc)
    elif fmt in ("native", "packed"):
        return _export_to_datafiles(h, nvalues, infotup, prefix, fmt, filterfunc)
    else:
        raise ValueError(f"ERROR: format '{fmt}' is not supported; choose from {FORMATS}.")


def _export_to_datafiles(h, nvalues, infotup, prefix, fmt, filterfunc):
    # get buffers for keys, choices and values;
    # open output files, get their fd numbers;
    # pass it all to a function that scans the table
    assert fmt in ("native", "packed")
    packed = (fmt == "packed")
    exporter, bits, buffers = compile_data_exporter(h, filterfunc, nvalues, infotup, packed)
    bufk, bufc, bufv = buffers
    fnamek, fnamec, fnamev, fnamei = [
        f"{prefix}.{datatype}.data"
        for datatype in ("key", "chc", "val", "inf")
    ]
    ht = h.hashtable
    with open(fnamek, "wb") as fk, open(fnamec, "wb") as fc, open(fnamev, "wb") as fv:
        fdk, fdc, fdv = fk.fileno(), fc.fileno(), fv.fileno()
        written = exporter(ht, bufk, bufc, bufv, fdk, fdc, fdv)
    info = dict(
        packed=packed, size=written,
        bits_key=bits[0], bits_choice=bits[1], bits_value=bits[2],
        infotup=infotup,
        )
    with open(fnamei, "wb") as fi:
        pickle.dump(info, fi)
    return written


def _export_to_textfiles(h, nvalues, infotup, prefix, filterfunc):
    exporter, bits, _buffer = compile_text_exporter(h, filterfunc, nvalues, infotup)
    fnamek, fnamec, fnamev = [f"{prefix}.{datatype}.txt" for datatype in ("key", "chc", "val")]
    ht = h.hashtable
    with open(fnamek, "wb") as fk, open(fnamec, "wb") as fc, open(fnamev, "wb") as fv:
        fdk, fdc, fdv = fk.fileno(), fc.fileno(), fv.fileno()
        written = exporter(ht, _buffer, fdk, fdc, fdv)
    info = dict(
        format="text", packed=False, size=written,
        bits_key=bits[0], bits_choice=bits[1], bits_value=bits[2],
        infotup=infotup,
        )
    fnamei = f"{prefix}.inf.txt"  # text info file is exported to json
    with open(fnamei, "wt") as fi:
        json.dump(info, fi)
    return written


def _export_to_dnafile(h, prefix, filterfunc):
    exporter, k, _buffer, _vbuffer = compile_dna_exporter(h, filterfunc)
    fnamek = f"{prefix}.dna.txt"
    ht = h.hashtable
    with open(fnamek, "wb") as f:
        fd = f.fileno()
        written = exporter(ht, _buffer, _vbuffer, fd)
    return written


def load_exported_info(fname):
    with open(f"{fname}.inf.data", "rb") as finfo:
        info = pickle.load(finfo)
    return info


def load_exported_data(prefix, info, *, keys=True, choices=False, values=False):
    packed = info['packed']
    n = info['size']
    result = []
    for (flag, bitname, ext) in [
            (keys, 'bits_key', 'key'),
            (choices, 'bits_choice', 'chc'),
            (values, 'bits_value', 'val'),
            ]:
        if flag:
            fname = f"{prefix}.{ext}.data"
            # print(f"*** Loading {fname}")
            bits = info[bitname]
            if packed:
                R = intbitarray(n, bits)
                load_array_into(fname, R.array, allow_short=True)
            else:
                dtype = _npdtypes[nextpow2(bits)]
                R = np.empty(n, dtype=dtype)
                with open(fname, "rb") as fin:
                    fin.readinto(R.view(np.uint8))
            result.append(R)
    return tuple(result) if len(result) > 1 else (result[0] if len(result) == 1 else None)
