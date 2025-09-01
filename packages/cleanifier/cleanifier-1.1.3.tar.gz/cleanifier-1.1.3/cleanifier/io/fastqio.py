import io
from argparse import ArgumentParser

import numpy as np
from numba import njit, int32, int64

from .seqio import FormatError, _universal_reads
from ..lowlevel.libc import read_block
from ..lowlevel.conpro import \
    find_buffer_for_writing,\
    mark_buffer_for_reading, mark_buffer_for_writing


# Python FASTQ/gz handling ######################################

def fastq_reads(files, sequences_only=False, dirty=False):
    """
    For the given 'files':
    - list or tuple of FASTQ paths,
    - single FASTQ path (string; "-" for stdin)
    - open binary FASTQ file-like object f,
    yield a triple of bytes (header, sequence, qualities) for each read.
    If sequences_only=True, yield only the sequence of each read.

    This function operatates at the bytes (not string) level.
    The header contains the initial b'@' character.

    Automatic gzip decompression is provided
    if a file is a string and ends with .gz or .gzip.
    """
    func = _fastq_reads_from_filelike
    if sequences_only:
        func = _fastq_seqs_from_filelike
        if dirty:
            func = _fastq_seqs_dirty_from_filelike
    if type(files) == list or type(files) == tuple:
        # multiple files
        for f in files:
            yield from _universal_reads(f, func)
    else:
        # single file
        yield from _universal_reads(files, func)


def _fastq_reads_from_filelike(f, HEADER=b'@'[0], PLUS=b'+'[0]):
    strip = bytes.strip
    entry = 0
    try:
        while f:
            header = strip(next(f))
            if not header:
                continue
            entry += 1
            seq = strip(next(f))
            plus = strip(next(f))
            qual = strip(next(f))
            if header[0] != HEADER:
                raise FormatError(f"ERROR: Illegal FASTQ header: '{header.decode()}', entry {entry}")
            if plus[0] != PLUS:
                raise FormatError(f"ERROR: Illegal FASTQ plus line: '{plus.decode()}',\nheader '{header.decode()}',\nsequence '{seq.decode()}',\nentry {entry}")
            if len(plus) > 1 and plus[1:] != header[1:]:
                raise FormatError(f"ERROR: FASTQ Header/plus mismatch: '{header.decode()}' vs. '{plus.decode()}', entry {entry}")
            yield (header[1:], seq, qual)
    except StopIteration:
        pass


def _fastq_seqs_from_filelike(f, HEADER=b'@'[0], PLUS=b'+'[0]):
    strip = bytes.strip
    try:
        while f:
            header = strip(next(f))
            if not header:
                continue
            seq = strip(next(f))
            plus = next(f)
            next(f)  # ignore quality value
            if header[0] != HEADER:
                raise FormatError(f"ERROR: Illegal FASTQ header: '{header.decode()}'")
            if plus[0] != PLUS:
                raise FormatError(f"ERROR: Illegal FASTQ plus line: {plus.decode()}'")
            yield seq
    except StopIteration:
        pass


def _fastq_seqs_dirty_from_filelike(f):
    strip = bytes.strip
    while f:
        next(f)
        seq = strip(next(f))
        next(f)
        next(f)  # ignore quality value
        yield seq


# ConsumerProducer methods ############################################

@njit(nogil=True, locals=dict(
    ntodo=int32, errorcode=int32, offset=int32, skip=int32,
    wait=int64, wait_read=int64, wait_write=int64))
