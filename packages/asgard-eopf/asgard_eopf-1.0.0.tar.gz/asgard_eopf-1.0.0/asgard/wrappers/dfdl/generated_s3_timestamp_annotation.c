// auto-maintained by iwyu
// clang-format off
#include "generated_s3_timestamp_annotation.h"
#include <stdbool.h>    // for false, bool, true
#include <stddef.h>     // for NULL, size_t
#include <string.h>     // for memcmp, memset
#include "errors.h"     // for Error, PState, UState, ERR_CHOICE_KEY, Error::(anonymous), UNUSED
#include "parsers.h"    // for alloc_hexBinary, parse_hexBinary, parse_be_float, parse_be_int16, parse_be_bool32, parse_be_bool16, parse_be_int32, parse_be_uint16, parse_be_uint32, parse_le_bool32, parse_le_int64, parse_le_uint16, parse_le_uint8, parse_be_bool8, parse_be_double, parse_be_int64, parse_be_int8, parse_be_uint64, parse_be_uint8, parse_le_bool16, parse_le_bool8, parse_le_double, parse_le_float, parse_le_int16, parse_le_int32, parse_le_int8, parse_le_uint32, parse_le_uint64
#include "unparsers.h"  // for unparse_hexBinary, unparse_be_float, unparse_be_int16, unparse_be_bool32, unparse_be_bool16, unparse_be_int32, unparse_be_uint16, unparse_be_uint32, unparse_le_bool32, unparse_le_int64, unparse_le_uint16, unparse_le_uint8, unparse_be_bool8, unparse_be_double, unparse_be_int64, unparse_be_int8, unparse_be_uint64, unparse_be_uint8, unparse_le_bool16, unparse_le_bool8, unparse_le_double, unparse_le_float, unparse_le_int16, unparse_le_int32, unparse_le_int8, unparse_le_uint32, unparse_le_uint64
#include "validators.h" // for validate_array_bounds, validate_fixed_attribute, validate_floatpt_enumeration, validate_integer_enumeration, validate_schema_range
// clang-format on

// Declare prototypes for easier compilation

static void gpsTime_annotationType__parseSelf(gpsTime_annotationType_ *instance, PState *pstate);
static void gpsTime_annotationType__unparseSelf(const gpsTime_annotationType_ *instance, UState *ustate);
static void annotation__parseSelf(annotation_ *instance, PState *pstate);
static void annotation__unparseSelf(const annotation_ *instance, UState *ustate);

// Define schema version (will be empty if schema did not define any version string)

const char *schema_version = "";

// Define metadata for the infoset

static const ERD days_gpsTimeType_ERD = {
    {
        NULL, // namedQName.prefix
        "days", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD seconds_gpsTimeType_ERD = {
    {
        NULL, // namedQName.prefix
        "seconds", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD microseconds_gpsTimeType_ERD = {
    {
        NULL, // namedQName.prefix
        "microseconds", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const gpsTime_annotationType_ gpsTime_annotationType__compute_offsets;

static const size_t gpsTime_annotationType__childrenOffsets[3] = {
    (const char *)&gpsTime_annotationType__compute_offsets.days - (const char *)&gpsTime_annotationType__compute_offsets,
    (const char *)&gpsTime_annotationType__compute_offsets.seconds - (const char *)&gpsTime_annotationType__compute_offsets,
    (const char *)&gpsTime_annotationType__compute_offsets.microseconds - (const char *)&gpsTime_annotationType__compute_offsets
};

static const ERD *const gpsTime_annotationType__childrenERDs[3] = {
    &days_gpsTimeType_ERD,
    &seconds_gpsTimeType_ERD,
    &microseconds_gpsTimeType_ERD
};

static const ERD gpsTime_annotationType_ERD = {
    {
        NULL, // namedQName.prefix
        "gpsTime", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    3, // numChildren
    gpsTime_annotationType__childrenOffsets,
    gpsTime_annotationType__childrenERDs,
    (ERDParseSelf)&gpsTime_annotationType__parseSelf,
    (ERDUnparseSelf)&gpsTime_annotationType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD fepAnnotationData_annotationType_ERD = {
    {
        NULL, // namedQName.prefix
        "fepAnnotationData", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const annotation_ annotation__compute_offsets;

static const size_t annotation__childrenOffsets[2] = {
    (const char *)&annotation__compute_offsets.gpsTime - (const char *)&annotation__compute_offsets,
    (const char *)&annotation__compute_offsets.fepAnnotationData - (const char *)&annotation__compute_offsets
};

static const ERD *const annotation__childrenERDs[2] = {
    &gpsTime_annotationType_ERD,
    &fepAnnotationData_annotationType_ERD
};

static const ERD annotation_ERD = {
    {
        NULL, // namedQName.prefix
        "annotation", // namedQName.local
        "http://www.esa.int/safe/sentinel-1.0/", // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    annotation__childrenOffsets,
    annotation__childrenERDs,
    (ERDParseSelf)&annotation__parseSelf,
    (ERDUnparseSelf)&annotation__unparseSelf,
    {.initChoice = NULL}
};

// Initialize, parse, and unparse nodes of the infoset

static void
gpsTime_annotationType__initERD(gpsTime_annotationType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &gpsTime_annotationType_ERD;
    instance->_base.parent = parent;
}

static void
gpsTime_annotationType__parseSelf(gpsTime_annotationType_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->days, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->seconds, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->microseconds, 32, pstate);
    if (pstate->pu.error) return;
}

static void
gpsTime_annotationType__unparseSelf(const gpsTime_annotationType_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->days, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->seconds, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->microseconds, 32, ustate);
    if (ustate->pu.error) return;
}

static void
annotation__initERD(annotation_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &annotation_ERD;
    instance->_base.parent = parent;
    gpsTime_annotationType__initERD(&instance->gpsTime, (InfosetBase *)instance);
    instance->fepAnnotationData.array = instance->_a_fepAnnotationData;
    instance->fepAnnotationData.lengthInBytes = sizeof(instance->_a_fepAnnotationData);
    instance->fepAnnotationData.dynamic = false;
}

static void
annotation__parseSelf(annotation_ *instance, PState *pstate)
{
    gpsTime_annotationType__parseSelf(&instance->gpsTime, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->fepAnnotationData, pstate);
    if (pstate->pu.error) return;
}

static void
annotation__unparseSelf(const annotation_ *instance, UState *ustate)
{
    gpsTime_annotationType__unparseSelf(&instance->gpsTime, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->fepAnnotationData, ustate);
    if (ustate->pu.error) return;
}

// Get an infoset (optionally clearing it first) for parsing/walking

InfosetBase *
get_infoset(bool clear_infoset)
{
    static annotation_ infoset;

    if (clear_infoset)
    {
        // If your infoset contains hexBinary prefixed length elements,
        // you may want to walk infoset first to free their malloc'ed
        // storage - we are not handling that case for now...
        memset(&infoset, 0, sizeof(infoset));
        annotation__initERD(&infoset, (InfosetBase *)&infoset);
    }

    return &infoset._base;
}

const int packet_size = 30;

