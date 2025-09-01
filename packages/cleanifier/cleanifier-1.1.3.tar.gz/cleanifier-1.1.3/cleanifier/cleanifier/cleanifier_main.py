"""
cleanifier_main.py
cleanifier: filtering human (or other species) out of a data set.
by Jens Zentgraf, Johanna Schmitz & Sven Rahmann, 2019--2025
"""

from importlib import import_module  # dynamically import subcommand
from importlib.metadata import metadata
from os.path import dirname, join as pathjoin

from jsonargparse import ArgumentParser, ActionConfigFile, SUPPRESS
from jsonargparse.typing import restricted_number_type

from ..lowlevel.debug import set_debugfunctions
from ..fastcash_main import info, get_name_version_description


def get_config_path():
    cleanifierfolder = dirname(__file__)
    cfgpath = pathjoin(cleanifierfolder, "config")
    return cfgpath


def filter(p):
    p.add_argument("--fastq", "-q", metavar="FASTQ", required=True, nargs="+",
        help="single or first paired-end FASTQ file to filter")
    p.add_argument("--pairs", "-p", metavar="FASTQ", nargs="+",
        help="second paired-end FASTQ file (only together with --fastq)")
    p.add_argument("--index", required=True,
        help="existing index")
    p.add_argument("--shared", action="store_true",
        help="index should be loaded via shared memory")
    gmode = p.add_mutually_exclusive_group(required=False)
    gmode.add_argument("--count", action="store_true",
        help="only count reads or read pairs for each class, do not output any FASTQ")
    gmode.add_argument("--out", "-o", "--prefix",
        dest="prefix", metavar="PREFIX",
        help="prefix for output files (directory and name prefix)")
    p.add_argument("--keep-host", action="store_true",
        help="output both the filtered FASTQ file and a file with the removed host reads; only together with --out")
    p.add_argument("--threads", "-T", "-j", metavar="INT", type=int, default=2,
        help="maximum number of worker threads for classification")
    p.add_argument("--compression", choices=("none", "gz", "bz2", "xz"),
        help="compression of output files")
    p.add_argument("--compression-threads", type=int, default=1,
        help="maximum number of compression threads")
    p.add_argument("--compression-level", type=int, default=1,
        help="compression level; supported levels depend on compression type (1-11 for gz, 1-9 for bz2 and 0-9 for xz)")
    p.add_argument("--sensitive", action="store_true",
        help="sensitive (slower) mode that queries all k-mers")
    p.add_argument("--threshold", metavar="INT", default=0.5, type=float,
        help="threshold at which reads are filtered")
    p.add_argument("--prefetchlevel", metavar="INT",
        type=restricted_number_type("from_0_to_2", int, [(">=", 0), ("<=", 2)]),
        help="amount of prefetching: none (0), second bucket (1), all buckets (2); supported only for hash table")
    p.add_argument("--buffersize", metavar="INT", default=16,
        type=int, help="io buffersize; in powers of two default 16 (2^16 bytes, fast on SDDs); increase on HDD to e.g. 24")
    p.add_argument("--progress", "-P", action="store_true",
        help="show progress")


def index(p):
    p.add_argument("--index", required=True,
        help="name of the resulting index (.hash and .info output)")
    p.add_argument("--files", "-H", metavar="FASTA/Q", nargs="+",
        help="FASTA/Q file(s) for the genomes that should be removed.")

    p.add_argument("-n", "--nobjects", metavar="INT",
        type=int, required=True,
        help="number of k-mers to be stored in hash table (2_512_390_070 for human T2T and k=31)")

    k_group = p.add_mutually_exclusive_group(required=True)
    k_group.add_argument('--mask', metavar="MASK", type=str,
        help="gapped k-mer mask (quoted string like '#__##_##__#')")
    k_group.add_argument('-k', '--kmersize', dest="mask",
        type=int, metavar="INT", help="k-mer size")

    p.add_argument("--type", default="default",
        # help="hash type (e.g. s3c_fbcbvb), implemented in hash_{TYPE}.py")
        help=SUPPRESS)
    p.add_argument("--bucketsize", "-b", "-p",
        metavar="INT", type=int, required=True,
        help="bucket size, i.e. number of elements in a bucket")
    p.add_argument("--fill",
        type=float, metavar="FLOAT",
        help="desired fill rate (< 1.0) of the hash table")
    p.add_argument("--subtables", type=int, metavar="INT",  # no default -> None!
        help="number of subtables used; subtables+1 threads are used")
    p.add_argument("--threads-read", type=int,  # 2?
        help="Number of reader threads")
    p.add_argument("--threads-split", type=int,  # 4?
        help="Number of splitter threads")

    p.add_argument("--shortcutbits", "-S", metavar="INT",
        type=restricted_number_type("from_0_to_2", int, [(">=", 0), ("<=", 2)]),
        help="number of shortcut bits (0,1,2)")
    p.add_argument("--hashfunctions", "--functions", metavar="SPEC", default="random",
        help="hash functions: 'random', or 'func0:func1:func2:func3'")
    p.add_argument("--aligned", action="store_true",
        help="use power-of-two-bits-aligned buckets (slightly faster, but larger)")
    p.add_argument("--statistics", "--stats",
        choices=("none", "summary", "details", "full"), default="summary",
        help="level of detail for statistics (none, summary, details, full (all subtables))")
    p.add_argument("--maxwalk", metavar="INT", type=int,
        help="maximum length of random walk through hash table before failing")
    p.add_argument("--maxfailures", metavar="INT", type=int,
        help="continue even after this many failures; forever: -1]")
    p.add_argument("--walkseed", type=int, metavar="INT",
        help="seed for random walks while inserting elements")

    # additional arguments for using windowed cuckoo filters
    p.add_argument("--filter", action="store_true",
        help="use cuckoo filter instead of cuckoo hash table")
    p.add_argument("--fpr", type=int, metavar="INT", default=14,
        help="integer k to build a cuckoo filter with an FPR of 1/2^k (only for --filter)")
    p.add_argument("--windowsize", type=int, default=2,
        help="windowsize of cuckoo filter (only for --filter)")


