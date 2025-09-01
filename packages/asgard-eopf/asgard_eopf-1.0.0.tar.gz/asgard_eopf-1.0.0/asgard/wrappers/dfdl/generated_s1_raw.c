// auto-maintained by iwyu
// clang-format off
#include "generated_s1_raw.h"
#include <stdbool.h>    // for false, bool, true
#include <stddef.h>     // for NULL, size_t
#include <string.h>     // for memcmp, memset
#include "errors.h"     // for Error, PState, UState, ERR_CHOICE_KEY, Error::(anonymous), UNUSED
#include "parsers.h"    // for alloc_hexBinary, parse_hexBinary, parse_be_float, parse_be_int16, parse_be_bool32, parse_be_bool16, parse_be_int32, parse_be_uint16, parse_be_uint32, parse_le_bool32, parse_le_int64, parse_le_uint16, parse_le_uint8, parse_be_bool8, parse_be_double, parse_be_int64, parse_be_int8, parse_be_uint64, parse_be_uint8, parse_le_bool16, parse_le_bool8, parse_le_double, parse_le_float, parse_le_int16, parse_le_int32, parse_le_int8, parse_le_uint32, parse_le_uint64
#include "unparsers.h"  // for unparse_hexBinary, unparse_be_float, unparse_be_int16, unparse_be_bool32, unparse_be_bool16, unparse_be_int32, unparse_be_uint16, unparse_be_uint32, unparse_le_bool32, unparse_le_int64, unparse_le_uint16, unparse_le_uint8, unparse_be_bool8, unparse_be_double, unparse_be_int64, unparse_be_int8, unparse_be_uint64, unparse_be_uint8, unparse_le_bool16, unparse_le_bool8, unparse_le_double, unparse_le_float, unparse_le_int16, unparse_le_int32, unparse_le_int8, unparse_le_uint32, unparse_le_uint64
#include "validators.h" // for validate_array_bounds, validate_fixed_attribute, validate_floatpt_enumeration, validate_integer_enumeration, validate_schema_range
// clang-format on

// Declare prototypes for easier compilation

static void primaryHeader_ispType__parseSelf(primaryHeader_ispType_ *instance, PState *pstate);
static void primaryHeader_ispType__unparseSelf(const primaryHeader_ispType_ *instance, UState *ustate);
static void time_secondaryHeaderType__parseSelf(time_secondaryHeaderType_ *instance, PState *pstate);
static void time_secondaryHeaderType__unparseSelf(const time_secondaryHeaderType_ *instance, UState *ustate);
static void subcommutatedAncillary_secondaryHeaderType__parseSelf(subcommutatedAncillary_secondaryHeaderType_ *instance, PState *pstate);
static void subcommutatedAncillary_secondaryHeaderType__unparseSelf(const subcommutatedAncillary_secondaryHeaderType_ *instance, UState *ustate);
static void secondaryHeader_ispType__parseSelf(secondaryHeader_ispType_ *instance, PState *pstate);
static void secondaryHeader_ispType__unparseSelf(const secondaryHeader_ispType_ *instance, UState *ustate);
static void isp__parseSelf(isp_ *instance, PState *pstate);
static void isp__unparseSelf(const isp_ *instance, UState *ustate);

// Define schema version (will be empty if schema did not define any version string)

const char *schema_version = "";

// Define metadata for the infoset

static const ERD packetVersionNumber_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "packetVersionNumber", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD packetType_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "packetType", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD dataFieldHeaderFlag_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "dataFieldHeaderFlag", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PID_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "PID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PCAT_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "PCAT", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD groupingFlags_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "groupingFlags", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD sequenceCount_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "sequenceCount", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD packetLength_mainHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "packetLength", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const primaryHeader_ispType_ primaryHeader_ispType__compute_offsets;

static const size_t primaryHeader_ispType__childrenOffsets[8] = {
    (const char *)&primaryHeader_ispType__compute_offsets.packetVersionNumber - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.packetType - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.dataFieldHeaderFlag - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.PID - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.PCAT - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.groupingFlags - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.sequenceCount - (const char *)&primaryHeader_ispType__compute_offsets,
    (const char *)&primaryHeader_ispType__compute_offsets.packetLength - (const char *)&primaryHeader_ispType__compute_offsets
};

