from libc.stdint cimport int8_t as int8_t
from libc.stdint cimport int16_t as int16_t
from libc.stdint cimport int32_t as int32_t
from libc.stdint cimport int64_t as int64_t
from libc.stdint cimport uint8_t as uint8_t
from libc.stdint cimport uint16_t as uint16_t
from libc.stdint cimport uint32_t as uint32_t
from libc.stdint cimport uint64_t as uint64_t


cdef extern from "unparsers.h":
    void unparse_be_bool(bint, size_t, uint32_t, uint32_t, UState*)
    void unparse_be_double(double, size_t, UState*)
    void unparse_be_float(float, size_t, UState*)
    void unparse_be_int16(int16_t, size_t, UState*)
    void unparse_be_int32(int32_t, size_t, UState*)
    void unparse_be_int64(int64_t, size_t, UState*)
    void unparse_be_int8(int8_t, size_t, UState*)
    void unparse_be_uint16(uint16_t, size_t, UState*)
    void unparse_be_uint32(uint32_t, size_t, UState*)
    void unparse_be_uint64(uint64_t, size_t, UState*)
    void unparse_be_uint8(uint8_t, size_t, UState*)
    void unparse_le_bool(bint, size_t, uint32_t, uint32_t, UState*)
    void unparse_le_double(double, size_t, UState*)
    void unparse_le_float(float, size_t, UState*)
    void unparse_le_int16(int16_t, size_t, UState*)
    void unparse_le_int32(int32_t, size_t, UState*)
    void unparse_le_int64(int64_t, size_t, UState*)
    void unparse_le_int8(int8_t, size_t, UState*)
    void unparse_le_uint16(uint16_t, size_t, UState*)
    void unparse_le_uint32(uint32_t, size_t, UState*)
    void unparse_le_uint64(uint64_t, size_t, UState*)
    void unparse_le_uint8(uint8_t, size_t, UState*)
    void unparse_hexBinary(HexBinary, UState*)
    void unparse_align_to(size_t, uint8_t, UState*)
    void unparse_alignment_bits(size_t, uint8_t, UState*)
    void flush_fragment_byte(uint8_t, UState*)


