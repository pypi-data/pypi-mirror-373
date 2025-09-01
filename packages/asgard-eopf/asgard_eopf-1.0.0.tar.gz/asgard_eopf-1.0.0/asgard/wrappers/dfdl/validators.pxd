from libc.stdint cimport int64_t as int64_t


cdef extern from "validators.h":
    void validate_array_bounds(const char*, size_t, size_t, size_t, ParserOrUnparserState*)
    void validate_fixed_attribute(bint, const char*, ParserOrUnparserState*)
    void validate_floatpt_enumeration(double, size_t, double[], const char*, ParserOrUnparserState*)
    void validate_hexbinary_enumeration(HexBinary*, size_t, HexBinary[], const char*, ParserOrUnparserState*)
    void validate_integer_enumeration(int64_t, size_t, int64_t[], const char*, ParserOrUnparserState*)
    void validate_schema_range(bint, const char*, ParserOrUnparserState*)


