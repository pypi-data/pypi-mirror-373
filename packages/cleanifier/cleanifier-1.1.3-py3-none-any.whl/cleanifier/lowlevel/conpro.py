"""
ConsumerProducer:
a "class" that implements a ConsumerProducer, i.e.,
an entity that consumes data and/or produces data.
The support offered by this class is for the case
where the data serially comes from and goes into buffers.
If the data comes from or goes to something else (a file, a hash table, etc) on one side,
there are no input resp. output buffers, and the user is expected to handle that by herself.

General setting
(Input) -> {ConsumerProducer1} -> [Data buffers] -> {ConsumerProducer2} -> [Data buffers] -> {ConsumerProducer3} -> (Output)
Legend: ( ) external input/output; [ ] buffers; { } consumer/producer processes

Concrete Examples:
(FASTQ files) -> {FastQDispatch} -> [subkeys, values] -> {Inserter} -> (Sub-Hashtables)
                 consume FASTQ files                     insert subkeys
                 produce canonical codes                 and values
                 compute subkeys and values              into subtables

(FASTQ files) -> {Reader} -> [FASTQ bytes, linemarks] -> {KmerEncoder} -> [Subkeys,Values] -> {Inserter} -> (Sub-Hashtables)
                 consume FASTQ chunk                     compute kmers,                       insert subkeys
                 compute linemarks                       subtable hash functions,             and values
                                                         subkeys (and values)                 into subtables

Control buffer layout
control[i, 0]: buffer status
control[i, 1]: set to nonzero on error
control[i, 6]: Contained data, 0 is sequence data and 1 indicates k-mers
control[i, 7]: k-mers in input buffer i

"""


import os
import sys
from enum import Enum, auto
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED

import numpy as np
from numba import njit, int64, uint64

from . import debug
from .llvm import (
    compile_pause,
    compile_compare_xchange,
    compile_volatile_load,
    compile_volatile_store,
    )
from .aligned_arrays import aligned_zeros

vload = compile_volatile_load("uint64")
vstore = compile_volatile_store("uint64")
cmpxchg = compile_compare_xchange("uint64")
cpu_pause = compile_pause()

# ######################################################################


class CPInputMode(Enum):
    DEFAULT = auto()
    ONE_TO_ONE = auto()
    GATHER = auto()


