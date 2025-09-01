from contextlib import nullcontext

import numpy as np
from numba import njit, int32, int64, uint64

from ..lowlevel import debug
from ..lowlevel.conpro import (
    ConsumerProducer,
    CPInputMode,
    run_cps,
)
from ..lowlevel.conpro import \
    find_buffer_for_reading, find_buffer_for_writing, mark_buffer_for_writing, mark_buffer_for_reading
from ..lowlevel.libc import write_block
from ..lowlevel.llvm import printf
from ..lowlevel.aligned_arrays import aligned_zeros
from ..lowlevel.bitarray import bitarray
from ..io.generalio import cptask_read_file, _in_suffixes, OutputFileHandler
from ..io.generaldsio import load_data_structure
from ..mask import create_mask
from ..kmers import compile_positional_kmer_processor
new_encoding = True

if new_encoding:
    from ..dnaencode_fast import (
        quick_dna_to_2bits,
        compile_twobit_to_codes
    )
else:
    from ..dnaencode import (
        quick_dna_to_2bits,
        compile_twobit_to_codes
    )


def get_out_file(prefix, fastq, filter_reads, is_paired, force_compression=None):
    if prefix is None:
        raise ValueError("- Please provide an output name using --out or -o")
    fastq_org = fastq

    categories = ["keep"]
    if not filter_reads:
        categories.append('filter')
    compression = ''
    extension = ''
    if fastq.endswith(tuple(_in_suffixes.keys())):
        fastq, compression = fastq.rsplit(".", 1)
    if fastq.endswith(("fq", "fastq")):
        fastq, extension = fastq.rsplit('.', 1)

    if extension == '':
        raise ValueError(f'The input file {fastq_org} has no file extension')

    if force_compression:
        if force_compression != 'none':
            compression = force_compression
        else:
            compression = ''

    if is_paired:
        outfiles = tuple((f'{prefix}_{str(i)}_{c}.{extension}.{compression}').strip('.') for i in [1, 2] for c in categories)
    else:
        outfiles = tuple((f'{prefix}_{c}.{extension}.{compression}').strip('.') for c in categories)
    return outfiles


def load_index_data_structure(index, shared=False):
    # Load datastructure (index)
    index, _, infotup = load_data_structure(index, shared_memory=shared)
    if 'filtertype' in infotup[0]:
        appinfo = infotup[2]
        arr = index.array
        index_type = 'hash'
    elif 'hashtype' in infotup[0]:
        appinfo = infotup[3]
        arr = index.hashtable
        index_type = 'table'
    else:
        raise NotImplementedError("Only hash table or filter supported.")

    return index, infotup, appinfo, arr, index_type


