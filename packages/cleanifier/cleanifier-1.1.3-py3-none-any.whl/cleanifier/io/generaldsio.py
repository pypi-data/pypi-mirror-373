"""
generaldsio.py:
IO for hash table or filter
"""

import pickle  # for binary files
from importlib import import_module


def load_data_structure(filename, *, shared_memory=False, info_only=False):
    if filename.endswith((".", ".info", ".filter")):
        filename = filename.rsplit(".", 1)[0]

    with open(f"{filename}.info", "rb") as finfo:
        infotup = pickle.load(finfo)

    if info_only:
        return None, infotup

    if 'filtertype' in infotup[0]:
        iomodule = import_module(".filterio", __package__)
        load = iomodule.load_filter
        ds, infotup = load(filename, shared_memory=shared_memory, info_only=info_only)
        values = None
    elif 'hashtype' in infotup[0]:
        iomodule = import_module(".hashio", __package__)
        load = iomodule.load_hash
        ds, values, infotup = load(filename, shared_memory=shared_memory, info_only=info_only)
    else:
        raise NotImplementedError("Inconsistent infotup for hash table \
            [(hashinfo, valueinfo, optinfo, appinfo); use_filter=False] and \
            filter [(filterinfo, optinfo, appinfo); use_filter=True]")
    return ds, values, infotup


def save_data_structure(outname, ds, optinfo=dict(), appinfo=dict(), *, valueinfo=dict()):
    if getattr(ds, 'filtertype', 0):
        iomodule = import_module(".filterio", __package__)
        save = iomodule.save_filter
        return save(outname, ds, optinfo=optinfo, appinfo=appinfo)
    elif getattr(ds, 'hashtype', 0):
        iomodule = import_module(".hashio", __package__)
        save = iomodule.save_hash
        return save(outname, ds, valueinfo, optinfo=optinfo, appinfo=appinfo)
    raise NotImplementedError("Data structure should either be a hash table \
        (has hashtype attr.) or probabilistic filter (has filtertype attr.)")
