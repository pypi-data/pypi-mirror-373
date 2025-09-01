from numba import njit, int32, int64

from ..lowlevel.conpro import find_buffer_for_writing, mark_buffer_for_reading, mark_buffer_for_writing
from ..lowlevel.libc import read_block


def compile_cptask_read_data_into_buffers(bitsize):

    assert bitsize == 64
    nbytes = int64(bitsize // 8)

    @njit(nogil=True, locals=dict(
        ntodo=int32, errorcode=int32, offset=int32, skip=int32,
        wait=int64, wait_read=int64, wait_write=int64))
    def cptask_read_data_into_buffers(fd, inbuffers, incontrol, ininfos, outbuffers, outcontrol, outinfos):
        """
        Has to be run as a thread within a consumer producer task.
        Keep reading bytes into one of the outbuffers (cycling)
        until EOF is reached or an error occurs.
        Return 0 (EOF), or an error code (negative), corresponding to -os.errno.
        """
        # print("- running: cptask_read_fastq_into_linemarked_buffers; fd =", fd, "; output shapes: ", outbuffers.shape, outcontrol.shape, outinfos.shape)
        # assert (inbuffers is None) and (incontrol is None) and (ininfos is None)
        # if outbuffers.shape[0] < 2:
        #     raise ValueError("cptask_read_fastq_into_linemarked_buffers: must have 2 or more output buffers per worker")
        M, N = outinfos.shape
        assert N % 4 == 0

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
            nkeys = ntodo // nbytes
            nxt = nkeys * nbytes
            outcontrol[nactive, 7] = nkeys
            outcontrol[nactive, 6] = 1  # buffer type k-mer codes
            offset = ntodo - nxt
            assert offset < 8
        mark_buffer_for_writing(outcontrol, nactive, force=True)  # nothing left to read; re-use buffer
        return (wait_read, wait_write, errorcode)

    return cptask_read_data_into_buffers
