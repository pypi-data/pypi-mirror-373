# parameters.py: parameter manipulations
# (c) Sven Rahmann, 2021-2023

import os
from importlib import import_module
from .mask import create_mask


def set_threads(args, argname="threads"):
    threads = getattr(args, argname, None)
    if threads is None:
        return
    threads = str(threads)
    env = os.environ
    env["OMP_NUM_THREADS"] = threads
    env["OPENBLAS_NUM_THREADS"] = threads
    env["MKL_NUM_THREADS"] = threads
    env["VECLIB_MAXIMUM_THREADS"] = threads
    env["NUMEXPR_NUM_THREADS"] = threads
    env["NUMBA_NUM_THREADS"] = threads
    env["NUMBA_THREADING_LAYER"] = "omp"


def get_valueset_and_parameters(valueset, *, rcmode=None, mask=None, strict=True):
    # NOTE: strict is currently not used.
    # NOTE: does not deal with minimizer size anymore; calling code needs to be changed
    # NOTE: vstr is not needed anymore.
    if isinstance(valueset, list):
        valueset = tuple(valueset)
    vimport = "values." + valueset[0]
    vmodule = import_module("." + vimport, __package__)
    values = vmodule.initialize(*(valueset[1:]))
    vstr = " ".join((vimport,) + valueset[1:])
    if not rcmode:
        rcmode = values.RCMODE
    mymask = create_mask(mask)
    return (values, vstr, rcmode, mymask)


def parse_parameters(parameters, args, *, singles=True):
    if parameters is not None:
        (nobjects, hashtype, aligned, hashfuncs, bucketsize, nfingerprints, fill) \
            = parameters
    else:  # defaults
        (nobjects, hashtype, aligned, hashfuncs, bucketsize, nfingerprints, fill) \
            = (-1, "default", False, "random", 0, -1, 0.9)
    # process single command line arguments
    if singles:
        if args.nobjects is not None:
            nobjects = args.nobjects
        if "type" in args and args.type is not None:
            hashtype = args.type
        if args.aligned is not None:
            aligned = args.aligned
        if hasattr(args, 'hashfunctions') and args.hashfunctions is not None:
            hashfuncs = args.hashfunctions
        if args.bucketsize is not None:
            bucketsize = args.bucketsize
        if args.fill is not None:
            fill = args.fill
    # pack up and return
    parameters = (nobjects, hashtype, aligned, hashfuncs, bucketsize, nfingerprints, fill)
    return parameters