static const ERD *const primaryHeader_ispType__childrenERDs[8] = {
    &packetVersionNumber_mainHeaderType_ERD,
    &packetType_mainHeaderType_ERD,
    &dataFieldHeaderFlag_mainHeaderType_ERD,
    &PID_mainHeaderType_ERD,
    &PCAT_mainHeaderType_ERD,
    &groupingFlags_mainHeaderType_ERD,
    &sequenceCount_mainHeaderType_ERD,
    &packetLength_mainHeaderType_ERD
};

static const ERD primaryHeader_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "primaryHeader", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    8, // numChildren
    primaryHeader_ispType__childrenOffsets,
    primaryHeader_ispType__childrenERDs,
    (ERDParseSelf)&primaryHeader_ispType__parseSelf,
    (ERDUnparseSelf)&primaryHeader_ispType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD coarse_cucTime_ERD = {
    {
        NULL, // namedQName.prefix
        "coarse", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD fine_cucTime_ERD = {
    {
        NULL, // namedQName.prefix
        "fine", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const time_secondaryHeaderType_ time_secondaryHeaderType__compute_offsets;

static const size_t time_secondaryHeaderType__childrenOffsets[2] = {
    (const char *)&time_secondaryHeaderType__compute_offsets.coarse - (const char *)&time_secondaryHeaderType__compute_offsets,
    (const char *)&time_secondaryHeaderType__compute_offsets.fine - (const char *)&time_secondaryHeaderType__compute_offsets
};

static const ERD *const time_secondaryHeaderType__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD time_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "time", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    time_secondaryHeaderType__childrenOffsets,
    time_secondaryHeaderType__childrenERDs,
    (ERDParseSelf)&time_secondaryHeaderType__parseSelf,
    (ERDUnparseSelf)&time_secondaryHeaderType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD syncMarker_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "syncMarker", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD dataTakeID_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "dataTakeID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD ECC_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "ECC", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding1_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD testMode_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "testMode", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD RXChannelID_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "RXChannelID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD instrumentConfigID_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "instrumentConfigID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD wordIndex_subcommutatedAncillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "wordIndex", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD word_subcommutatedAncillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "word", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const subcommutatedAncillary_secondaryHeaderType_ subcommutatedAncillary_secondaryHeaderType__compute_offsets;

static const size_t subcommutatedAncillary_secondaryHeaderType__childrenOffsets[2] = {
    (const char *)&subcommutatedAncillary_secondaryHeaderType__compute_offsets.wordIndex - (const char *)&subcommutatedAncillary_secondaryHeaderType__compute_offsets,
    (const char *)&subcommutatedAncillary_secondaryHeaderType__compute_offsets.word - (const char *)&subcommutatedAncillary_secondaryHeaderType__compute_offsets
};

static const ERD *const subcommutatedAncillary_secondaryHeaderType__childrenERDs[2] = {
    &wordIndex_subcommutatedAncillaryType_ERD,
    &word_subcommutatedAncillaryType_ERD
};

static const ERD subcommutatedAncillary_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "subcommutatedAncillary", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    subcommutatedAncillary_secondaryHeaderType__childrenOffsets,
    subcommutatedAncillary_secondaryHeaderType__childrenERDs,
    (ERDParseSelf)&subcommutatedAncillary_secondaryHeaderType__parseSelf,
    (ERDUnparseSelf)&subcommutatedAncillary_secondaryHeaderType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD spacePacketCount_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "spacePacketCount", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PRICount_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "PRICount", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD errorFlag_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "errorFlag", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding2_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD BAQMode_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "BAQMode", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD BAQBlockLength_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "BAQBlockLength", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding3_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD rangeDecimation_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "rangeDecimation", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD rxGain_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "rxGain", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD txPulseRampRate_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "txPulseRampRate", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD txPulseStartFrequency_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "txPulseStartFrequency", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD txPulseLength_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "txPulseLength", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding4_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding4", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD rank_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "rank", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PRI_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "PRI", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SWST_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "SWST", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SWL_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "SWL", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SSBMessageSAS_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "SSBMessageSAS", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SSBMessageSES_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "SSBMessageSES", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD numberOfQuad_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "numberOfQuad", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding5_secondaryHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding5", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const secondaryHeader_ispType_ secondaryHeader_ispType__compute_offsets;

static const size_t secondaryHeader_ispType__childrenOffsets[30] = {
    (const char *)&secondaryHeader_ispType__compute_offsets.time - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.syncMarker - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.dataTakeID - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.ECC - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets._padding1 - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.testMode - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.RXChannelID - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.instrumentConfigID - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.subcommutatedAncillary - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.spacePacketCount - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.PRICount - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.errorFlag - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets._padding2 - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.BAQMode - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.BAQBlockLength - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets._padding3 - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.rangeDecimation - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.rxGain - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.txPulseRampRate - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.txPulseStartFrequency - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.txPulseLength - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets._padding4 - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.rank - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.PRI - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.SWST - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.SWL - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.SSBMessageSAS - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.SSBMessageSES - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.numberOfQuad - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets._padding5 - (const char *)&secondaryHeader_ispType__compute_offsets
};

static const ERD *const secondaryHeader_ispType__childrenERDs[30] = {
    &time_secondaryHeaderType_ERD,
    &syncMarker_secondaryHeaderType_ERD,
    &dataTakeID_secondaryHeaderType_ERD,
    &ECC_secondaryHeaderType_ERD,
    &_padding1_secondaryHeaderType_ERD,
    &testMode_secondaryHeaderType_ERD,
    &RXChannelID_secondaryHeaderType_ERD,
    &instrumentConfigID_secondaryHeaderType_ERD,
    &subcommutatedAncillary_secondaryHeaderType_ERD,
    &spacePacketCount_secondaryHeaderType_ERD,
    &PRICount_secondaryHeaderType_ERD,
    &errorFlag_secondaryHeaderType_ERD,
    &_padding2_secondaryHeaderType_ERD,
    &BAQMode_secondaryHeaderType_ERD,
    &BAQBlockLength_secondaryHeaderType_ERD,
    &_padding3_secondaryHeaderType_ERD,
    &rangeDecimation_secondaryHeaderType_ERD,
    &rxGain_secondaryHeaderType_ERD,
    &txPulseRampRate_secondaryHeaderType_ERD,
    &txPulseStartFrequency_secondaryHeaderType_ERD,
    &txPulseLength_secondaryHeaderType_ERD,
    &_padding4_secondaryHeaderType_ERD,
    &rank_secondaryHeaderType_ERD,
    &PRI_secondaryHeaderType_ERD,
    &SWST_secondaryHeaderType_ERD,
    &SWL_secondaryHeaderType_ERD,
    &SSBMessageSAS_secondaryHeaderType_ERD,
    &SSBMessageSES_secondaryHeaderType_ERD,
    &numberOfQuad_secondaryHeaderType_ERD,
    &_padding5_secondaryHeaderType_ERD
};

static const ERD secondaryHeader_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "secondaryHeader", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    30, // numChildren
    secondaryHeader_ispType__childrenOffsets,
    secondaryHeader_ispType__childrenERDs,
    (ERDParseSelf)&secondaryHeader_ispType__parseSelf,
    (ERDUnparseSelf)&secondaryHeader_ispType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD sourceData_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "sourceData", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const isp_ isp__compute_offsets;

static const size_t isp__childrenOffsets[3] = {
    (const char *)&isp__compute_offsets.primaryHeader - (const char *)&isp__compute_offsets,
    (const char *)&isp__compute_offsets.secondaryHeader - (const char *)&isp__compute_offsets,
    (const char *)&isp__compute_offsets.sourceData - (const char *)&isp__compute_offsets
};

static const ERD *const isp__childrenERDs[3] = {
    &primaryHeader_ispType_ERD,
    &secondaryHeader_ispType_ERD,
    &sourceData_ispType_ERD
};

static const ERD isp_ERD = {
    {
        NULL, // namedQName.prefix
        "isp", // namedQName.local
        "http://www.esa.int/safe/sentinel-1.0/", // namedQName.ns
    },
    COMPLEX, // typeCode
    3, // numChildren
    isp__childrenOffsets,
    isp__childrenERDs,
    (ERDParseSelf)&isp__parseSelf,
    (ERDUnparseSelf)&isp__unparseSelf,
    {.initChoice = NULL}
};

// Initialize, parse, and unparse nodes of the infoset

static void
primaryHeader_ispType__initERD(primaryHeader_ispType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &primaryHeader_ispType_ERD;
    instance->_base.parent = parent;
}

static void
primaryHeader_ispType__parseSelf(primaryHeader_ispType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->packetVersionNumber, 3, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->packetVersionNumber == 0, "packetVersionNumber", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->packetType, 1, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->packetType == 0, "packetType", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->dataFieldHeaderFlag, 1, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->dataFieldHeaderFlag == 1, "dataFieldHeaderFlag", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->PID, 7, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->PCAT, 4, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->groupingFlags, 2, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->groupingFlags == 3, "groupingFlags", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->sequenceCount, 14, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->packetLength, 16, pstate);
    if (pstate->pu.error) return;
}

static void
primaryHeader_ispType__unparseSelf(const primaryHeader_ispType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->packetVersionNumber, 3, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->packetVersionNumber == 0, "packetVersionNumber", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->packetType, 1, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->packetType == 0, "packetType", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->dataFieldHeaderFlag, 1, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->dataFieldHeaderFlag == 1, "dataFieldHeaderFlag", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->PID, 7, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->PCAT, 4, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->groupingFlags, 2, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->groupingFlags == 3, "groupingFlags", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->sequenceCount, 14, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->packetLength, 16, ustate);
    if (ustate->pu.error) return;
}

static void
time_secondaryHeaderType__initERD(time_secondaryHeaderType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &time_secondaryHeaderType_ERD;
    instance->_base.parent = parent;
}

static void
time_secondaryHeaderType__parseSelf(time_secondaryHeaderType_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->fine, 16, pstate);
    if (pstate->pu.error) return;
}

static void
time_secondaryHeaderType__unparseSelf(const time_secondaryHeaderType_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->fine, 16, ustate);
    if (ustate->pu.error) return;
}

