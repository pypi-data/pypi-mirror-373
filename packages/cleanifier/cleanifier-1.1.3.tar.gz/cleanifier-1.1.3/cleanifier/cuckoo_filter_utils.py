"""
Utilities, pointer and bit magic for cuckoo filters
"""

from math import log2
from numba import njit, uint8, uint16, uint32, uint64
import numba as nb
import numpy as np
from llvmlite import ir
from .mathutils import bitsfor
from .lowlevel.llvm import compile_cttz


def compute_masks(bits_per_slot, slots):
    mask1 = ('0' * (bits_per_slot - 1) + '1') * slots
    mask2 = ('1' + '0' * (bits_per_slot - 1)) * slots
    return uint64(int(mask1, 2)), uint64(int(mask2, 2))


def compute_fp_mask(bits_per_slot, fingerprint_bits, slots):
    fp_mask = uint64(0)
    for s in range(1, slots):
        fp_mask |= (s << (s * bits_per_slot + fingerprint_bits))
    return uint64(fp_mask)


def compute_choice_fp_mask(bits_per_slot, fingerprint_bits, slots):
    window_bits = bitsfor(slots)
    fp_mask = uint64(0)
    for s in range(0, slots):
        fp_mask |= (s << (s * bits_per_slot + fingerprint_bits))
        fp_mask |= 1 << (s * bits_per_slot + fingerprint_bits + window_bits)
    for s in range(0, slots):
        fp_mask |= (s << ((slots + s) * bits_per_slot + fingerprint_bits))
    return uint64(fp_mask)


def compute_choice_mask(bits_per_slot, fingerprint_bits, slots):
    fp_mask = uint64(0)
    for s in range(0, slots):
        fp_mask |= 1 << (s * bits_per_slot + fingerprint_bits)
    return uint64(fp_mask)


def compile_lookup(bits_per_slot, slots, windowed=True, choice=False):
    fingerprint_bits = uint64(bits_per_slot - int(log2(slots)) - 1 if windowed else bits_per_slot - 1)
    if choice:
        assert bits_per_slot * slots * 2 <= 64
        m1, m2 = compute_masks(bits_per_slot, 2 * slots)
        if windowed:
            fp_mask = compute_choice_fp_mask(bits_per_slot, fingerprint_bits, slots)
        else:
            fp_mask = compute_choice_mask(bits_per_slot, fingerprint_bits, slots)
    else:
        assert bits_per_slot * slots <= 64
        m1, m2 = compute_masks(bits_per_slot, slots)
        fp_mask = compute_fp_mask(bits_per_slot, fingerprint_bits, slots) if windowed else uint64(0)

    @njit(nogil=True)
    def haszero(x):
        return uint64(((x) - m1) & (~(x)) & m2)

    @njit(nogil=True)
    def hasvalue(window, fp):
        x = haszero(window ^ ((m1 * fp) | fp_mask))
        return x != 0

    return hasvalue


def compile_get_empty_slot(bits_per_slot, slots):
    assert bits_per_slot * slots <= 64
    count_trailing_zeros = compile_cttz('uint64')
    m1, m2 = compute_masks(bits_per_slot, slots)

    @njit(nogil=True)
    def haszero(x):
        return (((x) - m1) & (~(x)) & m2)

    @njit(nogil=True, locals=dict(x=uint64, slot=uint64))
    def get_empty_slot(window):
        x = haszero(window)
        slot = count_trailing_zeros(x) // bits_per_slot
        return slot

    return get_empty_slot


