import pickle  # for binary files
from os import stat as osstat
from importlib import import_module
from os.path import basename
from multiprocessing import resource_tracker
from multiprocessing.shared_memory import SharedMemory

import numpy as np

from ..lowlevel import debug
from .hashio import write_array


def load_array_into(fname, arr, *, check=None, allow_short=False):
    # Return whether we made a check.
    # (If we make a check at it fails, it will raise RuntimeError)
    dtype, size = arr.dtype, arr.size
    fsize = osstat(fname).st_size  # file size in bytes
    assert fsize % 8 == 0
    n_uint64 = fsize // 8
    if dtype != np.uint64:
        raise RuntimeError(f"- ERROR: filterio.load_array_into: Provided array's {dtype=:_} does not match uint64")
    if (size > n_uint64) or ((not allow_short) and size != n_uint64):
        raise RuntimeError(f"- ERROR: filterio.load_array_into: Provided array's {size=:_} does not match file's {n_uint64=:_}")
    with open(fname, "rb") as fin:
        fin.readinto(arr.view(np.uint64))
    if check is not None:
        checksum = int(arr[:256].sum())
        if checksum != check:
            raise RuntimeError(f"- ERROR: filterio.load_array_into: {checksum=} does not match expected {check}")
        else:
            return True
    return False


def save_filter(outname, fltr, optinfo=dict(), appinfo=dict()):
    """
    Save the filter array fltr.array in `{outname}.filter` (array only)
    and `{outname}.info` (dicts with information)
    """
    if outname.endswith((".", ".info", ".filter")):
        outname = outname.rsplit(".", 1)[0]
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    startout = timestamp0(msg="\n## Output")
    if outname.casefold() in ("/dev/null", "null", "none"):
        debugprint0(f"- not writing special null output file '{outname}'")
        return None
    debugprint0(f"- writing output files '{outname}.filter', '{outname}.info'...")
    filterinfo = dict()
    for field in fltr._fields:
        if field in ('private', 'array'):
            continue
        attr = getattr(fltr, field)
        if isinstance(attr, np.ndarray) or callable(attr):
            continue
        filterinfo[field] = attr
        debugprint2(f"  - {field}: {type(attr)} {attr}")
    obj = (filterinfo, optinfo, appinfo)
    pickle.dumps(obj)
    checksum = write_array(f"{outname}.filter", fltr.array)
    filterinfo['checksum'] = checksum
    with open(f"{outname}.info", "wb") as fout:
        pickle.dump(obj, fout)
    timestamp0(startout, msg="- writing output: wall time")
    return checksum


def load_filter(filename, *, shared_memory=False, info_only=False):
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp

    if filename.endswith((".", ".info", ".filter")):
        filename = filename.rsplit(".", 1)[0]

    if not info_only:
        startload = timestamp0(msg="\n## Loading filter")
        debugprint0(f"- filter files '{filename}.info', '{filename}.filter'...")
    with open(f"{filename}.info", "rb") as finfo:
        infotup = pickle.load(finfo)
    if info_only:
        return None, infotup
    (filterinfo, optinfo, appinfo) = infotup
    filtertype = filterinfo['filtertype']
    debugprint1(f"- Building filter of type '{filtertype}'...")
    m = import_module(f"..filter_{filtertype}", __package__)

    shm = None
    if shared_memory:
        print('SharedMemory')
        filename = basename(filename)
        shm = SharedMemory(name=filename, create=False)
        resource_tracker.unregister(shm._name, "shared_memory")
        shm_buf = shm.buf
        assert shm_buf.shape[0] % 8 == 0
        assert shm_buf.itemsize == 1
        init = np.ndarray(shm_buf.shape[0] // 8, dtype=np.uint64, buffer=shm_buf)
        fltr = m.build_from_info(filterinfo, init=init, shm=shm)
    else:
        fltr = m.build_from_info(filterinfo)
    if not shared_memory:
        checksum = filterinfo['checksum']
        checked = load_array_into(f"{filename}.filter", fltr.array, check=checksum)
        if checked:
            debugprint2(f"- Checksum {checksum} successfully verified. Nice.")
    else:
        check = fltr.array[:256].sum()
        if check != filterinfo['checksum']:
            raise RuntimeError(f"ERROR loading '{filename}.filter' into shared memory: {filterinfo['checksum']} does not match expected {check}")
        debugprint2(f"- checksum {check} successfully verified. Nice.")
    timestamp0(startload, msg="- Time to load")
    return fltr, (filterinfo, optinfo, appinfo)