class ConsumerProducer:
    """
    A ConsumerProducer class.
    name: name of this instance (used as thread_name_prefix)
    tasks: list of pairs or triples [(func1, args1, kwargs1), (func2, args2, kwargs2), ...];
      each args is a tuple of arguments, each kwargs is a dict or keyword arguments.
      Each function given here must satisfy certain parameter and return conventions:
      1. It must have been decorated with @consumer_producer_function.
      2. It must specify the following argument list:
         func(*fargs, *buffers)
      3. It must return either a single integer or a tuple that ends with an integer.
         If that integer is negative, this indicates an error, which is passed on.
         In this way, each task can succeed or report a different single task-specific error code.
    """
    def __init__(self, *,
                 name='',  # name of this instance (used as thread_name_prefix)
                 tasks=[],
                 input=None,
                 input_mode=CPInputMode.DEFAULT,
                 nworkers=0,
                 noutbuffers_per_worker=3,  # total number of output buffers per worker
                 specific_outbuffers_per_worker=False,
                 datatype=np.uint64,
                 dataitems_per_buffer=2**16,
                 dataitemsize=1,
                 infotype=np.int64,
                 infoitems_per_buffer=0,
                 infoitemsize=1,
                 ):

        CPUCORES = os.cpu_count() or 2
        MAXWORKERS = max(CPUCORES - 1, 1)
        debugprint0, debugprint1, debugprint2 = debug.debugprint

        ntasks = len(tasks)
        if ntasks == 0:
            raise ValueError("ConsumerProducer: no tasks.")

        if input is None:
            inbuffers = incontrol = ininfos = None
            if input_mode != CPInputMode.DEFAULT:
                raise ValueError(f"ConsumerProducer '{name}': With {input=}, only DEFAULT input mode is possible.")
        else:
            inbuffers, incontrol, ininfos = input.outbuffers, input.outcontrol, input.outinfos

        if isinstance(input_mode, tuple):
            input_mode, input_mode_data = input_mode
        else:
            input_mode_data = None

        # handle different input modes
        gathering = 0
        if input_mode == CPInputMode.ONE_TO_ONE:
            if inbuffers.ndim != 3:
                raise ValueError(f"ConsumerProducer '{name}': With ONE_TO_ONE input, must have specific input buffers.")
            if nworkers == 0:
                nworkers = input.nworkers
                debugprint1(f"- ConsumerProducer '{name}': Set {nworkers=} from input '{input.name}'")
                if ntasks != nworkers:
                    if ntasks != 1:
                        raise ValueError(f"ConsumerProducer '{name}': Have ONE_TO_ONE input, {nworkers=}, but {ntasks} tasks")
                    debugprint1(f"- ConsumerProducer '{name}': Copying single task {nworkers=} times.")
                    tasks = tasks * nworkers
            if nworkers != inbuffers.shape[0]:
                raise ValueError(f"ConsumerProducer '{name}': For ONE_TO_ONE input, we have {nworkers=}, but {inbuffers.shape=}")
        elif input_mode == CPInputMode.GATHER:
            if nworkers == 0:
                nworkers = ntasks
            if nworkers != ntasks:
                raise ValueError(f"ConsumerProducer '{name}': With GATHER input, must have {nworkers=} == {ntasks=}")
            if inbuffers.ndim != 2:
                raise ValueError(f"ConsumerProducer '{name}': With GATHER input, must not have specific input buffers")
            if not isinstance(input_mode_data, int):
                raise TypeError(f"ConsumerProducer '{name}': With GATHER input, specify HOW MANY buffers to gather for each worker")
            gathering = int(input_mode_data)
            ninbuffers = inbuffers.shape[0]
            if nworkers * gathering != ninbuffers:
                raise ValueError(f"ConsumerProducer '{name}': With GATHER input, {nworkers=} * {gathering=} must equal {ninbuffers=}, but does not.")
            if ntasks != nworkers:
                raise ValueError(f"ConsumerProducer '{name}': With GATHER input, {nworkers=} must equal {ntasks=}, but does not.")
        else:
            # DEFAULT input mode; input can be None, or specific!
            if inbuffers is not None and inbuffers.ndim == 3:
                ishp = inbuffers.shape
                inb = ishp[0] * ishp[1]
                inbuffers = inbuffers.reshape(inb, ishp[2])
                incontrol = incontrol.reshape(inb, -1)
                ininfos = ininfos.reshape(inb, -1)
                debugprint1(f"- ConsumerProducer '{name}': re-shaping input buffers from {ishp} to {inbuffers.shape}.")
            if nworkers <= 0:
                nworkers = max(min(MAXWORKERS, ntasks), 1)
            else:
                nworkers = max(min(nworkers, ntasks), 1)
            if nworkers > MAXWORKERS:
                debugprint0(f"Error: ConsumerProducer '{name}': {nworkers=} exceeds {MAXWORKERS=} for your system or process")
                sys.exit(1)

        datalen = dataitemsize * dataitems_per_buffer
        infolen = infoitemsize * infoitems_per_buffer
        nbytes_per_buffer = (datalen * np.dtype(datatype).itemsize
                            + infolen * np.dtype(infotype).itemsize)  # noqa: W503
        nbuffers = int(round(nworkers * noutbuffers_per_worker))
        nbytes = nbytes_per_buffer * nbuffers
        if nbytes > (3 * 2**30):
            raise ValueError(f"ConsumerProducer '{name}': {nbuffers} buffers need over 3 GiB ({nbytes / (2**23):.3f} GiB)")

        if not specific_outbuffers_per_worker:
            outbuffers = aligned_zeros((nbuffers, datalen), dtype=datatype, autogrow=True)
            outcontrol = aligned_zeros((nbuffers, 8))  # 8 control uint64s (512 bits) per buffer
            outinfos = aligned_zeros((nbuffers, infolen), dtype=infotype, autogrow=True)
        else:
            if not isinstance(noutbuffers_per_worker, int):
                raise TypeError(f"ConsumerProducer '{name}': {noutbuffers_per_worker=} must be an integer if {specific_outbuffers_per_worker=}.")
            outbuffers = aligned_zeros((nworkers, noutbuffers_per_worker, datalen), dtype=datatype, autogrow=True)
            outcontrol = aligned_zeros((nworkers, noutbuffers_per_worker, 8))  # 8 control uint64s (512 bits) per buffer
            outinfos = aligned_zeros((nworkers, noutbuffers_per_worker, infolen), dtype=infotype, autogrow=True)

        self.name = name
        self.tasks = tasks
        self._funcs = [task[0] for task in tasks]
        self._args = [tuple(task[1:]) for task in tasks]
        self.nworkers = nworkers
        self.input = input
        self.input_mode = input_mode
        self.inbuffers = inbuffers
        self.incontrol = incontrol
        self.ininfos = ininfos
        self.specific_inbuffers_per_worker = inbuffers is not None and inbuffers.ndim == 3
        self.gathering = gathering
        self.noutbuffers_per_worker = noutbuffers_per_worker
        self.specific_outbuffers_per_worker = specific_outbuffers_per_worker
        self.datatype = datatype
        self.dataitems_per_buffer = dataitems_per_buffer
        self.dataitemsize = dataitemsize
        self.infotype = infotype
        self.infoitems_per_buffer = infoitems_per_buffer
        self.infoitemsize = infoitemsize
        self.outbuffers = outbuffers
        self.outcontrol = outcontrol
        self.outinfos = outinfos
        self.results = [None] * ntasks
        self.wait_read = [0] * nworkers
        self.wait_write = [0] * nworkers

    def __repr__(self):
        r = f'ConsumerProducer(name={self.name}, '
        R = []
        for attr in self.__dir__():
            if attr.startswith("_") or attr == "name":
                continue
            val = getattr(self, attr)
            val = f"ndarray(shape={val.shape}, dtype={val.dtype})" if isinstance(val, np.ndarray) else val
            R.append(f"{attr}={val}")
        return r + ", ".join(R) + ")"