def compile_load_value(nbits):
    # fast version for multiples of 8 (cast byte counter)
    if nbits in [8, 16, 32, 64]:
        signatures = {8: uint8, 16: uint16, 32: uint32, 64: uint64}
        pointer = ir.IntType(nbits).as_pointer()
        int_type = signatures[nbits]

        @nb.extending.intrinsic
        def address_to_value(typingctx, src):
            """ returns the value stored at a given memory address """
            sig = int_type(src)
            def codegen(cgctx, builder, sig, args):
                ptr = builder.inttoptr(args[0], pointer)
                return builder.load(ptr)
            return sig, codegen

        @njit(nogil=True, locals=dict(address=uint64))
        def get_value(fltr, start):
            address = fltr.ctypes.data + (uint64(start) >> 3)
            return address_to_value(address)

        return get_value

    # slow version if nbits is not a multiple of 8
    elif 0 < nbits <= 64:
        padded_nbits = ((int(nbits) + 7) & (-8)) + 8
        int_type = uint64
        mask = ir.Constant(ir.IntType(64), int(nbits * '1', 2))
        finalcast = ir.IntType(64)
        if padded_nbits <= 64:
            cast = ir.IntType(64)
            pointer = ir.IntType(64).as_pointer()
        else:
            cast = ir.IntType(128)
            pointer = ir.IntType(128).as_pointer()

        @nb.extending.intrinsic
        def address_to_value(typingctx, address, offset):
            """ returns the value stored at a given memory address """
            sig = int_type(address, offset)
            def codegen(cgctx, builder, sig, args):
                ptr = builder.inttoptr(args[0], pointer)
                value = builder.load(ptr)
                shift = builder.zext(args[1], cast)
                value = builder.lshr(value, shift)
                value = builder.trunc(value, finalcast)
                return builder.and_(value, mask)
            return sig, codegen

        @njit(nogil=True, locals=dict(address=uint64, offset=uint64))
        def get_value(array, pos):
            address = array.ctypes.data + (uint64(pos) >> 3)
            return address_to_value(address, (uint64(pos) & 7))

        return get_value

    return None

def compile_store_value(nbits):
    # fast version for multiples of 8 (cast byte counter)
    if nbits in [8, 16, 32, 64]:
        pointer = ir.IntType(nbits).as_pointer()
        signatures = {8: uint8, 16: uint16, 32: uint32, 64: uint64}
        int_type = signatures[nbits]

        @nb.extending.intrinsic
        def store_value_at_address(typingctx, address, value):
            """returns the value stored at a given memory address """
            sig = nb.void(nb.types.uintp, int_type)
            def codegen(cgctx, builder, sig, args):
                ptr = builder.inttoptr(args[0], pointer)
                builder.store(args[1], ptr)
            return sig, codegen

        @njit(nogil=True, locals=dict(pos=uint64))
        def store_value(array, pos, value):
            pos = array.ctypes.data + (uint64(pos) >> 3)
            store_value_at_address(pos, value)

        return store_value

    # slow version if nbits is not a multiple of 8
    elif 0 < nbits <= 64:
        padded_nbits = ((int(nbits) + 7) & (-8)) + 8
        if padded_nbits <= 64:
            cast = ir.IntType(64)
            pointer = ir.IntType(64).as_pointer()
            ones = ir.Constant(ir.IntType(64), int(2**64 - 1))
            mask = ir.Constant(ir.IntType(64), 2**int(nbits) - 1)
        elif padded_nbits <= 128:
            cast = ir.IntType(128)
            pointer = ir.IntType(128).as_pointer()
            ones = ir.Constant(ir.IntType(128), 2**128 - 1)
            mask = ir.Constant(ir.IntType(128), 2**int(nbits) - 1)

        @nb.extending.intrinsic
        def store_value_at_address(typingctx, address, value, shift):
            """returns the value stored at a given memory address """
            sig = nb.void(nb.types.uintp, address, value, shift)
            def codegen(cgctx, builder, sig, args):
                ptr = builder.inttoptr(args[0], pointer)
                value = builder.load(ptr)
                zero_mask = builder.shl(mask, builder.zext(args[2], cast))
                zero_mask = builder.xor(zero_mask, ones)
                value = builder.and_(value, zero_mask)
                insert = builder.shl(args[1], args[2])
                value = builder.or_(value, builder.zext(insert, cast))
                builder.store(value, ptr)
            return sig, codegen

        @njit(nogil=True, locals=dict(address=uint64, shift=uint64, value=uint64))
        def store_value(array, pos, value):
            address = array.ctypes.data + (uint64(pos) >> 3)
            shift = uint64(pos) & 7
            store_value_at_address(address, value, shift)

        return store_value

    raise NotImplementedError("Only storing values <= 64 bits supported")