def compile_single_classify_function(index_tuple, classify_mode, threshold, mask, rcmode):
    k = mask.k
    w = mask.w
    is_filter = hasattr(index_tuple, 'filtertype')

    # Getter function for table and filter
    if is_filter:
        is_contained = index_tuple.lookup
    else:
        get_value = index_tuple.get_value

        @njit(nogil=True)
        def is_contained(ds, key):
            return get_value(ds, key, default=uint64(1)) != 1

    if classify_mode:
        mask_tuple = mask.tuple
        mask_int = uint64(0)
        for i in mask_tuple:
            assert i < 64
            mask_int |= (1 << i)

        ba = bitarray(0)
        set_bit = ba.setor
        popcount = ba.popcount

        @njit(nogil=True)
        def func(ds, code, pos, ba):
            if is_contained(ds, code):
                set_bit(ba, pos, mask_int, w)

        _, kmers = compile_positional_kmer_processor(mask_tuple, func, rcmode=rcmode, new_encoding=new_encoding)

        @njit(nogil=True)
        def classify(ds, ba, seq):
            ba[:] = 0
            kmers(ds, seq, 0, len(seq), ba)
            nbits_set = popcount(ba, 0, len(seq))
            if threshold * len(seq) < nbits_set:
                return 1
            return 0

        return classify
    else:
        _, twobit_to_code = compile_twobit_to_codes(mask, rcmode)

        @njit(nogil=True, locals=dict(count=uint64, last=uint64, contained=uint64))
        def sampling_2(ds, _, seq):
            count = 0
            last = 0
            for i in range(0, len(seq) - w + 1, w // 2):
                kmer = twobit_to_code(seq, i)
                contained = is_contained(ds, kmer)
                if contained:
                    if last == 0:
                        count += w
                    else:
                        count += w // 2
                last = contained
                if threshold * len(seq) < count:
                    return 1
            return 0
        return sampling_2

    raise ValueError(f'- Classification mode {classify_mode} not supported!')


def compile_paired_classify_function(index_tuple, classify_mode, threshold, mask, rcmode):
    classify_single = compile_single_classify_function(index_tuple, classify_mode, threshold, mask, rcmode)

    @njit(nogil=True)
    def classify_paired(ds, ba, seq1, seq2):
        return classify_single(ds, ba, seq1) | classify_single(ds, ba, seq2)

    return classify_paired


def compile_cptask_classify(index_tuple, is_paired, classify_mode, threshold, mask, rcmode):
    if is_paired:
        classify = compile_paired_classify_function(index_tuple, classify_mode, threshold, mask, rcmode)
    else:
        classify = compile_single_classify_function(index_tuple, classify_mode, threshold, mask, rcmode)

    @njit(nogil=True)
    def _cptask_classify(index, stats, ba, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
        debugprint2("- running: _cptask_classify")
        assert inbuffers.ndim == 2
        assert outbuffers.ndim == 2
        M_in, N_in = ininfos.shape
        assert N_in % 4 == 0
        in_linemarkbuffers = ininfos.reshape(M_in, N_in // 4, 4)

        M_out, N_out = outinfos.shape
        assert N_out % 8 == 0
        out_linemarkbuffers = outinfos.reshape(M_out, N_out // 8, 8)

        wait_read = wait_write = 0
        in_active = -1  # active input buffer
        active_in_buffer = inbuffers[0]  # irrelevant
        buffersizes = active_in_buffer.shape[0] // 2
        failed = mytotal = 0
        while True:
            in_active, wait = find_buffer_for_reading(incontrol, in_active)
            wait_read += wait
            if in_active < 0:  # all finished
                debugprint2("- ending: cptask_classify")
                break
            out_active, wait = find_buffer_for_writing(outcontrol)
            wait_write += wait

            active_in_buffer = inbuffers[in_active]
            active_in_buffer1 = active_in_buffer[:buffersizes]
            active_in_buffer2 = active_in_buffer[buffersizes:buffersizes * 2]
            active_out_buffer = outbuffers[out_active]
            buffer_type = incontrol[in_active, 6]
            assert buffer_type == 0  # This should always be sequencing data
            nseqs = incontrol[in_active, 7]
            outcontrol[out_active, 7] = nseqs

            # write linemarks to outbuffer
            in_linemarks_all = in_linemarkbuffers[in_active]
            out_linemarks_all = out_linemarkbuffers[out_active]
            out_linemarks_all[:, :4] = in_linemarks_all[:N_out // 8, :]
            active_out_buffer[:] = active_in_buffer[:]

            if is_paired:
                in_linemarks_r1 = in_linemarks_all[:N_in // 8]
                in_linemarks_r2 = in_linemarks_all[N_in // 8:]

                out_linemarks_r1 = out_linemarks_all[:N_out // 16]
                out_linemarks_r2 = out_linemarks_all[N_out // 16:]

                for i in range(nseqs):
                    mytotal += 1
                    seq1 = active_in_buffer1[in_linemarks_r1[i, 0]:in_linemarks_r1[i, 1]]
                    seq2 = active_in_buffer2[in_linemarks_r2[i, 0]:in_linemarks_r2[i, 1]]
                    quick_dna_to_2bits(seq1)
                    quick_dna_to_2bits(seq2)

                    if classify_mode:
                        max_seq_len = max(len(seq1), len(seq2))
                        if max_seq_len > ba.size * 64:
                            ba = np.empty(max_seq_len // 64 + 1, dtype=np.uint64)

                    result = classify(index, ba, seq1, seq2)
                    stats[result] += 1

                    out_linemarks_r1[i, 4] = result
                    out_linemarks_r2[i, 4] = result

            else:
                for i in range(nseqs):
                    mytotal += 1
                    seq = active_in_buffer[in_linemarks_all[i, 0]:in_linemarks_all[i, 1]]
                    quick_dna_to_2bits(seq)
                    if classify_mode:
                        seq_len = len(seq)
                        if seq_len > ba.size * 64:
                            ba = np.empty(seq_len // 64 + 1, dtype=np.uint64)
                    result = classify(index, ba, seq)
                    stats[result] += 1
                    out_linemarks_all[i, 4] = result

            mark_buffer_for_writing(incontrol, in_active)
            mark_buffer_for_reading(outcontrol, out_active)
        return (mytotal, failed, wait_read, wait_write, -(failed > 0))

    return _cptask_classify


def compile_cptask_write(filter_reads, is_paired, buffersizes=2**16, progress=False, count_only=False):

    if not is_paired:
        buffersizes *= 2

    @njit(nogil=True, locals=dict(
        ntodo=int32, errorcode=int32, offset=int32, skip=int32,
        wait=int64, wait_read=int64, wait_write=int64,
        fd1=int32, fd2=int32, fd3=int32, fd4=int32))
    def cptask_write_linemarked_buffers_into_pairedfastq(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
        """
        Has to be run as a thread within a consumer producer task.
        Keep reading bytes from one of the inbuffers (cycling),
        splits the data in parts and writes it to files
        until a finished buffer is found or an error occurs.
        """
        M, N = ininfos.shape
        assert N % 8 == 0
        linemarkbuffers = ininfos.reshape(M, N // 8, 8)

        # define output buffers
        if filter_reads:
            fd1, fd3 = fd
            outbuffer_t0_r1 = np.empty(buffersizes, dtype=np.uint8)
            outbuffer_t0_r2 = np.empty(buffersizes, dtype=np.uint8)
        else:
            fd1, fd2, fd3, fd4 = fd
            outbuffer_t0_r1 = np.empty(buffersizes, dtype=np.uint8)
            outbuffer_t0_r2 = np.empty(buffersizes, dtype=np.uint8)
            outbuffer_t1_r1 = np.empty(buffersizes, dtype=np.uint8)
            outbuffer_t1_r2 = np.empty(buffersizes, dtype=np.uint8)

        wait_read = wait_write = 0
        nactive = -1
        active_buffer = inbuffers[0]  # irrelevant
        processed_reads = 0
        while True:
            writer_t0_r1 = writer_t0_r2 = writer_t1_r1 = writer_t1_r2 = 0
            old = nactive
            nactive, wait = find_buffer_for_reading(incontrol, old)
            if nactive < 0:  # all finished
                debugprint2("- ending: cptask_write_file")
                break
            wait_write += wait
            active_buffer = inbuffers[nactive]
            active_buffer1 = active_buffer[:len(active_buffer) // 2]
            active_buffer2 = active_buffer[len(active_buffer) // 2:]
            linemarks1 = linemarkbuffers[nactive, :N // 16]
            linemarks2 = linemarkbuffers[nactive, N // 16:]

            errorcode = incontrol[nactive, 1]
            if errorcode != 0:
                errorcode = -errorcode
                break
            nseqs = incontrol[nactive, 7]
            processed_reads += nseqs

            # sort reads into out buffer:
            for i in range(nseqs):
                read_linemarks1 = linemarks1[i]
                read_linemarks2 = linemarks2[i]
                if filter_reads:
                    assert read_linemarks1[4] == read_linemarks2[4]
                    read_type = read_linemarks1[4]
                    if read_type == 1:
                        continue
                    assert read_type == 0

                    r1_start = read_linemarks1[2]
                    r1_end = read_linemarks1[3]
                    r2_start = read_linemarks2[2]
                    r2_end = read_linemarks2[3]

                    r1_len = r1_end - r1_start
                    r2_len = r2_end - r2_start

                    outbuffer_t0_r1[writer_t0_r1:writer_t0_r1 + r1_len] = active_buffer1[r1_start:r1_end]
                    outbuffer_t0_r2[writer_t0_r2:writer_t0_r2 + r2_len] = active_buffer2[r2_start:r2_end]

                    writer_t0_r1 += r1_len
                    writer_t0_r2 += r2_len
                else:
                    # same classification for both reads
                    assert read_linemarks1[4] == read_linemarks2[4]
                    read_type = read_linemarks1[4]

                    r1_start = read_linemarks1[2]
                    r1_end = read_linemarks1[3]
                    r2_start = read_linemarks2[2]
                    r2_end = read_linemarks2[3]

                    r1_len = r1_end - r1_start
                    r2_len = r2_end - r2_start

                    if read_type == 0:
                        outbuffer_t0_r1[writer_t0_r1:writer_t0_r1 + r1_len] = active_buffer1[r1_start:r1_end]
                        outbuffer_t0_r2[writer_t0_r2:writer_t0_r2 + r2_len] = active_buffer2[r2_start:r2_end]
                        writer_t0_r1 += r1_len
                        writer_t0_r2 += r2_len
                    elif read_type == 1:
                        outbuffer_t1_r1[writer_t1_r1:writer_t1_r1 + r1_len] = active_buffer1[r1_start:r1_end]
                        outbuffer_t1_r2[writer_t1_r2:writer_t1_r2 + r2_len] = active_buffer2[r2_start:r2_end]
                        writer_t1_r1 += r1_len
                        writer_t1_r2 += r2_len
                    # else:
                    #     raise RuntimeError(f'Wrong classification {read_type=}. Only 0 (keep) and 1 (filter) supported')
            nwritten_fd1 = write_block(fd1, outbuffer_t0_r1, writer_t0_r1)
            assert nwritten_fd1 == writer_t0_r1
            nwritten_fd3 = write_block(fd3, outbuffer_t0_r2, writer_t0_r2)
            assert nwritten_fd3 == writer_t0_r2

            if not filter_reads:
                nwritten_fd2 = write_block(fd2, outbuffer_t1_r1, writer_t1_r1)
                assert nwritten_fd2 == writer_t1_r1
                nwritten_fd4 = write_block(fd4, outbuffer_t1_r2, writer_t1_r2)
                assert nwritten_fd4 == writer_t1_r2

            mark_buffer_for_writing(incontrol, nactive)

            if progress:
                printf("- %i reads processed.\r", processed_reads)

        mark_buffer_for_writing(incontrol, nactive, force=True)
        if progress:
            printf("- Finished: all %i reads processed.\n", processed_reads)
        return (wait_read, wait_write, errorcode)

    @njit(nogil=True, locals=dict(
        ntodo=int32, errorcode=int32, offset=int32, skip=int32,
        wait=int64, wait_read=int64, wait_write=int64,
        fd1=int32, fd2=int32))
    def cptask_write_linemarked_buffers_into_fastq(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
        """
        Has to be run as a thread within a consumer producer task.
        Keep reading bytes from one of the inbuffers (cycling),
        splits the data in parts and writes it to files
        until a finished buffer is found or an error occurs.
        """
        M, N = ininfos.shape
        assert N % 8 == 0
        linemarkbuffers = ininfos.reshape(M, N // 8, 8)

        # define output buffers
        if filter_reads:
            fd1 = fd[0]
            outbuffer_t0 = np.empty(buffersizes, dtype=np.uint8)
        else:
            fd1, fd2 = fd
            outbuffer_t0 = np.empty(buffersizes, dtype=np.uint8)
            outbuffer_t1 = np.empty(buffersizes, dtype=np.uint8)

        wait_read = wait_write = 0
        nactive = -1
        active_buffer = inbuffers[0]  # irrelevant
        while True:
            writer_t0 = writer_t1 = 0
            old = nactive
            nactive, wait = find_buffer_for_reading(incontrol, old)
            if nactive < 0:  # all finished
                debugprint2("- ending: cptask_write_file")
                break
            wait_write += wait
            active_buffer = inbuffers[nactive]
            active_linemarks = linemarkbuffers[nactive]

            errorcode = incontrol[nactive, 1]
            if errorcode != 0:
                errorcode = -errorcode
                break
            nseqs = incontrol[nactive, 7]

            # sort reads into out buffer:
            for i in range(nseqs):
                read_linemarks = active_linemarks[i]
                if filter_reads:
                    read_type = read_linemarks[4]
                    if read_type == 1:
                        continue
                    assert read_type == 0

                    r1_start = read_linemarks[2]
                    r1_end = read_linemarks[3]
                    r1_len = r1_end - r1_start
                    outbuffer_t0[writer_t0:writer_t0 + r1_len] = active_buffer[r1_start:r1_end]
                    writer_t0 += r1_len
                else:
                    # same classification for both reads
                    read_type = read_linemarks[4]
                    r1_start = read_linemarks[2]
                    r1_end = read_linemarks[3]
                    r1_len = r1_end - r1_start

                    if read_type == 0:
                        outbuffer_t0[writer_t0:writer_t0 + r1_len] = active_buffer[r1_start:r1_end]
                        writer_t0 += r1_len
                    elif read_type == 1:
                        outbuffer_t1[writer_t1:writer_t1 + r1_len] = active_buffer[r1_start:r1_end]
                        writer_t1 += r1_len

            nwritten_fd1 = write_block(fd1, outbuffer_t0, writer_t0)
            assert nwritten_fd1 == writer_t0

            if not filter_reads:
                nwritten_fd2 = write_block(fd2, outbuffer_t1, writer_t1)
                assert nwritten_fd2 == writer_t1

            mark_buffer_for_writing(incontrol, nactive)
        mark_buffer_for_writing(incontrol, nactive, force=True)
        return (wait_read, wait_write, errorcode)

    @njit(nogil=True, locals=dict(
        ntodo=int32, errorcode=int32, offset=int32, skip=int32,
        wait=int64, wait_read=int64, wait_write=int64,
        fd1=int32, fd2=int32))
    def cptask_count_only(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
        """
        Has to be run as a thread within a consumer producer task.
        Do nothing, except marking buffer for writing
        """
        wait_read = wait_write = 0
        nactive = -1
        active_buffer = inbuffers[0]  # irrelevant
        while True:
            old = nactive
            nactive, wait = find_buffer_for_reading(incontrol, old)
            wait_write += wait

            if nactive < 0:  # all finished
                debugprint2("- ending: cptask_write_file")
                break

            errorcode = incontrol[nactive, 1]
            if errorcode != 0:
                errorcode = -errorcode
                break

            wait_write += wait
            active_buffer = inbuffers[nactive]
            mark_buffer_for_writing(incontrol, nactive)
        mark_buffer_for_writing(incontrol, nactive, force=True)
        return (wait_read, wait_write, errorcode)

    if count_only:
        return cptask_count_only
    elif is_paired:
        return cptask_write_linemarked_buffers_into_pairedfastq
    return cptask_write_linemarked_buffers_into_fastq


def cptask_write_file(fnames, is_paired, filter_reads, buffersizes, compression_threads, compression_level, progress, count_only, *allbuffers):
    """
    ConsumerProducer task that
    """
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    if isinstance(fnames, tuple):
        if is_paired and not filter_reads:
            fname1, fname2, fname3, fname4 = fnames
        elif is_paired and filter_reads:
            fname1, fname3 = fnames
            fname2 = fname4 = ''
        elif not is_paired and not filter_reads:
            fname1, fname2 = fnames
            fname3 = fname4 = ''
        elif not is_paired and filter_reads:
            fname1 = fnames[0]
            fname2 = fname3 = fname4 = ''
    else:
        fname1 = fnames

    _cptask_write_file = compile_cptask_write(filter_reads, is_paired, buffersizes, progress=progress, count_only=count_only)

    with OutputFileHandler(fname1, compression_threads=compression_threads, compression_level=compression_level) if not count_only else nullcontext() as keep_1, \
         OutputFileHandler(fname2, compression_threads=compression_threads, compression_level=compression_level) if not count_only and not filter_reads else nullcontext() as fltr_1, \
         OutputFileHandler(fname3, compression_threads=compression_threads, compression_level=compression_level) if not count_only and is_paired else nullcontext() as keep_2, \
         OutputFileHandler(fname4, compression_threads=compression_threads, compression_level=compression_level) if not count_only and is_paired and not filter_reads else nullcontext() as fltr_2:

        if not count_only:
            ft = keep_1.file_type
            assert ft == 'fastq'

        fds = []
        if keep_1 is not None:
            fds.append(int32(keep_1.fd))
        if fltr_1 is not None:
            fds.append(int32(fltr_1.fd))
        if keep_2 is not None:
            fds.append(int32(keep_2.fd))
        if fltr_2 is not None:
            fds.append(int32(fltr_2.fd))
        fds = tuple(fds)

        result = _cptask_write_file(fds, *allbuffers)

        return fnames, *result


def process_files(index_tuple,
                  fastqs,
                  pairs,
                  outfiles,
                  classify_mode,
                  threshold,
                  mask,
                  rcmode,
                  buffersizes=2**16,
                  threads_classify=4,
                  filter_reads=False,
                  compression_threads=1,
                  compression_level=1,
                  progress=False,
                  count_only=False,
                  ):

    is_paired = pairs is not None
    nreads_per_buffer = buffersizes // 256
    nreads_per_buffer += nreads_per_buffer % 2

    # 1. Define jobs to read files
    if is_paired:
        fnames = list(zip(fastqs, pairs))
    else:
        fnames = fastqs

    read_jobs = ConsumerProducer(
        name='file_reader',
        tasks=[(cptask_read_file, fname, None, mask.w) for fname in fnames],
        nworkers=1,
        noutbuffers_per_worker=4 * threads_classify,
        specific_outbuffers_per_worker=True,
        datatype=np.uint8,
        infotype=np.int64,
        dataitems_per_buffer=buffersizes,
        infoitems_per_buffer=nreads_per_buffer,
        infoitemsize=4,  # linemarks use 4 numbers per sequence
    )

    cptask_classify = compile_cptask_classify(index_tuple, is_paired, classify_mode, threshold, mask, rcmode)
    index = index_tuple.hashtable if hasattr(index_tuple, 'hashtype') else index_tuple.array

    # stat array
    for i in range(threads_classify):
        stat_arrays = [aligned_zeros(2) for _ in range(threads_classify)]
    if classify_mode:
        classify_tasks = [(cptask_classify, index, stat_arrays[i], np.empty(5, dtype=np.uint64)) for i in range(threads_classify)]
    else:
        classify_tasks = [(cptask_classify, index, stat_arrays[i], np.empty(0, dtype=np.uint64)) for i in range(threads_classify)]
    classify_jobs = ConsumerProducer(
        name='classifier',
        input=read_jobs,
        tasks=classify_tasks,
        nworkers=threads_classify,
        noutbuffers_per_worker=4,
        specific_outbuffers_per_worker=True,
        datatype=np.uint8,
        infotype=np.int64,
        dataitems_per_buffer=buffersizes,
        infoitems_per_buffer=nreads_per_buffer,
        infoitemsize=8,
    )

    write_jobs = ConsumerProducer(
        name='file_writer',
        input=classify_jobs,
        tasks=[(cptask_write_file, outfiles, is_paired, filter_reads, buffersizes, compression_threads, compression_level, progress, count_only)],
        nworkers=1,
    )

    # failures = run_cps(read_jobs, classify_jobs)
    failures = run_cps(read_jobs, classify_jobs, write_jobs)

    for i in range(1, threads_classify):
        stat_arrays[0] += stat_arrays[i]

    return failures == 0, stat_arrays[0]


def print_class_stats(prefix, stats):
    classes = ["keep", "filter"]

    percentages = [i / sum(stats) * 100 for i in stats]
    str_counts = "\t".join(str(i) for i in stats)
    ndigits = max(map(lambda x: len(str(x)), stats))

    timestamp0(msg="\n## Classification Statistics")
    debugprint0("\n```")
    debugprint0("prefix\tkeep\tfilter")
    debugprint0(f"{prefix}\t{str_counts}")
    debugprint0("```\n")
    debugprint0("```")
    debugprint0(f"| prefix    | {prefix} ")
    for i in range(len(classes)):
        debugprint0(f"| {classes[i]:9s} | {stats[i]:{ndigits}d} | {percentages[i]:5.2f}% |")
    debugprint0("```")
    debugprint0()


def main(args):
    """main method for classifying reads"""
    global debugprint0, debugprint1, debugprint2
    global timestamp0, timestamp1, timestamp2
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    timestamp0, timestamp1, timestamp2 = debug.timestamp

    starttime = timestamp0(msg="\n# Cleanifier filter")
    debugprint0("\n- (c) 2019-2025 by Jens Zentgraf, Johanna Elena Schmitz, Sven Rahmann, Algorithmic Bioinformatics, Saarland University")
    debugprint0("- Licensed under the MIT License")

    # Check parameters
    if 0 > args.threshold > 1:
        debugprint0(f"- {args.threshold} is not a valid threshold. 0.0 < t < 1.0")
        exit(1)

    index, _, appinfo, _, _ = load_index_data_structure(args.index, shared=args.shared)

    if args.prefix is None:
        if not args.count:
            raise ValueError('--Provide a prefix for the output files or the --count parameter')

    mask = create_mask(appinfo['mask'])
    k, tmask = mask.k, mask.tuple
    assert k == appinfo['k']
    rcmode = appinfo['rcmode']

    # classify reads from either FASTQ or FASTA files
    timestamp1(msg='- Begin classification')
    debugprint1(f"- mask: {k=}, w={tmask[-1] + 1}, tuple={tmask}")

    if not args.fastq:
        # NO --fastq given, nothing to do
        debugprint0("- No FASTQ files to classify. Nothing to do. Have a good day.")
        exit(1)

    # check if same number of fastq files are provided for paired end reads
    is_paired = False
    if args.pairs:
        if len(args.fastq) != len(args.pairs):
            raise ValueError("- Different number of files in --fastq and --pairs")
        is_paired = True

    classify_mode = args.sensitive
    filter_reads = not args.keep_host
    threshold = args.threshold
    classify_threads = max(1, args.threads - 2)
    buffersizes = 2 * 2**args.buffersize if is_paired else 2**args.buffersize

    outfiles = get_out_file(args.prefix, args.fastq[0], filter_reads, is_paired, force_compression=args.compression) if args.prefix is not None else None
    success, stats = process_files(index, args.fastq, args.pairs, outfiles, classify_mode, threshold, mask, rcmode, buffersizes, classify_threads, filter_reads, args.compression_threads, args.compression_level, args.progress, args.count)
    assert success
    print_class_stats(args.prefix, stats)