def cptask_read_fastq_into_linemarked_buffers(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
    """
    Has to be run as a thread within a consumer producer task.
    Keep reading bytes into one of the outbuffers (cycling),
    and compute linemarks in one of the outinfos (same index, cycling),
    until EOF is reached or an error occurs.
    Return 0 (EOF), or an error code (negative), corresponding to -os.errno.
    """
    # print("- running: cptask_read_fastq_into_linemarked_buffers; fd =", fd, "; output shapes: ", outbuffers.shape, outcontrol.shape, outinfos.shape)
    # assert (inbuffers is None) and (incontrol is None) and (ininfos is None)
    # if outbuffers.shape[0] < 2:
    #     raise ValueError("cptask_read_fastq_into_linemarked_buffers: must have 2 or more output buffers per worker")
    M, N = outinfos.shape
    assert N % 4 == 0
    linemarkbuffers = outinfos.reshape(M, N // 4, 4)

    offset = ntodo = wait_read = wait_write = 0
    nactive = -1
    active_buffer = outbuffers[0]  # irrelevant
    while True:
        old = nactive
        old_buffer = active_buffer
        nactive, wait = find_buffer_for_writing(outcontrol, old)
        wait_write += wait
        active_buffer = outbuffers[nactive]
        if old >= 0:
            if offset > 0:
                active_buffer[0:offset] = old_buffer[(ntodo - offset):ntodo]
            mark_buffer_for_reading(outcontrol, old)
        errorcode = outcontrol[nactive, 1]
        if errorcode != 0:
            # print("- FAILED: cptask_read_fastq_into_linemarked_buffers; fd =", fd, "; output shapes: ", outbuffers.shape, outcontrol.shape, outinfos.shape)
            errorcode = -errorcode
            break
        ntodo = read_block(int32(fd), active_buffer, offset)
        if ntodo <= 0:
            if ntodo < 0 or offset == 0:
                errorcode = ntodo
                break
            ntodo = offset
        nseqs, nxt = _find_fastq_seqmarks(active_buffer[:ntodo], linemarkbuffers[nactive])
        outcontrol[nactive, 7] = nseqs
        outcontrol[nactive, 6] = 0  # buffer type sequence data
        offset = ntodo - nxt
    mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer
    return (wait_read, wait_write, errorcode)


@njit(nogil=True, locals=dict(
    ntodo1=int32, ntodo2=int32, errorcode=int32, offset1=int32, offset2=int32,
    skip=int32, nxt1=int32, nxt2=int32, nseqs=int32, nseqs1=int32, nseqs2=int32,
    wait=int64, wait_read=int64, wait_write=int64, buffersize=int64))
def cptask_read_pairedfastq_into_linemarked_buffers(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
    """
    Has to be run as a thread within a consumer producer task.
    Keep reading bytes into one of the outbuffers (cycling),
    and compute linemarks in one of the outinfos (same index, cycling),
    until EOF is reached or an error occurs.
    Return 0 (EOF), or an error code (negative), corresponding to -os.errno.
    """
    fd1, fd2 = fd
    M, N = outinfos.shape
    assert N % 4 == 0
    linemarkbuffers = outinfos.reshape(M, N // 4, 4)

    offset1 = offset2 = ntodo1 = ntodo2 = wait_read = wait_write = 0
    nactive = -1
    active_buffer = outbuffers[0]  # irrelevant
    buffersize = active_buffer.shape[0] // 2
    active_buffer1 = active_buffer[:len(active_buffer) // 2]
    active_buffer2 = active_buffer[len(active_buffer) // 2:]
    c = 0
    while True:
        old = nactive
        old_buffer1 = active_buffer1
        old_buffer2 = active_buffer2
        nactive, wait = find_buffer_for_writing(outcontrol, old)
        if nactive < 0:
            break
        wait_write += wait
        active_buffer = outbuffers[nactive]
        active_buffer1 = active_buffer[:buffersize]
        active_buffer2 = active_buffer[buffersize:buffersize * 2]
        linemarks = linemarkbuffers[nactive]
        linemarks1 = linemarks[:len(linemarks) // 2, :]
        linemarks2 = linemarks[len(linemarks) // 2: (len(linemarks) // 2) * 2, :]
        if old >= 0:
            assert nactive != old
            if offset1 > 0:
                for i in range(offset1):
                    active_buffer1[i] = old_buffer1[ntodo1 - offset1 + i]
            if offset2 > 0:
                for i in range(offset2):
                    active_buffer2[i] = old_buffer2[ntodo2 - offset2 + i]
            mark_buffer_for_reading(outcontrol, old)
        errorcode = outcontrol[nactive, 1]
        if errorcode != 0:
            errorcode = -errorcode
            break

        # only read if the buffer is filled less than 80%
        if offset1 < active_buffer1.size * 4 // 5:
            inner_offset1 = offset1
            while inner_offset1 < active_buffer1.size * 4 // 5:
                ntodo1 = read_block(int32(fd1), active_buffer1, inner_offset1)
                if ntodo1 == 0:
                    ntodo1 = inner_offset1
                    break
                inner_offset1 = ntodo1
        else:
            ntodo1 = offset1

        if offset2 < active_buffer2.size * 4 // 5:
            inner_offset2 = offset2
            while inner_offset2 < active_buffer2.size * 4 // 5:
                ntodo2 = read_block(int32(fd2), active_buffer2, inner_offset2)
                if ntodo2 == 0:
                    ntodo2 = inner_offset2
                    break
                inner_offset2 = ntodo2
        else:
            ntodo2 = offset2

        if ntodo1 <= 0 or ntodo2 <= 0:
            # Error reading first file
            if ntodo1 < 0:
                errorcode = ntodo1
                break
            # Error reading second file
            if ntodo2 < 0:
                errorcode = ntodo2
                break
            # ntodo1=ntodo2=0 nothing read and no offset left; we are done
            if ntodo1 == ntodo2 == offset1 == offset2 == 0:
                errorcode = ntodo1
                break
            if ntodo1 == 0:
                ntodo1 = offset1
            elif ntodo2 == 0:
                ntodo2 = offset2
            else:
                assert False

        nseqs1, nxt1 = _find_fastq_seqmarks(active_buffer1[:ntodo1], linemarks1)
        nseqs2, nxt2 = _find_fastq_seqmarks(active_buffer2[:ntodo2], linemarks2)

        # sync the linemarks of the the two buffers
        nseqs = min(nseqs1, nseqs2)
        nxt1 = linemarks1[nseqs - 1, 3]
        nxt2 = linemarks2[nseqs - 1, 3]
        outcontrol[nactive, 7] = nseqs
        outcontrol[nactive, 6] = 0  # buffer type sequence data
        offset1 = ntodo1 - nxt1
        offset2 = ntodo2 - nxt2
    mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer
    return (wait_read, wait_write, errorcode)


@njit(nogil=True, locals=dict(
    ntodo=int32, errorcode=int32, offset=int32, wait=int64,
    wait_write=int64, sequence_id=int64, nseq=int64))
def cptask_read_fastq_seqid_pos_into_buffers(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
    """
    Has to be run as a thread within a consumer producer task.
    Keep reading bytes into one of the outbuffers (cycling),
    and compute linemarks in one of the outinfos (same index, cycling),
    until a new header is reached or EOF or an error occurs.
    Return 0 (EOF), or an error code (negative), corresponding to -os.errno.

    This provides for each sequence in a fastq file a sequence id and a position.
    At the moment only reads which fit into a buffer are supported.
    This means the position is always 0.
    """
    # We need an additional slot for the offset and position

    M, N = outinfos.shape
    errorcode = 0
    assert N % 6 == 0
    linemarkbuffers = outinfos.reshape(M, N // 6, 6)
    offset = ntodo = wait_write = 0
    nactive = -1
    active_buffer = outbuffers[0]  # irrelevant
    sequence_id = 0
    while True:
        old = nactive
        old_buffer = active_buffer
        nactive, wait = find_buffer_for_writing(outcontrol, old)
        wait_write += wait
        active_buffer = outbuffers[nactive]
        if old >= 0:
            if offset > 0:
                active_buffer[0:offset] = old_buffer[(ntodo - offset):ntodo]
            mark_buffer_for_reading(outcontrol, old)
        ntodo = read_block(int32(fd), active_buffer, offset)  # ntodo is the number of read bytes
        if ntodo <= 0:
            # Error while reading a new block
            if ntodo < 0 or offset == 0:
                errorcode = ntodo
                break
            # Nothing read but we still have some data in the buffer
            ntodo = offset

        nseqs, nxt = _find_fastq_seqmarks(active_buffer[:ntodo], linemarkbuffers[nactive], sequence_id)
        sequence_id += nseqs
        outcontrol[nactive, 7] = nseqs
        outcontrol[nactive, 6] = 0  # buffer type sequence data
        offset = ntodo - nxt

    mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer

    # 0 because the tasks never waits for a buffer to read
    return (0, wait_write, errorcode)


# numba FASTQ handling ######################################

@njit(nogil=True)
def _find_fastq_seqmarks(buf, linemarks, sequence_id=-1):
    """
    Find start and end positions of lines in byte buffer 'buf'.
    Store the information in 'linemarks', such that
    linemarks[i, 0:4] has information about record number i.
    If we need to store the sequence id and the position in the read, linemarks has 4 entries.

    Return pair (m, nxt), where:
        m: number of sequences processed
        nxt: position at which to continue processing 
             in the next iteration (start of new entry, '@')
    linemarks[i, 0] = start of sequence line
    linemarks[i, 1] = end of sequence line
    linemarks[i, 2] = start of record (all lines)
    linemarks[i, 3] = end of record (all lines)
    ---------------------------------------------
    linemarks[i, 4] = sequence id
    linemarks[i, 5] = position in the sequence (currently always 0 since we expect that a sequence fits in a buffer)
    """
    n = buf.size
    if n == 0:
        return (0, 0)
    M = linemarks.shape[0]
    i = 0
    m = -1  # number of current record we're in
    nxt = 0  # byte of beginning of last record
    line = 0  # current line in FASTQ record (0, 1, 2, 3)
    # find start of current line
    while True:
        if buf[i] == 10:
            i += 1
            if line == 0:
                linemarks[m, 3] = i
                if sequence_id >= 0:
                    linemarks[m, 4] = sequence_id
                    linemarks[m, 5] = 0
                    sequence_id += 1
            if i >= n:
                # we did not find valid record start
                if line == 0:
                    m += 1
                    nxt = n
                return (m, nxt)
        if line == 0:
            m += 1
            nxt = i
            if m >= M:
                return (M, nxt)
            linemarks[m, 2] = i
        elif line == 1:
            linemarks[m, 0] = i
        # find end of current line
        while buf[i] != 10:
            i += 1
            if i >= n:
                # we did not find the end of the line before the buffer was exhausted
                # we cannot set linemarks[m][1]
                return (m, nxt)
        if line == 1:
            linemarks[m, 1] = i
        line = (line + 1) % 4


def fastq_chunks(files,
        bufsize=2**23, maxreads=(2**23) // 200,
        subsample=1):
    """
    Yield all chunks from a list or tuple of FASTQ 'files'.
    A chunk is a pair (buffer, linemarks), where
    - buffer is readable/writable byte buffer
    - buffer[linemarks[i,0]:linemarks[i,1]] contains the i-th sequence 
      of the chunk; other line marks are not stored.
    - The part of linemarks that is returned is such that
      linemarks.shape[0] is at most maxreads and equals the number of reads.
    CAUTION: If bufsize is very small, such that not even a single FASTQ entry
      fits into the buffer, it will appear that the buffer is empty.
    """
    # defaults are good for single-threaded runs; multiply by #threads.
    if not (isinstance(files, tuple) or isinstance(files, list)):
        files = (files,)  # single file?
    if bufsize / 2**30 > 1.5:
        raise ValueError(f"ERROR: bufsize={bufsize/2**30} GiB must be <= 1.5 GiB (2**30 bytes); use smaller chunksize of fewer threads.")
    linemarks = np.empty((maxreads, 4), dtype=np.int32)
    buf = np.empty(bufsize, dtype=np.uint8)
    for file in files:
        assert file.file_type == "fastq"
        f = file.file
        prev = 0
        while True:
            read = f.readinto(buf[prev:])
            if read == 0 and prev == 0:
                break
            available = prev + read  # number of bytes available
            m, cont = _find_fastq_seqmarks(buf[:available], linemarks)
            if m <= 0:
                # TODO: check for FASTQ (buffer starts with @)
                raise RuntimeError(f"no complete records for bufsize {bufsize}")
                break
            chunk = (buf, linemarks[0:m:subsample, :])
            yield chunk
            # cont = linemarks[m-1,1] + 1
            prev = available - cont

            # Checks if the part at the end overlaps with the part at the start to which it should be copied.
            # This is not supported.
            # Also undefined behaviour in memcopy. memmove is not supported in numpy.
            assert prev < cont, "fastq_chunks: Increase maxreads or decrease bufsize."

            if prev > 0:
                buf[:prev] = buf[cont:available]
                # print(f"  moving buf[{cont}:{available}] to buf[0:{prev}]")


def fastq_chunks_paired(pair, bufsize=2**23, maxreads=2**23 // 200):
    """
    Yield all chunks from a pair of InputFileHandler objects.
    A chunk is a pair (buffer, linemarks), where
    - buffer is readable/writable byte buffer
    - buffer[linemarks[i,0]:linemarks[i,1]] contains the i-th sequence 
      of the chunk; other line marks are not stored.
    - The part of linemarks that is returned is such that
      linemarks.shape[0] is at most maxreads and equals the number of reads.
    CAUTION: If bufsize is very small, such that not even a single FASTQ entry
      fits into the buffer, it will appear that  the buffer is empty.
    """
    # defaults are good for single-threaded runs; multiply by #threads.
    (files1, files2) = pair
    if not (isinstance(files1, tuple) or isinstance(files1, list)):
        files1 = (files1,)
    if not (isinstance(files2, tuple) or isinstance(files2, list)):
        files2 = (files2,)
    linemarks1 = np.empty((maxreads, 4), dtype=np.int32)
    linemarks2 = np.empty((maxreads, 4), dtype=np.int32)
    buf1 = np.empty(bufsize, dtype=np.uint8)
    buf2 = np.empty(bufsize, dtype=np.uint8)
    if len(files1) != len(files2):
        raise RuntimeError("different numbers of fastq files for files1 and files2")
    for i in range(len(files1)):
        f1 = files1[i]
        f2 = files2[i]

        assert f1.file_type == f2.file_type == "fastq"

        prev1 = 0
        prev2 = 0
        while True:
            read1 = f1.file.readinto(buf1[prev1:])
            read2 = f2.file.readinto(buf2[prev2:])

            available1 = prev1 + read1
            available2 = prev2 + read2

            if read1 == 0 and read2 == 0:
                break

            m1, cont1 = _find_fastq_seqmarks(buf1[:available1], linemarks1)
            m2, cont2 = _find_fastq_seqmarks(buf2[:available2], linemarks2)
            if m1 <= 0 or m2 <= 0:
                # TODO: check for FASTQ (buffer starts with @)
                raise RuntimeError(f"no complete records for bufsize {bufsize}")
                break
            if m1 == m2:
                chunk = (buf1, linemarks1[:m1], buf2, linemarks2[:m2])
            elif m1 < m2:
                chunk = (buf1, linemarks1[:m1], buf2, linemarks2[:m1])
                cont2 = linemarks2[m1, 2]
            else:
                chunk = (buf1, linemarks1[:m2], buf2, linemarks2[:m2])
                cont1 = linemarks1[m2, 2]
            yield chunk
            prev1 = available1 - cont1
            prev2 = available2 - cont2
            if prev1 > 0:
                buf1[:prev1] = buf1[cont1:available1]
                buf1[prev1:] = 0
            if prev2 > 0:
                buf2[:prev2] = buf2[cont2:available2]
                buf2[prev2:] = 0
            # assert prev1 < cont1
            # assert prev2 < cont2


# FASTQ checking ####################################################

def fastqcheck(args):
    files = args.sequences
    if args.paired:
        success = fastqcheck_paired(list(zip(*[iter(files)] * 2)), args)
    else:
        success = fastqcheck_single(files, args)
    return success


def fastqcheck_paired(filepairs, args):
    success = True
    for (f1, f2) in filepairs:
        print(f"Checking {f1}, {f2}...")
        msg = "OK"
        try:
            for entry1, entry2 in zip(fastq_reads(f1), fastq_reads(f2)):
                c1 = entry1[0].split()[0]
                c2 = entry2[0].split()[0]
                if c1 != c2:
                    raise FormatError(f"headers {c1.decode()} and {c2.decode()} do not match")
        except FormatError as err:
            success = False
            msg = "FAILED: " + str(err)
        print(f"{f1}, {f2}: {msg}")
    return success


def fastqcheck_single(files, args):
    success = True
    for f in files:
        print(f"Checking {f}...")
        msg = "OK"
        try:
            for entry in fastq_reads(f):
                pass
        except FormatError as err:
            success = False
            msg = "FAILED: " + str(err)
        print(f"{f}: {msg}")
    return success


# FASTQ name guessing and argument parsing   ##########################

def guess_pairs(filenames, replacer):
    """guess_pairs(filenames, replacer):
    Return a list of file names where the read number (1/2) 
    has been replaced by the 'replacer'.
    Example: guess_pairs(['abc_R1.fq', 'xyz_R1.fq'], 2)
        returns ['abc_R2.fq', 'xyz_R2.fq'].
    """
    if replacer != 1 and replacer != 2:
        raise ValueError("Eguess_pairs: Parameter 'replacer' must be 1 or 2")
    # replace=1: Replace rightmost occurrence of '_R2' by '_R1'
    # replace=2: Replace rightmost occurrence of '_R1' by '_R2'
    orig = str(3 - replacer)
    o = "_R" + orig
    r = "_R" + str(replacer)
    pairnames = list()
    for name in filenames:
        start = name.rfind(o)
        if start < 0:
            raise ValueError(f"guess_pairs: FASTQ file name '{name}' does not contain '{o}'")
        pairnames.append(name[:start] + r + name[start + len(o):])
    return pairnames


def parse_fastq_args(args):
    """
    Parse args.{first, second, single, guess_pairs}
    Return (paired, fastq), where
    - paired is a bool that is True iff args.first or args.second is provided
    - fastq is a 1-tuple or a 2-tuple of lists of filenames.
      It is a 2-tuple iff paired == True.
    """
    argerror = ArgumentParser.error
    paired = False
    if args.first or args.second:
        paired = True
        if args.guess_pairs and args.first:
            if args.second:
                argerror("ERROR: With given --first, cannot specify --second together with --guess-pairs")
            args.second = guess_pairs(args.first, 2)
        elif args.guess_pairs and args.second:
            args.first = guess_pairs(args.second, 1)
        if len(args.first) != len(args.second):
            argerror(f"ERROR: --first and --second must specify the same number of files ({len(args.first)} vs {len(args.second)})")
        if args.first is None or args.second is None:
            argerror("ERROR: not enough information given for paired reads")
    if args.single:
        if paired:
            argerror("ERROR: cannot use --single together with --first/--second")
    fastq = (args.single,) if (not paired) else (args.first, args.second)
    return paired, fastq
