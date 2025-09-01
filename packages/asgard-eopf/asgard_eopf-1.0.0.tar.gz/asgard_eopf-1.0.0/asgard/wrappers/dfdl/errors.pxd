from libc.stdint cimport int64_t as int64_t
from libc.stdint cimport uint8_t as uint8_t
from libc.stdio cimport FILE as FILE


cdef extern from "errors.h":
    enum ErrorCode:
        ERR_ARRAY_BOUNDS = 0
        ERR_CHOICE_KEY = 1
        ERR_HEXBINARY_ALLOC = 2
        ERR_LEFTOVER_DATA = 3
        ERR_PARSE_BOOL = 4
        ERR_RESTR_ENUM = 5
        ERR_RESTR_FIXED = 6
        ERR_RESTR_RANGE = 7
        ERR_STREAM_EOF = 8
        ERR_STREAM_ERROR = 9
        ERR__NUM_CODES = 10
    enum ErrorField:
        FIELD_C = 0
        FIELD_D64 = 1
        FIELD_S = 2
        FIELD_S_ON_STDOUT = 3
        FIELD__NO_ARGS = 4
    struct ErrorLookup:
        uint8_t code
        const char* message
        ErrorField field
    union pxdgen_anon_Error_0:
        int c
        int64_t d64
        const char* s
    struct Error:
        uint8_t code
        pxdgen_anon_Error_0 arg
    enum Limits:
        LIMIT_DIAGNOSTICS = 100
        LIMIT_NAME_LENGTH = 9999
    struct Diagnostics:
        Error array[100]
        size_t length
    Error* eof_or_error(FILE*)
    Diagnostics* get_diagnostics()
    bint add_diagnostic(Diagnostics*, Error*)
    void print_diagnostics(Diagnostics*)
    void continue_or_exit(Error*)
    ctypedef ErrorLookup* cli_error_lookup_t(uint8_t)
    cli_error_lookup_t* cli_error_lookup