static void
subcommutatedAncillary_secondaryHeaderType__initERD(subcommutatedAncillary_secondaryHeaderType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &subcommutatedAncillary_secondaryHeaderType_ERD;
    instance->_base.parent = parent;
    instance->word.array = instance->_a_word;
    instance->word.lengthInBytes = sizeof(instance->_a_word);
    instance->word.dynamic = false;
}

static void
subcommutatedAncillary_secondaryHeaderType__parseSelf(subcommutatedAncillary_secondaryHeaderType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->wordIndex, 8, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->word, pstate);
    if (pstate->pu.error) return;
}

static void
subcommutatedAncillary_secondaryHeaderType__unparseSelf(const subcommutatedAncillary_secondaryHeaderType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->wordIndex, 8, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->word, ustate);
    if (ustate->pu.error) return;
}

static void
secondaryHeader_ispType__initERD(secondaryHeader_ispType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &secondaryHeader_ispType_ERD;
    instance->_base.parent = parent;
    time_secondaryHeaderType__initERD(&instance->time, (InfosetBase *)instance);
    subcommutatedAncillary_secondaryHeaderType__initERD(&instance->subcommutatedAncillary, (InfosetBase *)instance);
    instance->SSBMessageSAS.array = instance->_a_SSBMessageSAS;
    instance->SSBMessageSAS.lengthInBytes = sizeof(instance->_a_SSBMessageSAS);
    instance->SSBMessageSAS.dynamic = false;
    instance->SSBMessageSES.array = instance->_a_SSBMessageSES;
    instance->SSBMessageSES.lengthInBytes = sizeof(instance->_a_SSBMessageSES);
    instance->SSBMessageSES.dynamic = false;
}

