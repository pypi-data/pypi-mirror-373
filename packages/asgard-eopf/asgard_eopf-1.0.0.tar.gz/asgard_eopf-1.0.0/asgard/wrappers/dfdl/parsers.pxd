from libc.stdint cimport int8_t as int8_t
from libc.stdint cimport int16_t as int16_t
from libc.stdint cimport int32_t as int32_t
from libc.stdint cimport int64_t as int64_t
from libc.stdint cimport uint8_t as uint8_t
from libc.stdint cimport uint16_t as uint16_t
from libc.stdint cimport uint32_t as uint32_t
from libc.stdint cimport uint64_t as uint64_t


cdef extern from "parsers.h":
    void parse_be_bool(bint*, size_t, int64_t, uint32_t, PState*)
    void parse_be_double(double*, size_t, PState*)
    void parse_be_float(float*, size_t, PState*)
    void parse_be_int16(int16_t*, size_t, PState*)
    void parse_be_int32(int32_t*, size_t, PState*)
    void parse_be_int64(int64_t*, size_t, PState*)
    void parse_be_int8(int8_t*, size_t, PState*)
    void parse_be_uint16(uint16_t*, size_t, PState*)
    void parse_be_uint32(uint32_t*, size_t, PState*)
    void parse_be_uint64(uint64_t*, size_t, PState*)
    void parse_be_uint8(uint8_t*, size_t, PState*)
    void parse_le_bool(bint*, size_t, int64_t, uint32_t, PState*)
    void parse_le_double(double*, size_t, PState*)
    void parse_le_float(float*, size_t, PState*)
    void parse_le_int16(int16_t*, size_t, PState*)
    void parse_le_int32(int32_t*, size_t, PState*)
    void parse_le_int64(int64_t*, size_t, PState*)
    void parse_le_int8(int8_t*, size_t, PState*)
    void parse_le_uint16(uint16_t*, size_t, PState*)
    void parse_le_uint32(uint32_t*, size_t, PState*)
    void parse_le_uint64(uint64_t*, size_t, PState*)
    void parse_le_uint8(uint8_t*, size_t, PState*)
    void alloc_hexBinary(HexBinary*, size_t, PState*)
    void parse_hexBinary(HexBinary*, PState*)
    void parse_align_to(size_t, PState*)
    void parse_alignment_bits(size_t, PState*)
    void no_leftover_data(PState*)