# This is the new and only way to run one or several ConsumerProducer(s) at once.
def run_cps(*cps):
    """
    Run all of the given ConsumerProducers in different threads.
    Return when everything is done.
    Return True if all tasks in all ConsumerProducers were successful, False othewise.
    """
    debugprint0, debugprint1, debugprint2 = debug.debugprint
    cptup = tuple(cps)
    N = len(cptup)
    ntotalworkers = sum(cp.nworkers for cp in cptup)
    ntotaltasks = sum(len(cp.results) for cp in cptup)
    for cp in cptup:
        debugprint1(f"- run_cps: starting task group {cp.name} with ntasks={len(cp._funcs)}, nworkers={cp.nworkers}")
    debugprint1(f"- run_cps: sums: {N} task groups, {ntotalworkers} threads for {ntotaltasks} tasks")
    Lnstarted = [0] * N
    Lndone = [0] * N

    with ThreadPoolExecutor(max_workers=ntotalworkers, thread_name_prefix="run_cps") as ex:
        actives = []
        actdata = []

        # initially, start a number of workers in every group
        for group in range(N):
            gntask = 0
            cp = cptup[group]
            nworkers = cp.nworkers
            specific_inbuffers_per_worker = cp.specific_inbuffers_per_worker
            gathering = cp.gathering
            inbuffers, incontrol, ininfos = cp.inbuffers, cp.incontrol, cp.ininfos
            specific_outbuffers_per_worker = cp.specific_outbuffers_per_worker
            outbuffers, outcontrol, outinfos = cp.outbuffers, cp.outcontrol, cp.outinfos
            funcs = cp._funcs
            args = cp._args
            for i in range(nworkers):
                if specific_inbuffers_per_worker:
                    assert gathering == 0, f"{gathering=} although we have specific input buffers (impossible!)"
                    ib, ic, ii = inbuffers[i], incontrol[i], ininfos[i]
                else:
                    if gathering:
                        jfrom, jto = i * gathering, (i + 1) * gathering
                        ib = inbuffers[jfrom:jto, :]
                        ic = incontrol[jfrom:jto, :]
                        ii = ininfos[jfrom:jto, :]
                    else:
                        ib, ic, ii = inbuffers, incontrol, ininfos
                if specific_outbuffers_per_worker:
                    ob, oc, oi = outbuffers[i], outcontrol[i], outinfos[i]
                else:
                    ob, oc, oi = outbuffers, outcontrol, outinfos
                actives.append(ex.submit(
                    funcs[gntask], *args[gntask],
                    ib, ic, ii, ob, oc, oi,
                    ))
                actdata.append((group, gntask, gntask))
                gntask += 1
            Lnstarted[group] = gntask

        # as jobs finish, start the next job from the same group in the free thread
        ntotaldone = 0
        nfailed = 0
        while True:
            finished_set, running_set = wait(actives, return_when=FIRST_COMPLETED)
            new_jobs = []
            new_data = []
            for done in finished_set:
                ntotaldone += 1
                didx = actives.index(done)  # must be there!
                dgrp, dtsk, dthread = actdata[didx]
                dcp = cptup[dgrp]
                name = dcp.name
                Lndone[dgrp] += 1
                try:
                    R = done.result()  # is an int (code) or tuple (..., code)
                except Exception as exc:
                    ex.shutdown(wait=False, cancel_futures=True)
                    debugprint0(f"- ConsumerProducer '{name}': Task {dtsk} in thread {dthread}, raised an Exception: '{exc}' // '{done.exception()}'")
                    R = (0, 0, -1)  # dummy result
                assert isinstance(R, tuple) and len(R) >= 3, f"- ConsumerProducer '{name}': {R=} not a tuple of length >=3"
                dcp.wait_read[dthread] += R[-3]
                dcp.wait_write[dthread] += R[-2]
                code = R[-1]
                dcp.results[dtsk] = R[:-3]
                assert isinstance(code, int), f"{type(code)=}, {code=}"
                if code < 0:
                    debugprint0(f"- ConsumerProducer '{name}': Task {dtsk} in thread {dthread} FAILED with error {-code}.")
                    nfailed += 1
                    break
                debugprint1(f"- ConsumerProducer '{name}': Task {dtsk} in thread {dthread} finished. Extended result is {R}.")

                # so far, we never failed; dgrp is the group where a job had finished.
                gntask = Lnstarted[dgrp]
                gntasks = len(dcp.results)
                if gntask < gntasks:
                    debugprint1(f"- ConsumerProducer '{name}': Submitting next task #{gntask} to thread {dthread}.")
                    if dcp.specific_inbuffers_per_worker:
                        ib, ic, ii = dcp.inbuffers[dthread], dcp.incontrol[dthread], dcp.ininfos[dthread]
                    else:
                        ib, ic, ii = dcp.inbuffers, dcp.incontrol, dcp.ininfos
                    if dcp.specific_outbuffers_per_worker:
                        ob, oc, oi = dcp.outbuffers[dthread], dcp.outcontrol[dthread], dcp.outinfos[dthread]
                    else:
                        ob, oc, oi = dcp.outbuffers, dcp.outcontrol, dcp.outinfos
                    new_jobs.append(ex.submit(
                        dcp._funcs[gntask], *dcp._args[gntask],
                        ib, ic, ii, ob, oc, oi,
                        ))
                    new_data.append((dgrp, gntask, dthread))
                    Lnstarted[dgrp] += 1
                else:
                    debugprint2(f"- ConsumerProducer '{name}': A task has finished; no further tasks to submit.")
                    if Lndone[dgrp] >= gntasks:
                        debugprint1(f"- ConsumerProducer '{name}': All tasks have finished in this group.")
                        outcontrol = dcp.outcontrol
                        specific_outbuffers_per_worker = dcp.specific_outbuffers_per_worker
                        nworkers = dcp.nworkers
                        if outcontrol is not None:
                            if specific_outbuffers_per_worker:
                                assert outcontrol.ndim == 3
                                for i in range(nworkers):
                                    mark_my_buffers_finished(outcontrol[i])
                            else:
                                assert outcontrol.ndim == 2
                                mark_my_buffers_finished(outcontrol)
                        debugprint2(f"- ConsumerProducer '{name}': Marked all buffers as finished.")
            # 'for done in finished_set' loop ends here.
            if (ntotaldone >= ntotaltasks) or (nfailed > 0):
                break
            running = list(running_set)
            rundata = [actdata[actives.index(r)] for r in running]
            actives = running + new_jobs
            actdata = rundata + new_data

        # out of the infinite while loop, but still within the thread pool executor
        if nfailed > 0:
            debugprint0(f"- run_cps: exiting because of failures or exceptions: {nfailed=}")
            for group in range(N):
                cp = cptup[group]
                incontrol = cp.incontrol
                if incontrol is not None:
                    mark_my_buffers_failed(incontrol)
                outcontrol = cp.outcontrol
                if outcontrol is not None:
                    mark_my_buffers_failed(outcontrol)
            debugprint1(f"- run_cps: All buffers marked as finished.")

    # all done
    debugprint1("- run_cps: done; ThreadPool closed")
    assert (ntotaldone == ntotaltasks) or (nfailed > 0), f"- Oops. All done, {ntotaltasks=}, but {ntotaldone=}, {nfailed=}."
    return nfailed


