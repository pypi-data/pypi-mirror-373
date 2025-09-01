from os.path import basename
from multiprocessing.shared_memory import SharedMemory

from ..lowlevel import debug


def remove_shared_memory(fname):
    try:
        shm = SharedMemory(name=fname, create=False)
    except FileNotFoundError:
        return False
    shm.close()
    shm.unlink()
    return True


def main(args):
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp

    fpath = args.name
    if fpath.endswith('.'):
        fpath = fpath[:-1]
    fname = basename(fpath)
    removed = remove_shared_memory(fname)
    if removed:
        debugprint0(f"Shared memory for {fpath} was removed.")
    else:
        debugprint0(f"Shared memory for {fpath} does not exist")


if __name__ == '__main__':
    main()