static void
secondaryHeader_ispType__parseSelf(secondaryHeader_ispType_ *instance, PState *pstate)
{
    time_secondaryHeaderType__parseSelf(&instance->time, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->syncMarker, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->dataTakeID, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->ECC, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding1, 1, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->testMode, 3, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->RXChannelID, 4, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->instrumentConfigID, 32, pstate);
    if (pstate->pu.error) return;
    subcommutatedAncillary_secondaryHeaderType__parseSelf(&instance->subcommutatedAncillary, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->spacePacketCount, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->PRICount, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->errorFlag, 1, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding2, 2, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->BAQMode, 5, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->BAQBlockLength, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding3, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->rangeDecimation, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->rxGain, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->txPulseRampRate, 16, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->txPulseStartFrequency, 16, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->txPulseLength, 24, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding4, 3, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->rank, 5, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->PRI, 24, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->SWST, 24, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->SWL, 24, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->SSBMessageSAS, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->SSBMessageSES, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->numberOfQuad, 16, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding5, 8, pstate);
    if (pstate->pu.error) return;
}

static void
secondaryHeader_ispType__unparseSelf(const secondaryHeader_ispType_ *instance, UState *ustate)
{
    time_secondaryHeaderType__unparseSelf(&instance->time, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->syncMarker, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->dataTakeID, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->ECC, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding1, 1, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->testMode, 3, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->RXChannelID, 4, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->instrumentConfigID, 32, ustate);
    if (ustate->pu.error) return;
    subcommutatedAncillary_secondaryHeaderType__unparseSelf(&instance->subcommutatedAncillary, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->spacePacketCount, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->PRICount, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->errorFlag, 1, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding2, 2, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->BAQMode, 5, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->BAQBlockLength, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding3, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->rangeDecimation, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->rxGain, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->txPulseRampRate, 16, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->txPulseStartFrequency, 16, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->txPulseLength, 24, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding4, 3, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->rank, 5, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->PRI, 24, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->SWST, 24, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->SWL, 24, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->SSBMessageSAS, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->SSBMessageSES, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->numberOfQuad, 16, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding5, 8, ustate);
    if (ustate->pu.error) return;
}

