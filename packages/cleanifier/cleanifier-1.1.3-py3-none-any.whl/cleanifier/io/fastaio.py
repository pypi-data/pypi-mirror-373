from numba import njit, uint8, int32, int64, uint64, boolean
from numba.typed import Dict

from .seqio import _universal_reads
from ..dnaencode import dna_to_2bits
from ..lowlevel.libc import read_block
from ..lowlevel.conpro import \
    find_buffer_for_writing, \
    mark_buffer_for_reading, mark_buffer_for_writing

# FASTA/gz handling ######################################


@njit(nogil=True, locals=dict(
    c=uint8, writer=int64, reader=int64, cseq=uint64,
    bsize=uint64))
def remove_linebreaks(buffer, linemarks):
    # linemarks.shape == (N, 4)
    # linemarks: (start_seq, end_seq, start_record, end_record)
    bsize = buffer.size
    reader = 0  # position in buffer
    writer = 0  # position in buffer
    cseq = 0  # counts sequence number

    # buffer always starts at 0
    linemarks[cseq, 0] = 0
    linemarks[cseq, 2] = 0

    while reader < bsize:
        while reader < bsize and (buffer[reader] >= 65):
            buffer[writer] = buffer[reader]
            writer += 1
            reader += 1
        if reader >= bsize:
            break

        c = buffer[reader]
        if c == 10 or c == 13:  # we found a line break
            reader += 1
            continue

        if c == 62:  # we found the start of a header line '>'
            if writer != 0:
                # Set end of read and record
                linemarks[cseq, 1] = writer
                linemarks[cseq, 3] = writer
                cseq += 1
                if len(linemarks) <= cseq:
                    while reader < bsize:
                        buffer[writer] = buffer[reader]
                        writer += 1
                        reader += 1
                    return (writer, cseq, False)
                assert len(linemarks) > cseq
                # Set start of record
                linemarks[cseq, 2] = writer
            # Skip the current header
            while buffer[reader] != 10 and buffer[reader] != 13:
                buffer[writer] = buffer[reader]
                writer += 1
                reader += 1
                if reader >= bsize:
                    return (writer, cseq, False)
            # set start of read
            linemarks[cseq, 0] = writer
            # reader is now on a line break
            continue

        print("Warning: UNSUPPORTED FASTA CHARACTER INGORED (comments with ';' not supported)", c, chr(c))
        reader += 1

    linemarks[cseq, 1] = writer
    linemarks[cseq, 3] = writer
    assert reader == bsize
    return (writer, cseq + 1, True)


@njit(nogil=True, locals=dict(
    ntodo=int64, errorcode=int64, offset=int64,
    wait=int64, wait_read=int64, wait_write=int64,
    end_buffer=uint64, nseq=uint64, inside_seq=boolean))
