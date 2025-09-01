import sys
from os.path import splitext
from shlex import split as cmdsplit
from subprocess import Popen, PIPE
from shutil import which
from contextlib import nullcontext
from collections import defaultdict


from ..lowlevel import debug
from .fastqio import \
    cptask_read_fastq_into_linemarked_buffers, \
    cptask_read_pairedfastq_into_linemarked_buffers, \
    cptask_read_fastq_seqid_pos_into_buffers
from .fastaio import \
    cptask_read_fasta_into_buffers, \
    cptask_read_fasta_chrom_pos_into_buffers
from .binaryio import \
    compile_cptask_read_data_into_buffers


_in_suffixes = {
    ".gz": "bgzip -cd",
    ".bz2": "bzip2 -cd",
    ".xz": "xz -cd"
    }
_out_suffixes = {
    ".gz": "bgzip",
    ".bz2": "bzip2",
    ".xz": "xz"
    }
_out_threads = {
    "bgzip": "@",
    "xz": "T"
    }
_out_compression = defaultdict(str)
_out_compression['bgzip'] = 'l'

_extensions = dict(
    fasta=[".fasta", ".fa", ".fna"],
    fastq=[".fastq", ".fq"],
    vcf=[".vcf"],
    numpy=[".np", ".npy"],
    data=[".data"],
    gff=[".gff3"]
    )
_filetypes = {ex: typ for typ, L in _extensions.items() for ex in L}


class InputFileHandler:
    def __init__(self, filename, bufsize=2**16):
        """
        Context manager class representing an input file or stream.

        Attributes:
        self.filename: the input filename, as given
        self.file_type: the file type (fasta, fastq)
        self.cmd: list of strings, passed to Popen as command
        self.process: Process returned by Popen (for compressed files) or None
        self.file: file handle returned by open (for uncompressed files) or None
        self.fd: the low-level file descriptor (int) of .process or of .file
        """
        debugprint0, debugprint1, debugprint2 = debug.debugprint

        # check if file is compressed
        fname, file_extension = splitext(filename)
        tool = _in_suffixes.get(file_extension, None)
        is_compressed = (tool is not None)

        # check file extension to determine file type
        if is_compressed:
            file_extension = splitext(fname)[1]
        file_type = _filetypes.get(file_extension, None)
        if file_type is None:
            debugprint0(f"Error: InputFileHandler: Unknown file type for '{filename}'")
            sys.exit(1)

        if is_compressed:
            if which(tool.split()[0]) is None:
                raise RuntimeError(f"Cannot decompress input file {filename} because {tool} is not installed.")
            debugprint2(f"- creating Popen command for {filename} of type {file_type} using '{tool} {filename}'")
            self.cmd = cmdsplit(f"{tool} {filename}")
        else:
            debugprint2(f"- using direct open for {filename} of type {file_type}")
            self.cmd = None
        self.filename = filename
        self.file_type = file_type
        self.bufsize = bufsize

    def __enter__(self):
        if self.cmd is not None:
            self.process = Popen(self.cmd, stdout=PIPE, bufsize=self.bufsize)
            self.fd = self.process.stdout.fileno()
            self.file = self.process.stdout
        else:
            self.file = open(self.filename, "rb", buffering=self.bufsize)
            self.fd = self.file.fileno()
            self.process = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process is not None:
            self.process.stdout.close()
            self.process.wait()
        else:
            self.file.close()
        self.fd = None


class OutputFileHandler:
    def __init__(self, filename, bufsize=2**16, compression_level=1, compression_threads=1):
        """
        Create a context manager to open an output file.
        Attributes:
        self.filename: the output filename, as given
        self.file_type: the file type (fasta, fastq)
        self.cmd: list of strings, passed to Popen as command
        self.process: Process returned by Popen (for compressed files) or None
        self.file: file handle returned by open (for uncompressed files) or None
        self.fd: the low-level file descriptor (int) of .process or of .file
        """
        debugprint0, debugprint1, debugprint2 = debug.debugprint

        # check if file is compressed
        fname, file_extension = splitext(filename)
        tool = _out_suffixes.get(file_extension, None)
        is_compressed = (tool is not None)

        # check file extension to determine file type
        if is_compressed:
            file_extension = splitext(fname)[1]
        file_type = _filetypes.get(file_extension, None)
        if file_type is None:
            debugprint0(f"Error: OutputFileHandler: Unknown file type for '{filename}'")
            sys.exit(1)

        if is_compressed:
            if which(tool) is None:
                raise RuntimeError(f"Cannot compress output file {filename}. {tool} is not installed")
            _threads = f' -{_out_threads[tool]} {compression_threads}' if tool in _out_threads else ''
            tool += f' {_threads} -{_out_compression[tool]}{compression_level}'
            debugprint2(f"- creating Popen command for {filename} of type {file_type} using '{tool} {filename}'")
            self.cmd = cmdsplit(f"{tool}")
        else:
            debugprint2(f"- using direct open for {filename} of type {file_type}")
            self.cmd = None
        self.filename = filename
        self.file_type = file_type
        self.bufsize = bufsize

    def __enter__(self):
        if self.cmd is not None:
            with open(self.filename, "wb", self.bufsize) as outfile:
                self.process = Popen(self.cmd, stdin=PIPE, stdout=outfile, bufsize=self.bufsize)
                self.fd = self.process.stdin.fileno()
                self.file = self.process.stdin
        else:
            self.file = open(self.filename, "wb", self.bufsize)
            self.fd = self.file.fileno()
            self.process = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process is not None:
            self.process.stdin.close()
            self.process.wait()
        else:
            self.file.close()
        self.fd = None