static void
isp__initERD(isp_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &isp_ERD;
    instance->_base.parent = parent;
    primaryHeader_ispType__initERD(&instance->primaryHeader, (InfosetBase *)instance);
    secondaryHeader_ispType__initERD(&instance->secondaryHeader, (InfosetBase *)instance);
    instance->sourceData.dynamic = true;
}

static void
isp__parseSelf(isp_ *instance, PState *pstate)
{
    primaryHeader_ispType__parseSelf(&instance->primaryHeader, pstate);
    if (pstate->pu.error) return;
    secondaryHeader_ispType__parseSelf(&instance->secondaryHeader, pstate);
    if (pstate->pu.error) return;
    size_t _l_sourceData = instance->primaryHeader.packetLength - 61;
    alloc_hexBinary(&instance->sourceData, _l_sourceData, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->sourceData, pstate);
    if (pstate->pu.error) return;
}

static void
isp__unparseSelf(const isp_ *instance, UState *ustate)
{
    primaryHeader_ispType__unparseSelf(&instance->primaryHeader, ustate);
    if (ustate->pu.error) return;
    secondaryHeader_ispType__unparseSelf(&instance->secondaryHeader, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->sourceData, ustate);
    if (ustate->pu.error) return;
}

// Get an infoset (optionally clearing it first) for parsing/walking

InfosetBase *
get_infoset(bool clear_infoset)
{
    static isp_ infoset;

    if (clear_infoset)
    {
        // If your infoset contains hexBinary prefixed length elements,
        // you may want to walk infoset first to free their malloc'ed
        // storage - we are not handling that case for now...
        memset(&infoset, 0, sizeof(infoset));
        isp__initERD(&infoset, (InfosetBase *)&infoset);
    }

    return &infoset._base;
}

const int packet_size = 0;