def cptask_read_fasta_into_buffers(fd, W, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
    """
    Has to be run as a thread witin a consumer producer task.
    Keep reading bytes into one of the outbuffers (cycling),
    and compute linemarks in one of the outinfos (same index, cycling),
    until a new header is reached or EOF or an error occurs.
    Return 0 (EOF), or an error code (negative), corresponding to -os.errno.
    """
    # debugprint1("- cptask_read_fasta_into_linemarked_buffers started, fd =", fd, "; output shapes: ",
    #     outbuffers.shape, outcontrol.shape, outinfos.shape)
    # assert (inbuffers is None) and (incontrol is None) and (ininfos is None)
    # if outbuffers.shape[0] < 2:
    #     raise ValueError("cptask_read_fasta_into_buffers: must have 2 or more output buffers per worker")
    M, N = outinfos.shape
    errorcode = 0
    # assert N % 4 == 0
    linemarkbuffers = outinfos.reshape(M, N // 4, 4)

    end_buffer = offset = ntodo = wait_read = wait_write = 0
    nactive = -1
    active_buffer = outbuffers[0]  # irrelevant
    inside_seq = True
    header_seq = False
    nseq = 0
    while True:
        old = nactive
        old_buffer = active_buffer
        nactive, wait = find_buffer_for_writing(outcontrol, old)
        if nactive < 0:
            break
        wait_write += wait
        active_buffer = outbuffers[nactive]
        active_buffer[:] = 0
        if old >= 0:
            if offset > 0:
                if header_seq:
                    last_seq_length = linemarkbuffers[old, nseq, 1] - linemarkbuffers[old, nseq, 0]
                    last_rec_length = linemarkbuffers[old, nseq, 3] - linemarkbuffers[old, nseq, 2]
                    start_header = linemarkbuffers[old, nseq, 2]
                    end_header = start_seq = linemarkbuffers[old, nseq, 0]
                    end_seq = linemarkbuffers[old, nseq, 1]
                    header_length = end_header - start_header
                    seq_length = end_seq - start_seq
                    active_buffer[0:header_length] = old_buffer[start_header:end_header]
                    active_buffer[header_length] = 10
                    active_buffer[header_length + 1:header_length + 1 + seq_length] = old_buffer[start_seq:end_seq]
                else:
                    active_buffer[0:offset] = old_buffer[(end_buffer - offset):end_buffer]
            mark_buffer_for_reading(outcontrol, old)
        ntodo = read_block(int32(fd), active_buffer, offset)  # ntodo is the number of read bytes
        if ntodo <= 0:
            # Error while reading a new block
            if ntodo < 0:
                errorcode = ntodo
                break
            # Nothing read and the offset is not a full (gapped) k-mer
            if offset < W:
                break
            # Nothing read but we still have some data in the buffer
            ntodo = offset

        offset = 0
        header_seq = False
        end_buffer, nseq, inside_seq = remove_linebreaks(active_buffer[:ntodo], linemarkbuffers[nactive])
        # end_buffer: length of compacted buffer;
        # nseq: number of used linemarks;
        # inside_seq: bool, True means we are inside a DNA sequence
        if inside_seq:
            last_seq_length = linemarkbuffers[nactive, nseq - 1, 1] - linemarkbuffers[nactive, nseq - 1, 0]
            last_rec_length = linemarkbuffers[nactive, nseq - 1, 3] - linemarkbuffers[nactive, nseq - 1, 2]
            if last_seq_length < W:
                header_seq = True
                offset = last_rec_length + 1
                nseq -= 1
            else:
                offset = (W - 1)
        else:
            offset = end_buffer - linemarkbuffers[nactive, nseq - 1, 3]

        outcontrol[nactive, 7] = nseq
        outcontrol[nactive, 6] = 0  # buffer type sequence data

    mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer
    return (wait_read, wait_write, errorcode)


@njit(nogil=True)
def generate_CHR_ENCODING():
    CHR_ENCODINGS = Dict.empty(key_type=uint8, value_type=uint64)
    for value, key in enumerate([i for i in range(1, 23)] + [88, 89, 77]):
        CHR_ENCODINGS[key] = uint64(value + 1)
    return CHR_ENCODINGS


@njit(nogil=True, locals=dict(
    s_seq=uint64, e_seq=uint64, s_rec=uint64, e_rec=uint64,
    current_pos=uint64, current_chrom=uint64, header=uint8[:]))
def analyze_seq_header(buffer, linemarks, current_chrom, current_pos, CHR_ENCODINGS):
    for linemark in linemarks:
        s_seq = linemark[0]  # Start position of the sequence data in the buffer
        e_seq = linemark[1]  # End position of the sequence data in the buffer
        s_rec = linemark[2]  # Start position of the record in the buffer
        e_rec = linemark[3]  # End position of the record in the buffer (should be equal to e_seq)

        # If the seq and the record start at the same position,
        # there is no header and we use the provided current
        # chromosome and position
        if s_seq == s_rec:
            linemark[4] = current_chrom
            linemark[5] = current_pos

            # Add length of the buffer to the current offset
            current_pos += e_seq - s_seq
            continue

        # We are not in an old sequence.
        # We need to get the new chromosome.
        # The start position is always 0
        header = buffer[s_rec:s_seq]
        assert header[0] == 62  # header should start with >
        # find first space in the header
        for i in range(len(header)):
            if header[i] == 32:
                break
        header = header[1:i]  # remove > at the start of the header

        if len(CHR_ENCODINGS) == 0:
            current_chrom += 1
        else:
            for key, value in CHR_ENCODINGS:
                if len(key) == len(header) and (key == header).all():
                    current_chrom = value
                    break
            else:
                print("- Warning Cannot encode header:", header)
                print("- Chromsome will be set to 0")
                current_chrom = 0

        linemark[4] = current_chrom
        linemark[5] = 0
        # Update the current pos for this read.
        # If this is the last read in the buffer we need it for the next buffer.
        # If not, it is overwritten by the next entry
        current_pos = e_seq - s_seq

    return current_chrom, current_pos


@njit(nogil=True, locals=dict(
    ntodo=int32, errorcode=int32, offset=int32, skip=int32,
    wait=int64, wait_read=int64, wait_write=int64, chromosome=uint64,
    position=uint64, nseq=int64))
def cptask_read_fasta_chrom_pos_into_buffers(fd, W, CHR_mapping, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
    """
    Has to be run as a thread within a consumer producer task.
    Keep reading bytes into one of the outbuffers (cycling),
    and compute linemarks in one of the outinfos (same index, cycling),
    until a new header is reached or EOF or an error occurs.
    Return 0 (EOF), or an error code (negative), corresponding to -os.errno.
    """
    # We need an additional slot for the offset and position
    M, N = outinfos.shape
    errorcode = 0
    assert N % 6 == 0
    linemarkbuffers = outinfos.reshape(M, N // 6, 6)

    end_buffer = offset = ntodo = wait_read = wait_write = 0
    nactive = -1
    active_buffer = outbuffers[0]  # irrelevant
    inside_seq = True
    header_seq = False
    nseq = 0
    position = 0
    chromosome = 0
    while True:
        old = nactive
        old_buffer = active_buffer
        nactive, wait = find_buffer_for_writing(outcontrol, old)
        wait_write += wait
        active_buffer = outbuffers[nactive]
        if old >= 0:
            if offset > 0:
                if header_seq:
                    start_header = linemarkbuffers[old, nseq, 2]
                    end_header = start_seq = linemarkbuffers[old, nseq, 0]
                    end_seq = linemarkbuffers[old, nseq, 1]
                    header_length = end_header - start_header
                    seq_length = end_seq - start_seq
                    active_buffer[0:header_length] = old_buffer[start_header:end_header]
                    active_buffer[header_length] = 10
                    active_buffer[header_length + 1:header_length + 1 + seq_length] = old_buffer[start_seq:end_seq]
                else:
                    active_buffer[0:offset] = old_buffer[(end_buffer - offset):end_buffer]
            mark_buffer_for_reading(outcontrol, old)
        ntodo = read_block(int32(fd), active_buffer, offset)  # ntodo is the number of read bytes
        if ntodo <= 0:
            # Error while reading a new block
            if ntodo < 0:
                errorcode = ntodo
                break
            # Nothing read and the offset is not a full (gapped) k-mer
            if offset < W:
                break
            # Nothing read but we still have some data in the buffer
            ntodo = offset

        offset = 0
        header_seq = False
        end_buffer, nseq, inside_seq = remove_linebreaks(active_buffer[:ntodo], linemarkbuffers[nactive])
        # end_buffer: length of compacted buffer; nseq: number of used linemarks;
        # nxt: up to where we processed the buffer (for offset computation);
        # inside_seq: bool, True means we are inside a DNA sequence

        if inside_seq:
            # We stopped in a sequence
            last_seq_length = linemarkbuffers[nactive, nseq - 1, 1] - linemarkbuffers[nactive, nseq - 1, 0]
            last_rec_length = linemarkbuffers[nactive, nseq - 1, 3] - linemarkbuffers[nactive, nseq - 1, 2]
            if last_seq_length < W:
                header_seq = True
                offset = last_rec_length + 1
                nseq -= 1
            else:
                offset = (W - 1)
        else:
            offset = end_buffer - linemarkbuffers[nactive, nseq - 1, 3]

        outcontrol[nactive, 7] = nseq
        outcontrol[nactive, 6] = 0  # buffer type sequence data

        chromosome, position = analyze_seq_header(active_buffer[:ntodo], linemarkbuffers[nactive][:nseq], chromosome, position, CHR_mapping)
        position -= (W - 1)
    mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer
    return (wait_read, wait_write, errorcode)


# Generator that yields all sequences and values from FASTA files

def all_fasta_seqs(fastas, value_from_name, both, skipvalue, *, progress=False):
    """
    Yield a (sq, v1, v2) triple for each sequence in given fastas, where:
    - sq is the two-bit-encoded sequence,
    - v1 is the first value derived from the header using value_from_name,
    - v2 is the second value derived from the header using value_from_name,
      or identical to v1 if both==False.
    Sequences whose v1 evaluates to skipvalue are skipped.
    Progress is printed to stdout if progress=True.
    """
    for fasta in fastas:
        print(f"# Processing '{fasta}':")
        for header, seq in fasta_reads(fasta):
            name = header.split()[0]
            v1 = value_from_name(name, 1)
            if v1 == skipvalue:
                if progress:
                    print(f"#   sequence '{name.decode()}': length {len(seq)}, skipping")
                continue
            v2 = value_from_name(name, 2) if both else v1
            if progress:
                print(f"#   sequence '{name.decode()}': length {len(seq)}, values {v1}, {v2}")
            sq = dna_to_2bits(seq)
            yield (name, sq, v1, v2)


def fasta_reads(files, sequences_only=False):
    """
    For the given
    - list or tuple of FASTA paths,
    - single FASTA path (string),
    - open binary FASTA file-like object f,
    yield a pair of bytes (header, sequence) for each entry (of each file).
    If sequences_only=True, yield only the sequence of each entry.
    This function operatates at the bytes (not string) level.
    The header DOES NOT contain the initial b'>' character.
    If f == "-", the stdin buffer is used.
    Automatic gzip decompression is provided,
    if f is a string and ends with .gz or .gzip.
    """
    func = _fasta_reads_from_filelike if not sequences_only else _fasta_seqs_from_filelike
    if isinstance(files, list) or isinstance(files, tuple):
        # multiple files
        for f in files:
            yield from _universal_reads(f, func)
    else:
        # single file
        yield from _universal_reads(files, func)


def _fasta_reads_from_filelike(f, COMMENT=b';'[0], HEADER=b'>'[0]):
    strip = bytes.strip
    header = seq = None
    for line in f:
        line = strip(line)
        if len(line) == 0:
            continue
        if line[0] == COMMENT:
            continue
        if line[0] == HEADER:
            if header is not None:
                yield (header, seq)
            header = line[1:]
            seq = bytearray()
            continue
        seq.extend(line)
    if header is not None:
        yield (header, seq)


def _fasta_seqs_from_filelike(f, COMMENT=b';'[0], HEADER=b'>'[0]):
    strip = bytes.strip
    header = seq = False
    for line in f:
        line = strip(line)
        if len(line) == 0:
            continue
        if line[0] == COMMENT:
            continue
        if line[0] == HEADER:
            if header:
                yield seq
            header = True
            seq = bytearray()
            continue
        seq.extend(line)
    yield seq


# FASTA header extraction ###########################################

_SEPARATORS = {'TAB': '\t', 'SPACE': ' '}


def fastaextract(args):
    """extract information from FASTA headers and write in tabular form to stdout"""
    files = args.files
    items = args.items
    seps = args.separators
    sfx = [args.suffix] if args.suffix else []
    seps = [_SEPARATORS.get(sep.upper(), sep) for sep in seps]
    if items is None: 
        items = list()
        seps = list()
    if len(seps) == 1:
        seps = seps * len(items)
    seps = [""] + seps
    head = ['transcript_id'] + items

    first = [x for t in zip(seps, head) for x in t] + sfx
    print("".join(first))
    for f in files:
        for (header, _) in fasta_reads(f):
            infolist = get_header_info(header, items, ":", seps) + sfx
            print("".join(infolist))


def get_header_info(header, items, assigner, seps):
    fields = header.decode("ascii").split()
    assigners = [i for (i, field) in enumerate(fields) if assigner in field]
    if 0 in assigners: 
        assigners.remove(0)
    D = dict()
    if items is None:
        items = list()
    for j, i in enumerate(assigners):
        field = fields[i]
        pos = field.find(assigner)
        assert pos >= 0
        name = field[:pos]
        nexti = assigners[j + 1] if j + 1 < len(assigners) else len(fields)
        suffix = "_".join(fields[i + 1:nexti])
        if len(suffix) == 0:
            D[name] = field[(pos + 1):]
        else:
            D[name] = field[(pos + 1):] + '_' + suffix
    # dictionary D now has values for all fields
    L = [seps[0], fields[0]]
    for i, item in enumerate(items):
        if item in D:
            L.append(seps[i + 1])
            L.append(D[item])
    return L
