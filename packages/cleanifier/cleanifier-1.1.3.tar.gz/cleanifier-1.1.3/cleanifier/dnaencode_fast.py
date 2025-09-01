"""
Fast DNA encoding and computation of the reverse complement A=00, C=01, T=10, G=11, U=10
Other characters are not treated correctly, except N=7>3 and n = 6>3
"""

from numba import njit, uint64
import numpy as np
from .mask import Mask

U64_MINUSONE = uint64(np.iinfo(np.uint64).max)


@njit(nogil=True)
def quick_dna_to_2bits(x):
    for i in range(len(x)):
        x[i] = (x[i] >> 1) & 7


@njit(nogil=True)
def dna_to_2bits(x, y):
    for i in range(len(x)):
        y[i] = (x[i] >> 1) & 7


# no need to njit!
def _get_table_2bits_to_dna():
    b = np.full(256, 35, dtype=np.uint8)  # fill with b'#'
    b[0] = 65
    b[1] = 67
    b[2] = 84
    b[3] = 71
    b[6] = 78
    b[7] = 78
    return b


_TABLE_2BITS_TO_DNA = _get_table_2bits_to_dna()


@njit(nogil=True)
def twobits_to_dna_inplace(buf, start=0, end=0):
    if end <= 0:
        end = len(buf) - end
    for i in range(start, end):
        buf[i] = _TABLE_2BITS_TO_DNA[buf[i]]


_TABLE_BITS_TO_DNASTR = ["A", "C", "T", "G"]


def qcode_to_dnastr(qcode, q, table=_TABLE_BITS_TO_DNASTR):
    qc = int(qcode)
    return "".join([table[((qc >> (2 * (q - i - 1))) & 3)] for i in range(q)])


def compile_revcomp_and_canonical_code(q, rcmode):
    """
    return pair of functions (revcomp_code_q, canonical_code_q)
    specialized for q-gram codes for the given value of q.
    It is expected that LLVM optimization does loop unrolling.
    """

    mask = uint64(int(q * '10', 2))
    shift = uint64(64 - 2 * q)

    @njit(nogil=True, locals=dict(value=uint64))
    def reverse_in_pairs(value):
        value = ((value & 0x3333333333333333) << 2) | ((value & 0xCCCCCCCCCCCCCCCC) >> 2)
        value = ((value & 0x0F0F0F0F0F0F0F0F) << 4) | ((value >> 4) & 0x0F0F0F0F0F0F0F0F)
        value = ((value & 0x00FF00FF00FF00FF) << 8) | ((value >> 8) & 0x00FF00FF00FF00FF)
        value = ((value & 0x0000FFFF0000FFFF) << 16) | ((value >> 16) & 0x0000FFFF0000FFFF)
        value = (value << 32) | (value >> 32)
        return value

    @njit(nogil=True, locals=dict(value=uint64))
    def _rc(value):
        value ^= mask
        value = reverse_in_pairs(value)
        return value >> shift

    if rcmode == "min":
        @njit(nogil=True, locals=dict(
            code=uint64, rc=uint64))
        def _cc(code):
            rc = _rc(code)
            return code if code <= rc else rc
    elif rcmode == "max":
        @njit(nogil=True, locals=dict(
            code=uint64, rc=uint64))
        def _cc(code):
            rc = _rc(code)
            return code if code >= rc else rc
    elif rcmode == "r":
        @njit(nogil=True, locals=dict(
            code=uint64, rc=uint64))
        def _cc(code):
            rc = _rc(code)
            return rc
    else:  # 'f', 'both', ...
        @njit(nogil=True, locals=dict(
            code=uint64, rc=uint64))
        def _cc(code):
            return code

    return _rc, _cc


# translation of a DNA buffer into codes


def compile_twobit_to_codes(tmask, rcmode, invalid=U64_MINUSONE):
    # tmask should be a mask tuple, but might be an int in some cases
    if isinstance(tmask, int):
        k = w = tmask  # be safe here
        tmask = tuple(range(k))
    elif isinstance(tmask, Mask):
        k = tmask.k
        w = tmask.w
        tmask = tmask.tuple
    elif type(tmask) is tuple:
        k, w = len(tmask), tmask[-1] + 1
    else:
        raise ValueError(f"mask type {type(tmask)} is not supported.")
    _, ccc = compile_revcomp_and_canonical_code(k, rcmode)

    @njit(nogil=True, locals=dict(code=uint64))
    def twobit_to_codes(seq, out, start=0, n=-1):
        """write n (or all) canonical k-mer codes from seq[start...] into out buffer"""
        if n == -1:
            n = len(seq) - w + 1 - start
        for i in range(start, start + n):
            code = 0
            for j in tmask:
                c = seq[i + j]
                if c >= 4:
                    out[i - start] = uint64(invalid)
                    break
                code = (code << 2) | c
            else:
                code = ccc(code)
                out[i - start] = code

    @njit(nogil=True, locals=dict(code=uint64))
    def twobit_to_code(seq, start=0):
        """return a single canonical code at seq[start...]"""
        code = 0
        for j in tmask:
            c = seq[start + j]
            if c >= 4:
                return uint64(invalid)
            code = (code << 2) | c
        else:
            code = ccc(code)
            return code

    return twobit_to_codes, twobit_to_code
