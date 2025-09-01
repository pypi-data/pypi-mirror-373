"""
fastcash_info.py:
Collect and print information on a hash table stored on disk.
Select elements according to a filter functions;
export selected or all elements (keys, values, choices, info).
"""

from os import sep as SLASH
from concurrent.futures import ThreadPoolExecutor, wait
from importlib.util import spec_from_file_location, module_from_spec

from numba import njit

from .lowlevel import debug
from .srhash import print_statistics
from .io.hashio import load_hash, export_hash


def print_dict(d, title=None):
    if title is not None:
        print(f"\n### {title}")
    for key, value in d.items():
        print(f"- {key}: {value}")


def print_values(values, valuetup, title=None):
    if title is not None:
        print(f"\n### {title}")
    print(f"- value set specification: {valuetup}")
    print(f"- value set name: {values.NAME}")
    print(f"- value set nvalues: {values.NVALUES}")


def compile_filter_function(
        expr=None, compile=None,
        valueset=None, appinfo=None):
    # any filter given?
    if expr is None and compile is None:
        f = (lambda key, choice, value: True)
        ff = njit(nogil=True)(f)
        return ff, False
    # filter by expression in key, choice, value
    elif expr is not None:
        # expr must be an expression using 'key', 'choice', 'value' and constants.
        f = eval(f'lambda key, choice, value: ({expr})')
        ff = njit(nogil=True)(f)
        return ff, True
    # filter by compiling a function, given by name='modulepath::funcname'.
    # compile must be a list: [name, *params] (all strings).
    # name must be of the form "module.function"
    # This function receives the valueset and appinfo as constants,
    # and must return a compiled function f(key, choice, value).
    name, params = compile[0], compile[1:]
    module_path, func = map(str.strip, name.split("::"))
    *_, module_name = module_path.split(SLASH)
    module_path += ".py"
    _spec = spec_from_file_location(module_name, module_path)
    module = module_from_spec(_spec)
    _spec.loader.exec_module(module)
    cf = getattr(module, func)
    ff = cf(valueset=valueset, appinfo=appinfo, params=params)
    return ff, True


def compile_count_filtered(h, filterfunc):
    hp = h.private
    is_slot_empty_at = hp.is_slot_empty_at
    get_item_at = hp.get_item_at
    get_subkey_choice_from_bucket_signature = hp.get_subkey_choice_from_bucket_signature
    get_key_from_subtable_subkey = hp.get_key_from_subtable_subkey
    nbuckets, bucketsize = h.nbuckets, h.bucketsize

    @njit(nogil=True)
    def count_filtered(ht, st):
        n = total = 0
        for bucket in range(nbuckets):
            for slot in range(bucketsize):
                if is_slot_empty_at(ht, st, bucket, slot):
                    break  # go to next bucket
                sig, val = get_item_at(ht, st, bucket, slot)
                sbk, chc = get_subkey_choice_from_bucket_signature(bucket, sig)
                key = get_key_from_subtable_subkey(st, sbk)
                n += filterfunc(key, chc, val)
                total += 1
        return n, total

    return count_filtered


def run_filter(h, filterfunc):
    count_filtered = compile_count_filtered(h, filterfunc)
    nsubtables = h.nsubtables if hasattr(h, "nsubtables") else h.subtables
    with ThreadPoolExecutor(max_workers=nsubtables) as executor:
        futures = [
            executor.submit(count_filtered, h.hashtable, st)
            for st in range(nsubtables)
        ]
    wait(futures)
    filtered = total = 0
    for st, f in enumerate(futures):
        sgood, stotal = f.result()  # this may raise errors
        filtered += sgood
        total += stotal
    return filtered, total


def main(args):
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp
    starttime = timestamp0(msg="\n# fastcash info/export : information and export of fastcash hash tables")

    # load hash table information
    _, values, infotup = load_hash(args.hashname, info_only=True)
    (hashinfo, valueinfo, optinfo, appinfo) = infotup
    print_dict(hashinfo, "Hash table properties")
    print_dict(optinfo)
    print_dict(appinfo)
    print_values(values, valueinfo, "Value set properties")

    # count number of k-mers passing the filter
    filterfunc, runfilter = compile_filter_function(
        expr=args.filterexpression,
        compile=args.compilefilter,
        valueset=values, appinfo=appinfo)

    # load the hash table and print statistics
    h, values, infotup = load_hash(args.hashname)
    nvalues = values.NVALUES
    SV = {'all': nvalues, 'none': False}
    sv = args.showvalues
    sv = SV[sv] if sv in SV else int(sv)
    print_statistics(h, level=args.statistics, show_values=sv)

    # run a compiled filter
    if runfilter:
        filtered, total = run_filter(h, filterfunc)
        percent = filtered / total if total > 0 else 0.0
        debugprint0(f"\n- k-mers passing filter: {filtered} of {total}, or {percent:.2%}")

    # export data
    fmt = args.format  # native, packed, text/txt, dna
    anyformat = (fmt is not None)
    prefix = args.outprefix
    if (prefix is None) and anyformat:
        prefix = args.hashname
    if prefix is not None:
        startout = timestamp0(msg="\n## Data Output")
        fmt = {None: 'native', 'txt': 'text'}.get(fmt, fmt)
        written = export_hash(h, nvalues, infotup, prefix, fmt, filterfunc)
        debugprint0(f"- wrote {written} items")
        timestamp0(startout, msg="- done writing data; writing time")

    # that's it; successfully exit the program
    timestamp0(starttime, msg="- DONE; total time")