def cptask_read_file(fname, valid_types, w, *allbuffers):
    """
    ConsumerProducer task that consumes a file and writes sequences into buffers.
    If the file is compressed using any of {gzip/pigz, bzip, xz},
    it is de-crompressed using the appropriate external tool in a separate process,
    via Popen().
    The resulting plain text file must be of type FASTQ or FASTA.
    It is read into buffers using the appropriate interpreter.
    """
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    paired = False
    if isinstance(fname, tuple):
        paired = True
        fname, fname2 = fname

    with InputFileHandler(fname) as infile, \
         InputFileHandler(fname2) if paired else nullcontext() as infile2:
        ft = infile.file_type
        if (valid_types is not None) and (ft not in valid_types):
            debugprint0(f"Error: file type '{ft}' not among {valid_types=} for file '{fname}'.")
            result = -1

        if ft == "fastq":
            if paired:
                assert infile.file_type == infile2.file_type == "fastq"
                result = cptask_read_pairedfastq_into_linemarked_buffers((infile.fd, infile2.fd), *allbuffers)
                fname = (fname, fname2)
            else:
                result = cptask_read_fastq_into_linemarked_buffers(infile.fd, *allbuffers)
        elif ft == "fasta":
            result = cptask_read_fasta_into_buffers(infile.fd, w, *allbuffers)
        elif ft == "data":
            cptask_read_data_into_buffers = compile_cptask_read_data_into_buffers(64)
            result = cptask_read_data_into_buffers(infile.fd, *allbuffers)
        else:
            debugprint0(f"Error: Interpreter for '{fname}' of type '{ft}' not implemented.")
            result = -1
        return fname, *result


def cptask_read_file_positional(fname, valid_types, w, CHR_mapping, *allbuffers):
    """
    ConsumerProducer task that consumes a file and writes sequences and the current chrom + position into buffers.
    If the file is compressed using any of {gzip/pigz, bzip, xz},
    it is de-crompressed using the appropriate external tool in a separate process,
    via Popen().
    The resulting plain text file must be of type FASTA.
    It is read into buffers using the appropriate interpreter.
    """
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    with InputFileHandler(fname) as infile:
        ft = infile.file_type
        if (valid_types is not None) and (ft not in valid_types):
            debugprint0(f"Error: file type '{ft}' not among {valid_types=} for file '{fname}'.")
            result = -1
        elif ft == "fasta":
            result = cptask_read_fasta_chrom_pos_into_buffers(infile.fd, w, CHR_mapping, *allbuffers)
        elif ft == 'fastq':
            result = cptask_read_fastq_seqid_pos_into_buffers(infile.fd, *allbuffers)
        else:
            debugprint0(f"Error: Interpreter for '{fname}' of type '{ft}' not implemented.")
            result = -1
        return fname, *result


def cptask_read_filepair(filepair, *allbuffers):
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    result = 0
    if (not isinstance(filepair, (tuple, list))) or (len(filepair) != 2):
        debugprint0(f"Error: {filepair=} is not a pair")
        return filepair, (-1)
    if1, if2 = InputFileHandler(filepair[0]), InputFileHandler(filepair[1])
    ft1, ft2 = if1.file_type, if2.file_type
    for (fname, ft) in zip(filepair, (ft1, ft2)):
        if ft != "fastq":
            debugprint0(f"Error: Paired interpreter for '{fname}' of type '{ft}' not implemented.")
            return filepair, (-1)
    with if1, if2:
        result = cptask_read_pairedfastq_into_linemarked_buffers(if1.fd, if2.fd, *allbuffers)
    return filepair, result
