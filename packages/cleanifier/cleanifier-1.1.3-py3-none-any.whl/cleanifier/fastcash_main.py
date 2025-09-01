"""
fastcash_main.py
"""

import argparse
from argparse import ArgumentParser
from importlib import import_module  # dynamically import subcommand
from importlib.metadata import metadata
from os.path import split as splitpath, splitext

from .lowlevel.debug import set_debugfunctions


def get_name_version_description(package: str, filename: str):
    # always call with (__package__, __file__)
    _, fname = splitpath(filename)
    fname, _ = splitext(fname)
    PKGNAME: str = package.split(".")[0]
    NAME: str = fname.replace("_main", "")
    md = metadata(PKGNAME)
    VERSION: str = str(md.json['version'])
    DESCRIPTION: str = f"{NAME} [{PKGNAME} {VERSION}]: " + str(md.json['summary'])
    return NAME, VERSION, DESCRIPTION


def add_hash_table_arguments(p: ArgumentParser):
    p.add_argument("--bucketsize", "-p", type=int, default="6",
        help="bucket size, i.e. number of elements on a bucket")
    p.add_argument("--fill", type=float, default="0.9",
        help="desired fill rate of the hash table")
    p.add_argument("--subtables", type=int, default=5, 
        help="number of subtables used; subtables+1 threads are used")


def add_hash_arguments(p: ArgumentParser):
    shp_group = p.add_mutually_exclusive_group(required=False)
    shp_group.add_argument('-k', '--kmersize', dest="mask", metavar="INT",
        type=int, default=27, help="k-mer size")
    shp_group.add_argument('--mask', metavar="MASK",
        help="gapped k-mer mask (quoted string like '#__##_##__#')")
    p.set_defaults(k="k")
    p.add_argument("-m", "--minimizersize", metavar="INT", type=int, default=0,
        help=argparse.SUPPRESS)  # help="minimizer size of the super-k-mer")
    p.add_argument("--rcmode", metavar="MODE", default="max",
        choices=("f", "r", "both", "min", "max"),
        help="mode specifying how to encode k-mers")
    p.add_argument("--shortcutbits", "-S", metavar="INT", type=int, choices=(0, 1, 2),
        help="number of shortcut bits (0,1,2), default: 0", default=0)
    # single parameter options for parameters
    p.add_argument("-n", "--nobjects", metavar="INT", type=int,
        help="number of objects to be stored")
    p.add_argument("--type", default="default",  # default="3c_fbcbvb",
        help="hash type (e.g. [s]3c_fbcbvb, 2v_fbcbvb), implemented in hash_{TYPE}.py")
    p.add_argument("--unaligned", action="store_const", 
        const=False, dest="aligned", default=None,
        help="use unaligned buckets (smaller, slightly slower; default)")
    p.add_argument("--aligned", action="store_const",
        const=True, dest="aligned", default=None,
        help="use power-of-two aligned buckets (faster, but larger)")
    p.add_argument("--hashfunctions", "--functions", 
        help="hash functions: 'default', 'random', or func1:func2[:func3]")
    # less important hash options
    p.add_argument("--nostatistics", "--nostats", action="store_true",
        help="do not compute or show index statistics at the end")
    p.add_argument("--maxwalk", metavar="INT", type=int, default=500,
        help="maximum length of random walk through hash table before failing [500]")
    p.add_argument("--maxfailures", metavar="INT", type=int, default=0, 
        help="continue even after this many failures [default:0; forever:-1]")
    p.add_argument("--walkseed", type=int, default=7,
        help="seed for random walks while inserting elements [7]")
    add_hash_table_arguments(p)


