import os
from os import stat as osstat
from os.path import basename
from signal import sigwait, SIGTERM, SIGINT
import pickle
from multiprocessing import resource_tracker
from multiprocessing.shared_memory import SharedMemory

import numpy as np

from .cleanifier_remove import remove_shared_memory
from ..lowlevel import debug


def create_shared_memory(fpath, fname, extension=".hash"):
    fpath = fpath + extension
    fsize = osstat(fpath).st_size
    assert fsize % 8 == 0

    with open(fpath, "rb") as hasharray:
        try:
            shm = SharedMemory(name=fname, create=True, size=fsize)
        except FileExistsError:
            return False
        shm_array = np.ndarray(fsize, dtype=np.uint8, buffer=shm.buf)
        hasharray.readinto(shm_array.view(np.uint8))

    resource_tracker.unregister(shm._name, "shared_memory")
    return True


def main(args):
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp

    osname = os.name.lower()
    fpath = args.name
    if fpath.endswith('.'):
        fpath = fpath[:-1]
    fname = basename(fpath)

    with open(f"{fpath}.info", "rb") as finfo:
        infotup = pickle.load(finfo)
    if 'filtertype' in infotup[0]:
        extension = '.filter'
    else:
        extension = '.hash'

    if osname != 'posix':
        msg = f"OS name '{osname}' not supported yet."
        debugprint0(msg)
        debugprint0(f"Shared object {fname} is not loaded.")
        exit(1)
    debugprint0(f"Creating shared memory object {fname}")
    created = create_shared_memory(fpath, fname, extension=extension)
    if created:
        if args.keep_running:
            debugprint0(f"Shared memory with {fname} was created.")
        else:
            debugprint0(f"Shared memory with {fname} was created. Please use cleanifier remove to delete it!")
    else:
        print(f"Index {fname} is already loaded as shared memory.")
        exit(0)
    if args.keep_running:
        sigwait((SIGTERM, SIGINT, ))
        removed = remove_shared_memory(fname)
        if removed:
            debugprint0(f"Shared memory for {fpath} was removed.")
        else:
            debugprint0(f"Could not remove shared memory for {fpath}. Please use the remove command.")


if __name__ == '__main__':
    main()