# ######################## BUFFER CONTROL LOGIC ###############################


def compile_buffer_logic():
    _BC_READY_TO_WRITE, _BC_READY_TO_READ, \
        _BC_WRITING, _BC_READING, \
        _BC_FINISHED = map(uint64, range(5))
    debugprint0, debugprint1, debugprint2 = debug.debugprint

    @njit(nogil=True, locals=dict(
        i=int64, state=uint64, waited=int64, delay=int64, error=uint64))
    def _find_buffer(control, current_state, new_state, last=-1):
        """
        Find a buffer with state `current_state`,
        set its state to `new state`,
        and return a pair of its index and wait time.
        Alternatively, if all states are _BC_FINISHED,
        return -1 and wait time.
        Alternatively, on error, return -2 and wait time.
        Otherwise, wait and try again.
        """
        n, _ = control.shape
        delay = waited = 0
        i = last
        while True:

            finished = 0
            for j in range(n):
                i += 1
                i -= n * (i >= n)
                state = vload(control[i], 0)
                if state == uint64(current_state):
                    if cmpxchg(control[i], 0, state, uint64(new_state)):
                        return (i, waited)
                elif state == uint64(_BC_FINISHED):
                    finished += 1
            if finished == n:
                return (int64(-1), waited)
            error = 0
            for j in range(n):
                error |= vload(control[j], 1)
            if error:
                return (int64(-2), waited)
            delay += 2
            waited += delay * (last >= 0)
            for _ in range(delay):
                cpu_pause()

    @njit(nogil=True)
    def find_buffer_for_writing(control, last=-1):
        return _find_buffer(control, _BC_READY_TO_WRITE, _BC_WRITING, last=last)

    @njit(nogil=True)
    def find_buffer_for_reading(control, last=-1):
        return _find_buffer(control, _BC_READY_TO_READ, _BC_READING, last=last)

    @njit(nogil=True, locals=dict(state=uint64))
    def mark_buffer_for_reading(control, nactive):
        state = vload(control[nactive], 0)
        if state != uint64(_BC_WRITING):
            debugprint0("- ERROR in mark_buffer_for_reading: state was not _BC_WRITING", state)
            assert state == _BC_WRITING
        vstore(control[nactive], 0, _BC_READY_TO_READ)

    @njit(nogil=True, locals=dict(state=uint64))
    def mark_buffer_for_writing(control, nactive, force=False):
        if not force:
            state = vload(control[nactive], 0)
            if state != uint64(_BC_READING):
                debugprint0("- ERROR in mark_buffer_for_writing: state was not _BC_reading", state)
                assert state == _BC_READING
        vstore(control[nactive], 0, _BC_READY_TO_WRITE)

    @njit(nogil=True)
    def mark_my_buffers_failed(control):
        n = control.shape[0]
        for i in range(n):
            vstore(control[i], 1, uint64(1))

    @njit(nogil=True, locals=dict(
        state=uint64, error=uint64, waited=int64, delay=int64))
    def mark_my_buffers_finished(control):
        """return wait cycles"""
        waited = 0
        delay = 8
        n = control.shape[0]
        while True:
            finished = 0
            for i in range(n):
                state = vload(control[i], 0)
                error = vload(control[i], 1)
                if state == _BC_WRITING or state == _BC_READY_TO_WRITE:
                    vstore(control[i], 0, _BC_FINISHED)
                    finished += 1
                    continue
                if (state == _BC_FINISHED) or error:
                    finished += 1
                    continue
            if finished == n:
                break
            delay += 2
            waited += delay
            for _ in range(delay):
                cpu_pause()
        return waited

    def diagnose_wait_times(*cps):
        debugprint0, debugprint1, debugprint2 = debug.debugprint
        total = 0
        cptup = tuple(cps)
        for cp in cptup:
            name = cp.name
            wr, ww = cp.wait_read, cp.wait_write
            sr, sw = sum(wr), sum(ww)
            debugprint1(f"- wait cycles for cptask '{name}': read: {(sr / 1e6):.3f} M;  write: {(sw / 1e6):.3f} M")
            for i, wwr in enumerate(wr):
                debugprint2(f"    - read wait thread {i}: {wwr}")
            for i, www in enumerate(ww):
                debugprint2(f"    - write wait thread {i}: {www}")
            total += sr + sw
        debugprint1(f"- wait cycles in total: {(total / 1e6):.3f} M")

    return find_buffer_for_reading, find_buffer_for_writing, \
        mark_buffer_for_reading, mark_buffer_for_writing, \
        mark_my_buffers_failed, mark_my_buffers_finished, \
        diagnose_wait_times


find_buffer_for_reading, find_buffer_for_writing, \
    mark_buffer_for_reading, mark_buffer_for_writing, \
    mark_my_buffers_failed, mark_my_buffers_finished, \
    diagnose_wait_times = compile_buffer_logic()