def info(p: ArgumentParser):
    p.add_argument("hashname", metavar="INPUTPREFIX",
        help="file name of existing hash table (without extension .hash or .info)")
    p.add_argument("--outprefix", "--export", "-o", "-e",
        metavar="OUTPREFIX",
        help="file name prefix of exported data, extended by .{key,chc.val}.{txt,data}.")
    p.add_argument("--format", choices=("native", "packed", "text", "txt", "dna"),
        help="output format [native (default): use native integer arrays (uint{8,16,32,64}); "
            "packed: use bit-backed arrays; "
            "text: use text files (one integer per line); "
            "dna: text file with DNA k-mers (one k-mer per line)]")
    p.add_argument("--filterexpression", "-f", metavar="EXPRESSION",
        help="filter expression using variables `key`, `choice`, `value`, "
        "e.g. '(choice != 0) and (value & 3 == 3)'. "
        "Output (but not statistics) will be restricted to items for which the filter expression is true.")
    p.add_argument("--compilefilter", "-c", metavar=("FUNCTIONPATH", "PARAM"), nargs="+",
        help="string specifying `path/module::compiler_func` that will be called with "
        "the valueset, the appinfo and given additional parameters (PARAM) "
        "to compile a filter function that takes key, choice and value as arguments.")
    p.add_argument("--statistics", metavar="LEVEL",
        choices=("none", "summary", "details", "full"),
        default="summary",
        help="level of detail of statistics to be shown (none, summary, details, full)")
    p.add_argument("--showvalues", default='1023', metavar="INT",
        help="number of values to show in value statistics (none, all, INT)")


def lookup(p: ArgumentParser):
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--kmers", "--dna", metavar="DNAINPUT",
        help="DNA text k-mer input file prefix (withot .dna.txt) with k-mers to look up")
    g.add_argument("--data", metavar="DATAINPUT",
        help="data (native) input file prefix (without (.key.data, .val.data, etc.) to look up")
    p.add_argument("--index", metavar="INDEXPREFIX", required=True,
        help="file name of existing hash table (without extension .hash or .info) in which to look up keys")
    p.add_argument("--format", choices=("tsv", "dnatsv"), default='dnatsv',
        help="output format (dnatsv)")


def optimize(p: ArgumentParser):
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--index",
        help="name of the hash table index to be optimized (without extension .hash, .info)")
    g.add_argument("--data",
        help="file name prefix of exported hash table data to be optimized (without extensions)")
    p.add_argument("--optindex", "--outprefix", "-o", required=True,
        help="name of the optimized index .hash and .info files")
    p.add_argument('--newvalueset', nargs='+',
        default=['strongunique'], metavar=("NAME", "PARAMETER"),
        help="value set with arguments, implemented in values.{VALUESET}.py")
    p.add_argument("--bucketsize", "-b", "-p", type=int,
        help="bucket size, i.e. number of elements on a bucket")
    p.add_argument("--fill", type=float,
        help="desired fill rate of the hash table")
    p.add_argument("--subtables", type=int,
        help="desired number of subtables")
    p.add_argument("--hashfunctions", "--functions",
        help="hash functions: 'default', 'random', or func1:func2:func3:func4")
    p.add_argument("-t", "--threads", type=int,
        help="number of threads to optimize. Works only in combinations with subtables.")
    p.add_argument("--check", action="store_true",
        help="Run an ILP for all subtables and check if the result is correct")


def deploy(p: ArgumentParser):
    p.add_argument("toolname", metavar="TOOL",
        help="name of tool to deploy (e.g., xengsort, hackgap, ...)")
    p.add_argument("--to", "--target", required=True, metavar="GIT_DIRECTORY",
        help="target directory where to copy top level files")
    p.add_argument("--execute", "-x", action="store_true",
        help="execute deployment (if not given, only simulate it)")
    p.add_argument("--tobranch", metavar="BRANCH",
        help="override name of branch to deploy to; must be checked out in tool's target directory")
    p.add_argument("--frombranch", metavar="BRANCH",
        help="override name of branch to deploy from; must be checked out in fastcash source directory")
    p.add_argument("--replace", action="store_true",
        help="allow replacing the existing version with the same version")


