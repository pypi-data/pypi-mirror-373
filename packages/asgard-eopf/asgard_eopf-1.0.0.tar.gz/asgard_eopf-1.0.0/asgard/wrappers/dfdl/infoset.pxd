cimport errors as dfdl_err
from libc.stdint cimport uint8_t as uint8_t
from libc.stdio cimport FILE as FILE


cdef extern from "infoset.h":
    ctypedef void (*ERDParseSelf)(InfosetBase*, PState*)
    ctypedef void (*ERDUnparseSelf)(InfosetBase*, UState*)
    ctypedef dfdl_err.Error* (*InitChoiceRD)(InfosetBase*)
    ctypedef size_t (*GetArraySize)(InfosetBase*)
    ctypedef dfdl_err.Error* (*VisitStartDocument)(VisitEventHandler*)
    ctypedef dfdl_err.Error* (*VisitEndDocument)(VisitEventHandler*)
    ctypedef dfdl_err.Error* (*VisitStartComplex)(VisitEventHandler*, InfosetBase*)
    ctypedef dfdl_err.Error* (*VisitEndComplex)(VisitEventHandler*, InfosetBase*)
    ctypedef dfdl_err.Error* (*VisitSimpleElem)(VisitEventHandler*, ERD*, const void*)
    struct NamedQName:
        const char* prefix
        const char* local
        const char* ns
    enum TypeCode:
        ARRAY = 0
        CHOICE = 1
        COMPLEX = 2
        PRIMITIVE_BOOLEAN = 3
        PRIMITIVE_DOUBLE = 4
        PRIMITIVE_FLOAT = 5
        PRIMITIVE_HEXBINARY = 6
        PRIMITIVE_INT16 = 7
        PRIMITIVE_INT32 = 8
        PRIMITIVE_INT64 = 9
        PRIMITIVE_INT8 = 10
        PRIMITIVE_UINT16 = 11
        PRIMITIVE_UINT32 = 12
        PRIMITIVE_UINT64 = 13
        PRIMITIVE_UINT8 = 14
    union pxdgen_anon_ERD_0:
        InitChoiceRD initChoice
        GetArraySize getArraySize
    struct ERD:
        NamedQName namedQName
        TypeCode typeCode
        size_t numChildren
        size_t* childrenOffsets
        ERD** childrenERDs
        ERDParseSelf parseSelf
        ERDUnparseSelf unparseSelf
    struct HexBinary:
        uint8_t* array
        size_t lengthInBytes
        bint dynamic
    struct InfosetBase:
        ERD* erd
        InfosetBase* parent
    struct ParserOrUnparserState:
        FILE* stream
        size_t bitPos0b
        dfdl_err.Diagnostics* diagnostics
        dfdl_err.Error* error
    struct PState:
        ParserOrUnparserState pu
        uint8_t unreadBits
        uint8_t numUnreadBits
    struct UState:
        ParserOrUnparserState pu
        uint8_t unwritBits
        uint8_t numUnwritBits
    struct VisitEventHandler:
        VisitStartDocument visitStartDocument
        VisitEndDocument visitEndDocument
        VisitStartComplex visitStartComplex
        VisitEndComplex visitEndComplex
        VisitSimpleElem visitSimpleElem
    const char* get_erd_name(ERD*)
    const char* get_erd_xmlns(ERD*)
    const char* get_erd_ns(ERD*)
    InfosetBase* get_infoset(bint)
    void parse_data(InfosetBase*, PState*)
    void unparse_infoset(InfosetBase*, UState*)
    dfdl_err.Error* walk_infoset(VisitEventHandler*, InfosetBase*)
    const int packet_size