def download(p):
    p.add_argument("--dir", default=None,
        help="directory name to store the index; default current directory")
    p.add_argument("--version", default='probabilistic',
        help="index version (probabilistic or exact); default probabilistic.")
    p.add_argument("--checksum", action="store_true",
        help="check the checksum of the downloaded file, might take some time")


def load(p):
    p.add_argument("--name", required=True,
        help="name (prefix) of the index to load into shared memory")
    p.add_argument("--keep-running", '-k', action='store_true',
        help='programm keeps running until killed bit SIGTERM. If killed, the shared object is removed.')


def remove(p):
    p.add_argument("--name", required=True,
        help="name (prefix) of the index to remove from shared memory")


CFGPATH = get_config_path()
SUBCOMMANDS = [
    ("index",
        "build index of all species' FASTA/Q files",
        index,
        "cleanifier_index", "main",
        [f"{CFGPATH}/index.yaml", 'config/index.yaml', 'index.yaml']),
    ("filter",
        "remove all reads that belong to the specified species",
        filter,
        "cleanifier_filter", "main",
        [f"{CFGPATH}/filter.yaml", 'config/filter.yaml', 'filter.yaml']),
    ("info",
        "get information about a hash table and dump its data",
        info,
        "..fastcash_info", "main", []),
    ("download",
        "Download the human index from Zenodo.",
        download,
        "cleanifier_download", "main", []),
    ("load",
        "Load the index as a shared memory object with the provided name.",
        load,
        "cleanifier_load", "main", []),
    ("remove",
        "Remove the shared memory object with the provided name.",
        remove,
        "cleanifier_remove", "main", []),
]


# main argument parser #############################

def get_argument_parser():
    """
    return an ArgumentParser object
    that describes the command line interface (CLI)
    of this application
    """

    NAME, VERSION, DESCRIPTION = get_name_version_description(__package__, __file__)
    p = ArgumentParser(
        prog="cleanifier",
        description=DESCRIPTION,
        epilog="(c) 2019-2025 by Algorithmic Bioinformatics, Saarland University. MIT License."
    )
    # global options
    p.add_argument("--version", action="version", version=VERSION,
        help="show version and exit")
    p.add_argument("--debug", "-D", action="count", default=0,
        help="output debugging information (repeat for more)")

    # add subcommands to parser
    scs = p.add_subcommands()
    subcommands = SUBCOMMANDS
    for (name, helptext, f_parser, module, f_main, default_configs) in subcommands:
        if name.endswith('!'):
            name = name[:-1]
            chandler = 'resolve'
        else:
            chandler = 'error'
        sp = ArgumentParser(prog=name, description=helptext,
            default_config_files=default_configs)
        if name in ["filter", "index"]:
            sp.add_argument('--cfg', "--config", action=ActionConfigFile)
        sp.add_argument("--func", default=(module, f_main), help=SUPPRESS)
        f_parser(sp)
        scs.add_subcommand(name, sp, help=helptext,
            description=helptext, conflict_handler=chandler)
    return p


def main(args=None):
    p = get_argument_parser()
    pargs = p.parse_args() if args is None else p.parse_args(args)
    set_debugfunctions(debug=pargs.debug, timestamps=pargs.debug)
    sc_pargs = pargs[pargs.subcommand]
    (module, f_main) = sc_pargs.func
    m = import_module("." + module, __package__)
    mymain = getattr(m, f_main)
    mymain(sc_pargs)