def mphf(p: ArgumentParser):
    p.add_argument("dataprefix", metavar="FILEPREFIX",
        help="file name prefix (without extensions) of a .key.data file")
    p.add_argument("--type", required=True,
        choices=("bbhash", "srhash", "bb", "sr"),
        help="type of MPHF to compute")
    p.add_argument("--bucketsize", "-b", type=int,
        metavar="INT", default=5,
        help="srhash: maximum bucket size [5]; larger values require less space, but construction takes much longer")
    p.add_argument("--sizefactor", "-s", type=float,
        metavar="FACTOR", default=1.0,
        help="srhash/bbhash: oversize factor for one level [optimal]")
    p.add_argument("--attempts", "-a", type=int,
        metavar="INT", default=10,
        help="srhash/bbhash: number of attempts per chosen hash function")
    p.add_argument("--space", metavar="SPACE",
        choices=("small", "medium", "large"), default="medium",
        help="srhash: amount of temporary memory to use [medium]")


def xorfilter(p: ArgumentParser):
    p.add_argument("--index", required=True,
        help="name of the input hash table; reads .hash and .info")
    p.add_argument("--filter", "--out", required=True,
        help="name of the resulting output XOR filter; writes .hash and .info as output")
    p.add_argument("--fprbits", type=int, default=16, metavar="BITS",
        help="number of fingerprint bits [16]; false positive rate is 2**fprbits")


# main argument parser #############################

def get_argument_parser():
    """
    return an ArgumentParser object
    that describes the command line interface (CLI)
    of this application
    """
    NAME, VERSION, DESCRIPTION = get_name_version_description(
        str(__package__), __file__)
    p: ArgumentParser = ArgumentParser(
        description=DESCRIPTION,
        epilog="by Algorithmic Bioinformatics, Saarland University, 2021-2025."
        )
    p.add_argument("--debug", "-D", action="count", default=0,
        help="output debugging information (repeat for more)")
    p.add_argument("--version", "-v", action="version", version=VERSION,
        help="show version and exit")

    subcommands = [
        (
            "info",
            "get information about a hash table; export its (filtered) data",
            info,
            "fastcash_info", "main",
        ), (
            "export",  # this is a synonym for info. Both commands do both.
            "get information about a hash table; export its (filtered) data",
            info,
            "fastcash_info", "main",
        ), (
            "lookup",
            "look up the values of a few k-mers in the given hash table",
            lookup,
            "fastcash_lookup", "main",
        ), (
            "optimize",
            "optimize the assignment of an existing hash table from exported data",
            optimize,
            "fastcash_optimize", "main",
        ), (
            "deploy",
            "deploy a fastcash-based tool (like xengsort, hackgap, etc.)",
            deploy,
            "fastcash_deploy", "main",
        ), (
            "mphf",
            "compute a minimal perfect hash function on a key set",
            mphf,
            "fastcash_mphf", "main",
        ), (
            "xorfilter",
            "build a XOR filter from a hash table",
            xorfilter,
            "fastcash_build_xor", "main",
        ),
    ]
    # add subcommands to parser
    sps = p.add_subparsers(
        description=f"The {NAME} library tool supports the commands below. "
            f"Run '{NAME} COMMAND --help' for detailed information on each command.",
        metavar="COMMAND")
    sps.required = True
    sps.dest = 'subcommand'
    for (name, helptext, f_parser, module, f_main) in subcommands:
        if name.endswith('!'):
            name = name[:-1]
            chandler = 'resolve'
        else:
            chandler = 'error'
        sp = sps.add_parser(name, help=helptext,
            description=f_parser.__doc__, conflict_handler=chandler)
        sp.set_defaults(func=(module, f_main))
        f_parser(sp)
    return p


def main(args: str | None = None):
    p = get_argument_parser()
    pargs = p.parse_args() if args is None else p.parse_args(args)
    set_debugfunctions(debug=pargs.debug, timestamps=pargs.debug)
    # set_threads(pargs, "threads")  # limit number of threads in numba/prange
    module, f_main = pargs.func
    m = import_module("." + module, __package__)
    mymain = getattr(m, f_main)
    mymain(pargs)


if __name__ == "__main__":
    main()
