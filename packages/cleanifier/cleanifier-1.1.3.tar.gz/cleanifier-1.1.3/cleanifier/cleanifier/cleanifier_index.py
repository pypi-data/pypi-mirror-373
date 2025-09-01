"""
cleanifier index --index human --files chm13v2.0.fa.gz -n 4_000_000_000 --fill 0.94 --mask '######_#######_###_#######_######' --subtables 15 --maxwalk 10000 --filter --fpr 14 --windowsize 2 --threads-read 2 --threads-split 4
"""

import os
import sys

from math import ceil
from importlib import import_module

import numpy as np
from numpy.random import randint
from numpy.random import seed as randomseed
from numba import njit

from ..lowlevel import debug
from ..lowlevel.conpro import (
    ConsumerProducer,
    CPInputMode,
    run_cps,
)
from ..parameters import get_valueset_and_parameters, parse_parameters
from ..srhash import get_nbuckets, print_statistics
from ..io.generalio import cptask_read_file
from ..io.generaldsio import save_data_structure
from ..cptasks_kmers import (
    compile_cptask_scatter_kmers_from_linemarked,
    compile_cptask_insert_filtered_subkeys,
)
from ..subtable_hashfunctions import compile_get_subtable_subkey_from_key

DEFAULT_HASHTYPE = "s3c_fbcbvb"
new_encoding = True


def check_threads(args):
    adjust = (args.subtables is None) or (args.threads_split is None) or (args.threads_read is None)
    # 1. Define number of subtables
    cpus = os.cpu_count()
    subtables = args.subtables
    if subtables is None:
        subtables = max(min(cpus // 2 - 1, cpus - 3, 19), 1)
        if (subtables % 2) == 0:
            subtables += 1
    if subtables < 1:
        debugprint0(f"- Error: At least one subtable is required, but {subtables=}")
        sys.exit(1)
    if subtables % 2 == 0:
        debugprint0(f"- Error: Number of subtables must be odd, but {subtables=}")
        sys.exit(1)
    # 2. Define threads for reading files
    threads_read = args.threads_read
    if threads_read is None:
        threads_read = int(ceil(subtables / 10))  # who knows?
    # 3. Define threads for
    threads_split = args.threads_split
    if threads_split is None:
        threads_split = 2 * threads_read
    if adjust and (subtables + threads_read + threads_split >= cpus):
        threads_read = 1
        threads_split = 2
    # 4. Return results
    assert threads_read >= 1
    assert threads_split >= 1
    return (subtables, threads_read, threads_split)


def create_new_index(nsubtables, args):
    """
    Initialize a filter and a hash table.
    Make sure they have the same 0-th hash function mapping to subtables.
    """
    valueset = ('set',)  # ToDo empty value set?
    P = get_valueset_and_parameters(valueset, mask=args.mask, rcmode="max")
    (values, _, rcmode, mask) = P
    universe = int(4 ** mask.k)

    parameters = parse_parameters(None, args)
    (nobjects, hashtype, aligned, hashfunc_str, bucketsize, nfingerprints, fill) = parameters
    debugprint2(f"- Parameters: {parameters}")

    if hashtype == "default":
        hashtype = DEFAULT_HASHTYPE
    debugprint1(f"- using hash type '{hashtype}''.")

    hashmodule = import_module("..hash_" + hashtype, __package__)
    build_hash = hashmodule.build_hash
    nvalues = values.NVALUES
    update_value = values.update
    n = get_nbuckets(nobjects, bucketsize, fill) * bucketsize
    debugprint1(f"- allocating hash table (with {nsubtables} subtables) for {n=} objects in total.")
    debugprint1(f"- hash function string: '{hashfunc_str}'...")
    h = build_hash(universe, n, nsubtables, bucketsize,
        hashfunc_str, nvalues, update_value,
        aligned=aligned, nfingerprints=nfingerprints,
        maxwalk=args.maxwalk, shortcutbits=args.shortcutbits)

    debugprint0(f"- memory for hash table: {h.mem_bytes/(2**30):.3f} GiB (with {nsubtables} subtables)")
    if not args.walkseed:
        args.walkseed = randint(0, high=2**32 - 1, dtype=np.uint64)
    randomseed(args.walkseed)
    debugprint2(f"- walkseed: {args.walkseed}")
    return (h, values, valueset, mask, rcmode)


def create_new_filter(nsubfilters, args):
    """
    Initialize a filter and a hash table.
    Make sure they have the same 0-th hash function mapping to subtables.
    """
    valueset = ('set',)  # ToDo empty value set?
    P = get_valueset_and_parameters(valueset, mask=args.mask, rcmode="max")
    (_, _, rcmode, mask) = P
    universe = int(4 ** mask.k)

    parameters = parse_parameters(None, args)
    (nobjects, _, _, hashfunc_str, _, _, fill) = parameters

    slots = nobjects / fill
    if hashfunc_str == 'random':
        subfilter_hashfunc_str = fingerprint_hashfunc_str = window_hashfunc_str = offset_hashfunc_str = hashfunc_str
    else:
        subfilter_hashfunc_str, fingerprint_hashfunc_str, window_hashfunc_str, offset_hashfunc_str = hashfunc_str.split(':')

    fltmodule = import_module("..filter_windowed_cuckoo", __package__)
    build_filter = fltmodule.build_filter
    debugprint1(f"- allocating filter (with {nsubfilters} subfilters) with {slots=} slots in total.")
    flt = build_filter(universe, nsubfilters, slots, args.windowsize, args.fpr,
        maxsteps=args.maxwalk, subfilter_hashfunc_str=subfilter_hashfunc_str,
        fingerprint_hashfunc_str=fingerprint_hashfunc_str, window_hashfunc_str=window_hashfunc_str,
        offset_hashfunc_str=offset_hashfunc_str)

    debugprint0(f"- memory for hash table: {flt.filterbits / (8 * 2**30):.3f} GiB (with {nsubfilters} subfilters)")
    if not args.walkseed:
        args.walkseed = randint(0, high=2**32 - 1, dtype=np.uint64)
    randomseed(args.walkseed)
    debugprint2(f"- walkseed: {args.walkseed}")
    return (flt, mask, rcmode)


def process_files(constant_value, index, fnames, mask, rcmode, *,
        maxfailures=0, maxwalk=1000,
        threads_read=1, threads_split=1, use_filter=False):

    # 1. Define jobs to read files
    read_jobs = ConsumerProducer(
        name='file_reader',
        tasks=[(cptask_read_file, fname, None, mask.w) for fname in fnames],
        nworkers=threads_read,
        noutbuffers_per_worker=3 * threads_split,
        specific_outbuffers_per_worker=True,
        datatype=np.uint8,
        infotype=np.int64,
        dataitems_per_buffer=2**16,
        infoitems_per_buffer=(2**16 // 200),
        infoitemsize=4,  # linemarks use 4 numbers per sequence
    )

    # 2. Define jobs to split k-mers
    _universe = 4**(mask.k)
    if use_filter:
        nsubtables = index.nsubfilters
        get_subfilter = index.private.get_subfilter

        @njit(nogil=True)
        def get_subfilter_key(key):
            subfilter = get_subfilter(key)
            return subfilter, key

        hashfunc0 = get_subfilter_key
        arr = index.array
    else:
        nsubtables = index.subtables
        hf0 = index.hashfuncs.split(":")[0]
        (hashfunc0, _) = compile_get_subtable_subkey_from_key(hf0, _universe, nsubtables)
        arr = index.hashtable

    n_splitter_jobs = threads_split
    nbuffers_per_worker_per_subtable = 3
    nbuffers_per_subtable = n_splitter_jobs * nbuffers_per_worker_per_subtable
    outbufsize = 2**16
    cptask_split = compile_cptask_scatter_kmers_from_linemarked(
        mask, rcmode, hashfunc0,
        nsubtables, nbuffers_per_subtable, outbufsize, new_encoding=new_encoding)

    splitter_jobs = ConsumerProducer(
        name='kmer_splitter',
        input=read_jobs,
        tasks=[(cptask_split, )] * n_splitter_jobs,
        noutbuffers_per_worker=(nsubtables * nbuffers_per_worker_per_subtable),
        datatype=np.uint64,
        dataitems_per_buffer=outbufsize,
        dataitemsize=1,
    )

    # 3. Define inserter jobs (one per subfilter/subtable)
    cptask_insert = compile_cptask_insert_filtered_subkeys(
        index, None, constant_value, maxfailures, maxwalk)
    actual_jobs = ConsumerProducer(
        name='kmer_filter_inserter',
        input=splitter_jobs,
        input_mode=(CPInputMode.GATHER, nbuffers_per_subtable),
        tasks=[(cptask_insert, st, arr, None) for st in range(nsubtables)],
        noutbuffers_per_worker=1,
        specific_outbuffers_per_worker=True,
        datatype=np.int64,
        dataitems_per_buffer=(maxwalk + 12),
        dataitemsize=1,
    )

    debugprint1("- cleanifier process_files: will now run several ConsumerProducers")
    failures = run_cps(read_jobs, splitter_jobs, actual_jobs)
    debugprint1(f"- cleanifier process_files: done; {failures=}")
    return failures == 0


def main(args):
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    starttime = timestamp0(msg="\n# cleanifier index")

    debugprint0("\n- (c) 2019-2025 by Jens Zentgraf, Johanna Elena Schmitz, Sven Rahmann, Algorithmic Bioinformatics, Saarland University")
    debugprint0("- Licensed under the MIT License")

    startbuild = timestamp0(msg=f"\n# Creating index {args.index}")
    nsubtables, threads_read, threads_split = check_threads(args)
    args.shortcutbits = int(args.shortcutbits)
    debugprint1(f"- threads: {nsubtables=}, {threads_read=}, {threads_split=}")

    if args.filter:
        use_filter, valuetup = True, None
        (index, mask, rcmode) = create_new_filter(nsubtables, args)
        stats = index.print_statistics

        def print_index_statistics(index, level):
            stats(index.array, level)
    else:
        use_filter = False
        (index, _, valuetup, mask, rcmode) = create_new_index(nsubtables, args)
        print_index_statistics = print_statistics

    if mask.k > 31:
        raise ValueError("masks with > 31 significant positions are not supported.")

    # process all files
    if args.files:
        success = process_files(1, index, args.files, mask, rcmode,
            maxfailures=0, maxwalk=args.maxwalk,
            threads_read=threads_read, threads_split=threads_split, use_filter=use_filter)

        if not success:
            debugprint0("- ERROR: Processing the provided files (--files) failed.")
            exit(1)

    timestamp0(starttime, msg="- Build index: wall time")
    timestamp0(starttime, msg="- Build index: wall time", minutes=True)

    # #################### Save Hash ####################

    optinfo = dict(walkseed=args.walkseed, maxwalk=args.maxwalk, maxfailures=0)
    appinfo = dict(rcmode=rcmode, mask=mask.tuple, k=mask.k)
    save_data_structure(args.index, index, optinfo, appinfo, valueinfo=valuetup)

    print_index_statistics(index, level=args.statistics)
    timestamp0(starttime, msg="- SUCCESS; total time")
    timestamp0(starttime, msg="- SUCCESS; total time", minutes=True)
