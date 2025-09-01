// auto-maintained by iwyu
// clang-format off
#include "generated_s3_slstr_slt.h"
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
static void time_dataFieldHeaderType__parseSelf(time_dataFieldHeaderType_ *instance, PState *pstate);
static void time_dataFieldHeaderType__unparseSelf(const time_dataFieldHeaderType_ *instance, UState *ustate);
static void secondaryHeader_ispType__parseSelf(secondaryHeader_ispType_ *instance, PState *pstate);
static void secondaryHeader_ispType__unparseSelf(const secondaryHeader_ispType_ *instance, UState *ustate);
static void header_slstrType__parseSelf(header_slstrType_ *instance, PState *pstate);
static void header_slstrType__unparseSelf(const header_slstrType_ *instance, UState *ustate);
static void array_array_slstrBandArray_band_slstrData__parseSelf(band_slstrData_ *instance, PState *pstate);
static void array_array_slstrBandArray_band_slstrData__unparseSelf(const band_slstrData_ *instance, UState *ustate);
static size_t array_array_slstrBandArray_band_slstrData__getArraySize(const band_slstrData_ *instance);
static void band_slstrData__parseSelf(band_slstrData_ *instance, PState *pstate);
static void band_slstrData__unparseSelf(const band_slstrData_ *instance, UState *ustate);
static void array_slstrScanEncoderArray__parseSelf(array_slstrScanEncoderArray_ *instance, PState *pstate);
static void array_slstrScanEncoderArray__unparseSelf(const array_slstrScanEncoderArray_ *instance, UState *ustate);
static void array_array_slstrScanEncoderArray_scanpos_slstrData__parseSelf(scanpos_slstrData_ *instance, PState *pstate);
static void array_array_slstrScanEncoderArray_scanpos_slstrData__unparseSelf(const scanpos_slstrData_ *instance, UState *ustate);
static size_t array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize(const scanpos_slstrData_ *instance);
static void scanpos_slstrData__parseSelf(scanpos_slstrData_ *instance, PState *pstate);
static void scanpos_slstrData__unparseSelf(const scanpos_slstrData_ *instance, UState *ustate);
static void hk_slstrData__parseSelf(hk_slstrData_ *instance, PState *pstate);
static void hk_slstrData__unparseSelf(const hk_slstrData_ *instance, UState *ustate);
static const Error *data_slstrType__initChoice(data_slstrType_ *instance);
static void data_slstrType__parseSelf(data_slstrType_ *instance, PState *pstate);
static void data_slstrType__unparseSelf(const data_slstrType_ *instance, UState *ustate);
static void sourceData_ispType__parseSelf(sourceData_ispType_ *instance, PState *pstate);
static void sourceData_ispType__unparseSelf(const sourceData_ispType_ *instance, UState *ustate);
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

static const ERD spareBit_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "spareBit", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PUSversion_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "PUSversion", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD spare4Bit_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "spare4Bit", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD servicePacketType_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "servicePacketType", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD servicePacketSubType_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "servicePacketSubType", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD destinationID_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "destinationID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
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
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const time_dataFieldHeaderType_ time_dataFieldHeaderType__compute_offsets;

static const size_t time_dataFieldHeaderType__childrenOffsets[2] = {
    (const char *)&time_dataFieldHeaderType__compute_offsets.coarse - (const char *)&time_dataFieldHeaderType__compute_offsets,
    (const char *)&time_dataFieldHeaderType__compute_offsets.fine - (const char *)&time_dataFieldHeaderType__compute_offsets
};

static const ERD *const time_dataFieldHeaderType__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD time_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "time", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    time_dataFieldHeaderType__childrenOffsets,
    time_dataFieldHeaderType__childrenERDs,
    (ERDParseSelf)&time_dataFieldHeaderType__parseSelf,
    (ERDUnparseSelf)&time_dataFieldHeaderType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD timeStatus_dataFieldHeaderType_ERD = {
    {
        NULL, // namedQName.prefix
        "timeStatus", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const secondaryHeader_ispType_ secondaryHeader_ispType__compute_offsets;

static const size_t secondaryHeader_ispType__childrenOffsets[8] = {
    (const char *)&secondaryHeader_ispType__compute_offsets.spareBit - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.PUSversion - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.spare4Bit - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.servicePacketType - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.servicePacketSubType - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.destinationID - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.time - (const char *)&secondaryHeader_ispType__compute_offsets,
    (const char *)&secondaryHeader_ispType__compute_offsets.timeStatus - (const char *)&secondaryHeader_ispType__compute_offsets
};

static const ERD *const secondaryHeader_ispType__childrenERDs[8] = {
    &spareBit_dataFieldHeaderType_ERD,
    &PUSversion_dataFieldHeaderType_ERD,
    &spare4Bit_dataFieldHeaderType_ERD,
    &servicePacketType_dataFieldHeaderType_ERD,
    &servicePacketSubType_dataFieldHeaderType_ERD,
    &destinationID_dataFieldHeaderType_ERD,
    &time_dataFieldHeaderType_ERD,
    &timeStatus_dataFieldHeaderType_ERD
};

static const ERD secondaryHeader_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "secondaryHeader", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    8, // numChildren
    secondaryHeader_ispType__childrenOffsets,
    secondaryHeader_ispType__childrenERDs,
    (ERDParseSelf)&secondaryHeader_ispType__parseSelf,
    (ERDUnparseSelf)&secondaryHeader_ispType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD SCAN_SYNC_COUNTER_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "SCAN_SYNC_COUNTER", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD DPM_MODE_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "DPM_MODE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD VALIDITY_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "VALIDITY", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD TARGET_ID_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "TARGET_ID", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD TARGET_FIRST_ACQ_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "TARGET_FIRST_ACQ", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD TARGET_LENGTH_slstrHeader_ERD = {
    {
        NULL, // namedQName.prefix
        "TARGET_LENGTH", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const header_slstrType_ header_slstrType__compute_offsets;

static const size_t header_slstrType__childrenOffsets[6] = {
    (const char *)&header_slstrType__compute_offsets.SCAN_SYNC_COUNTER - (const char *)&header_slstrType__compute_offsets,
    (const char *)&header_slstrType__compute_offsets.DPM_MODE - (const char *)&header_slstrType__compute_offsets,
    (const char *)&header_slstrType__compute_offsets.VALIDITY - (const char *)&header_slstrType__compute_offsets,
    (const char *)&header_slstrType__compute_offsets.TARGET_ID - (const char *)&header_slstrType__compute_offsets,
    (const char *)&header_slstrType__compute_offsets.TARGET_FIRST_ACQ - (const char *)&header_slstrType__compute_offsets,
    (const char *)&header_slstrType__compute_offsets.TARGET_LENGTH - (const char *)&header_slstrType__compute_offsets
};

static const ERD *const header_slstrType__childrenERDs[6] = {
    &SCAN_SYNC_COUNTER_slstrHeader_ERD,
    &DPM_MODE_slstrHeader_ERD,
    &VALIDITY_slstrHeader_ERD,
    &TARGET_ID_slstrHeader_ERD,
    &TARGET_FIRST_ACQ_slstrHeader_ERD,
    &TARGET_LENGTH_slstrHeader_ERD
};

static const ERD header_slstrType_ERD = {
    {
        NULL, // namedQName.prefix
        "header", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    6, // numChildren
    header_slstrType__childrenOffsets,
    header_slstrType__childrenERDs,
    (ERDParseSelf)&header_slstrType__parseSelf,
    (ERDUnparseSelf)&header_slstrType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD _choice_data_slstrType_ERD = {
    {
        NULL, // namedQName.prefix
        "_choice", // namedQName.local
        NULL, // namedQName.ns
    },
    CHOICE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD array_slstrBandArray_ERD = {
    {
        NULL, // namedQName.prefix
        "array", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const band_slstrData_ array_array_slstrBandArray_band_slstrData__compute_offsets;

static const size_t array_array_slstrBandArray_band_slstrData__childrenOffsets[1] = {
    (const char *)&array_array_slstrBandArray_band_slstrData__compute_offsets.array[1] - (const char *)&array_array_slstrBandArray_band_slstrData__compute_offsets.array[0]
};

static const ERD *const array_array_slstrBandArray_band_slstrData__childrenERDs[1] = {
    &array_slstrBandArray_ERD
};

static const ERD array_array_slstrBandArray_band_slstrData_ERD = {
    {
        NULL, // namedQName.prefix
        "array", // namedQName.local
        NULL, // namedQName.ns
    },
    ARRAY, // typeCode
    40000, // maxOccurs
    array_array_slstrBandArray_band_slstrData__childrenOffsets,
    array_array_slstrBandArray_band_slstrData__childrenERDs,
    (ERDParseSelf)&array_array_slstrBandArray_band_slstrData__parseSelf,
    (ERDUnparseSelf)&array_array_slstrBandArray_band_slstrData__unparseSelf,
    {.getArraySize = (GetArraySize)&array_array_slstrBandArray_band_slstrData__getArraySize}
};

static const band_slstrData_ band_slstrData__compute_offsets;

static const size_t band_slstrData__childrenOffsets[1] = {
    (const char *)&band_slstrData__compute_offsets.array[0] - (const char *)&band_slstrData__compute_offsets
};

static const ERD *const band_slstrData__childrenERDs[1] = {
    &array_array_slstrBandArray_band_slstrData_ERD
};

static const ERD band_slstrData_ERD = {
    {
        NULL, // namedQName.prefix
        "band", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    1, // numChildren
    band_slstrData__childrenOffsets,
    band_slstrData__childrenERDs,
    (ERDParseSelf)&band_slstrData__parseSelf,
    (ERDUnparseSelf)&band_slstrData__unparseSelf,
    {.initChoice = NULL}
};

static const ERD nad_slstrScanEncoder_ERD = {
    {
        NULL, // namedQName.prefix
        "nad", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD obl_slstrScanEncoder_ERD = {
    {
        NULL, // namedQName.prefix
        "obl", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD flip_slstrScanEncoder_ERD = {
    {
        NULL, // namedQName.prefix
        "flip", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_INT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const array_slstrScanEncoderArray_ array_slstrScanEncoderArray__compute_offsets;

static const size_t array_slstrScanEncoderArray__childrenOffsets[3] = {
    (const char *)&array_slstrScanEncoderArray__compute_offsets.nad - (const char *)&array_slstrScanEncoderArray__compute_offsets,
    (const char *)&array_slstrScanEncoderArray__compute_offsets.obl - (const char *)&array_slstrScanEncoderArray__compute_offsets,
    (const char *)&array_slstrScanEncoderArray__compute_offsets.flip - (const char *)&array_slstrScanEncoderArray__compute_offsets
};

static const ERD *const array_slstrScanEncoderArray__childrenERDs[3] = {
    &nad_slstrScanEncoder_ERD,
    &obl_slstrScanEncoder_ERD,
    &flip_slstrScanEncoder_ERD
};

static const ERD array_slstrScanEncoderArray_ERD = {
    {
        NULL, // namedQName.prefix
        "array", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    3, // numChildren
    array_slstrScanEncoderArray__childrenOffsets,
    array_slstrScanEncoderArray__childrenERDs,
    (ERDParseSelf)&array_slstrScanEncoderArray__parseSelf,
    (ERDUnparseSelf)&array_slstrScanEncoderArray__unparseSelf,
    {.initChoice = NULL}
};

static const scanpos_slstrData_ array_array_slstrScanEncoderArray_scanpos_slstrData__compute_offsets;

static const size_t array_array_slstrScanEncoderArray_scanpos_slstrData__childrenOffsets[1] = {
    (const char *)&array_array_slstrScanEncoderArray_scanpos_slstrData__compute_offsets.array[1] - (const char *)&array_array_slstrScanEncoderArray_scanpos_slstrData__compute_offsets.array[0]
};

static const ERD *const array_array_slstrScanEncoderArray_scanpos_slstrData__childrenERDs[1] = {
    &array_slstrScanEncoderArray_ERD
};

static const ERD array_array_slstrScanEncoderArray_scanpos_slstrData_ERD = {
    {
        NULL, // namedQName.prefix
        "array", // namedQName.local
        NULL, // namedQName.ns
    },
    ARRAY, // typeCode
    4000, // maxOccurs
    array_array_slstrScanEncoderArray_scanpos_slstrData__childrenOffsets,
    array_array_slstrScanEncoderArray_scanpos_slstrData__childrenERDs,
    (ERDParseSelf)&array_array_slstrScanEncoderArray_scanpos_slstrData__parseSelf,
    (ERDUnparseSelf)&array_array_slstrScanEncoderArray_scanpos_slstrData__unparseSelf,
    {.getArraySize = (GetArraySize)&array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize}
};

static const scanpos_slstrData_ scanpos_slstrData__compute_offsets;

static const size_t scanpos_slstrData__childrenOffsets[1] = {
    (const char *)&scanpos_slstrData__compute_offsets.array[0] - (const char *)&scanpos_slstrData__compute_offsets
};

static const ERD *const scanpos_slstrData__childrenERDs[1] = {
    &array_array_slstrScanEncoderArray_scanpos_slstrData_ERD
};

static const ERD scanpos_slstrData_ERD = {
    {
        NULL, // namedQName.prefix
        "scanpos", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    1, // numChildren
    scanpos_slstrData__childrenOffsets,
    scanpos_slstrData__childrenERDs,
    (ERDParseSelf)&scanpos_slstrData__parseSelf,
    (ERDUnparseSelf)&scanpos_slstrData__unparseSelf,
    {.initChoice = NULL}
};

static const ERD array_slstrHKArray_ERD = {
    {
        NULL, // namedQName.prefix
        "array", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const hk_slstrData_ hk_slstrData__compute_offsets;

static const size_t hk_slstrData__childrenOffsets[1] = {
    (const char *)&hk_slstrData__compute_offsets.array - (const char *)&hk_slstrData__compute_offsets
};

static const ERD *const hk_slstrData__childrenERDs[1] = {
    &array_slstrHKArray_ERD
};

static const ERD hk_slstrData_ERD = {
    {
        NULL, // namedQName.prefix
        "hk", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    1, // numChildren
    hk_slstrData__childrenOffsets,
    hk_slstrData__childrenERDs,
    (ERDParseSelf)&hk_slstrData__parseSelf,
    (ERDUnparseSelf)&hk_slstrData__unparseSelf,
    {.initChoice = NULL}
};

static const data_slstrType_ data_slstrType__compute_offsets;

static const size_t data_slstrType__childrenOffsets[4] = {
    (const char *)&data_slstrType__compute_offsets._choice - (const char *)&data_slstrType__compute_offsets,
    (const char *)&data_slstrType__compute_offsets.band - (const char *)&data_slstrType__compute_offsets,
    (const char *)&data_slstrType__compute_offsets.scanpos - (const char *)&data_slstrType__compute_offsets,
    (const char *)&data_slstrType__compute_offsets.hk - (const char *)&data_slstrType__compute_offsets
};

static const ERD *const data_slstrType__childrenERDs[4] = {
    &_choice_data_slstrType_ERD,
    &band_slstrData_ERD,
    &scanpos_slstrData_ERD,
    &hk_slstrData_ERD
};

static const ERD data_slstrType_ERD = {
    {
        NULL, // namedQName.prefix
        "data", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    data_slstrType__childrenOffsets,
    data_slstrType__childrenERDs,
    (ERDParseSelf)&data_slstrType__parseSelf,
    (ERDUnparseSelf)&data_slstrType__unparseSelf,
    {.initChoice = (InitChoiceRD)&data_slstrType__initChoice}
};

static const sourceData_ispType_ sourceData_ispType__compute_offsets;

static const size_t sourceData_ispType__childrenOffsets[2] = {
    (const char *)&sourceData_ispType__compute_offsets.header - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.data - (const char *)&sourceData_ispType__compute_offsets
};

static const ERD *const sourceData_ispType__childrenERDs[2] = {
    &header_slstrType_ERD,
    &data_slstrType_ERD
};

static const ERD sourceData_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "sourceData", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    sourceData_ispType__childrenOffsets,
    sourceData_ispType__childrenERDs,
    (ERDParseSelf)&sourceData_ispType__parseSelf,
    (ERDUnparseSelf)&sourceData_ispType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD errorControl_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "errorControl", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const isp_ isp__compute_offsets;

static const size_t isp__childrenOffsets[4] = {
    (const char *)&isp__compute_offsets.primaryHeader - (const char *)&isp__compute_offsets,
    (const char *)&isp__compute_offsets.secondaryHeader - (const char *)&isp__compute_offsets,
    (const char *)&isp__compute_offsets.sourceData - (const char *)&isp__compute_offsets,
    (const char *)&isp__compute_offsets.errorControl - (const char *)&isp__compute_offsets
};

static const ERD *const isp__childrenERDs[4] = {
    &primaryHeader_ispType_ERD,
    &secondaryHeader_ispType_ERD,
    &sourceData_ispType_ERD,
    &errorControl_ispType_ERD
};

static const ERD isp_ERD = {
    {
        NULL, // namedQName.prefix
        "isp", // namedQName.local
        "http://www.esa.int/safe/sentinel-1.0/", // namedQName.ns
    },
    COMPLEX, // typeCode
    4, // numChildren
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
time_dataFieldHeaderType__initERD(time_dataFieldHeaderType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &time_dataFieldHeaderType_ERD;
    instance->_base.parent = parent;
}

static void
time_dataFieldHeaderType__parseSelf(time_dataFieldHeaderType_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
time_dataFieldHeaderType__unparseSelf(const time_dataFieldHeaderType_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
secondaryHeader_ispType__initERD(secondaryHeader_ispType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &secondaryHeader_ispType_ERD;
    instance->_base.parent = parent;
    time_dataFieldHeaderType__initERD(&instance->time, (InfosetBase *)instance);
}

static void
secondaryHeader_ispType__parseSelf(secondaryHeader_ispType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->spareBit, 1, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->spareBit == 0, "spareBit", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->PUSversion, 3, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->PUSversion == 1, "PUSversion", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->spare4Bit, 4, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->spare4Bit == 0, "spare4Bit", &pstate->pu);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->servicePacketType, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->servicePacketSubType, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->destinationID, 8, pstate);
    if (pstate->pu.error) return;
    validate_fixed_attribute(instance->destinationID == 0, "destinationID", &pstate->pu);
    if (pstate->pu.error) return;
    time_dataFieldHeaderType__parseSelf(&instance->time, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->timeStatus, 8, pstate);
    if (pstate->pu.error) return;
}

static void
secondaryHeader_ispType__unparseSelf(const secondaryHeader_ispType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->spareBit, 1, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->spareBit == 0, "spareBit", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->PUSversion, 3, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->PUSversion == 1, "PUSversion", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->spare4Bit, 4, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->spare4Bit == 0, "spare4Bit", &ustate->pu);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->servicePacketType, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->servicePacketSubType, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->destinationID, 8, ustate);
    if (ustate->pu.error) return;
    validate_fixed_attribute(instance->destinationID == 0, "destinationID", &ustate->pu);
    if (ustate->pu.error) return;
    time_dataFieldHeaderType__unparseSelf(&instance->time, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->timeStatus, 8, ustate);
    if (ustate->pu.error) return;
}

static void
header_slstrType__initERD(header_slstrType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &header_slstrType_ERD;
    instance->_base.parent = parent;
}

static void
header_slstrType__parseSelf(header_slstrType_ *instance, PState *pstate)
{
    parse_be_uint16(&instance->SCAN_SYNC_COUNTER, 16, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->DPM_MODE, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->VALIDITY, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->TARGET_ID, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->TARGET_FIRST_ACQ, 16, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->TARGET_LENGTH, 16, pstate);
    if (pstate->pu.error) return;
}

static void
header_slstrType__unparseSelf(const header_slstrType_ *instance, UState *ustate)
{
    unparse_be_uint16(instance->SCAN_SYNC_COUNTER, 16, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->DPM_MODE, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->VALIDITY, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->TARGET_ID, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->TARGET_FIRST_ACQ, 16, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->TARGET_LENGTH, 16, ustate);
    if (ustate->pu.error) return;
}

static void
array_array_slstrBandArray_band_slstrData__initERD(band_slstrData_ *instance, InfosetBase *parent)
{
    UNUSED(instance);
    UNUSED(parent);
}

static void
array_array_slstrBandArray_band_slstrData__parseSelf(band_slstrData_ *instance, PState *pstate)
{
    const size_t arraySize = array_array_slstrBandArray_band_slstrData__getArraySize(instance);
    validate_array_bounds("array_array_slstrBandArray_band_slstrData_", arraySize, 0, 40000, &pstate->pu);
    if (pstate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        parse_be_uint16(&instance->array[i], 16, pstate);
        if (pstate->pu.error) return;
    }
}

static void
array_array_slstrBandArray_band_slstrData__unparseSelf(const band_slstrData_ *instance, UState *ustate)
{
    const size_t arraySize = array_array_slstrBandArray_band_slstrData__getArraySize(instance);
    validate_array_bounds("array_array_slstrBandArray_band_slstrData_", arraySize, 0, 40000, &ustate->pu);
    if (ustate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        unparse_be_uint16(instance->array[i], 16, ustate);
        if (ustate->pu.error) return;
    }
}

static size_t
array_array_slstrBandArray_band_slstrData__getArraySize(const band_slstrData_ *instance)
{
    return (((isp_ *)instance->_base.parent->parent->parent)->primaryHeader.packetLength-22) / 2;
}

static void
band_slstrData__initERD(band_slstrData_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &band_slstrData_ERD;
    instance->_base.parent = parent;
    array_array_slstrBandArray_band_slstrData__initERD(instance, parent);
}

static void
band_slstrData__parseSelf(band_slstrData_ *instance, PState *pstate)
{
    array_array_slstrBandArray_band_slstrData__parseSelf(instance, pstate);
    if (pstate->pu.error) return;
}

static void
band_slstrData__unparseSelf(const band_slstrData_ *instance, UState *ustate)
{
    array_array_slstrBandArray_band_slstrData__unparseSelf(instance, ustate);
    if (ustate->pu.error) return;
}

static void
array_slstrScanEncoderArray__initERD(array_slstrScanEncoderArray_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &array_slstrScanEncoderArray_ERD;
    instance->_base.parent = parent;
}

static void
array_slstrScanEncoderArray__parseSelf(array_slstrScanEncoderArray_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->nad, 24, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->obl, 24, pstate);
    if (pstate->pu.error) return;
    parse_be_int16(&instance->flip, 16, pstate);
    if (pstate->pu.error) return;
}

static void
array_slstrScanEncoderArray__unparseSelf(const array_slstrScanEncoderArray_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->nad, 24, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->obl, 24, ustate);
    if (ustate->pu.error) return;
    unparse_be_int16(instance->flip, 16, ustate);
    if (ustate->pu.error) return;
}

static void
array_array_slstrScanEncoderArray_scanpos_slstrData__initERD(scanpos_slstrData_ *instance, InfosetBase *parent)
{
    UNUSED(parent);
    for (size_t i = 0; i < 4000; i++)
    {
        array_slstrScanEncoderArray__initERD(&instance->array[i], (InfosetBase *)instance);
    }
}

static void
array_array_slstrScanEncoderArray_scanpos_slstrData__parseSelf(scanpos_slstrData_ *instance, PState *pstate)
{
    const size_t arraySize = array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize(instance);
    validate_array_bounds("array_array_slstrScanEncoderArray_scanpos_slstrData_", arraySize, 0, 4000, &pstate->pu);
    if (pstate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        array_slstrScanEncoderArray__parseSelf(&instance->array[i], pstate);
        if (pstate->pu.error) return;
    }
}

static void
array_array_slstrScanEncoderArray_scanpos_slstrData__unparseSelf(const scanpos_slstrData_ *instance, UState *ustate)
{
    const size_t arraySize = array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize(instance);
    validate_array_bounds("array_array_slstrScanEncoderArray_scanpos_slstrData_", arraySize, 0, 4000, &ustate->pu);
    if (ustate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        array_slstrScanEncoderArray__unparseSelf(&instance->array[i], ustate);
        if (ustate->pu.error) return;
    }
}

static size_t
array_array_slstrScanEncoderArray_scanpos_slstrData__getArraySize(const scanpos_slstrData_ *instance)
{
    return ((sourceData_ispType_ *)instance->_base.parent->parent)->header.TARGET_LENGTH;
}

static void
scanpos_slstrData__initERD(scanpos_slstrData_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &scanpos_slstrData_ERD;
    instance->_base.parent = parent;
    array_array_slstrScanEncoderArray_scanpos_slstrData__initERD(instance, parent);
}

static void
scanpos_slstrData__parseSelf(scanpos_slstrData_ *instance, PState *pstate)
{
    array_array_slstrScanEncoderArray_scanpos_slstrData__parseSelf(instance, pstate);
    if (pstate->pu.error) return;
}

static void
scanpos_slstrData__unparseSelf(const scanpos_slstrData_ *instance, UState *ustate)
{
    array_array_slstrScanEncoderArray_scanpos_slstrData__unparseSelf(instance, ustate);
    if (ustate->pu.error) return;
}

static void
hk_slstrData__initERD(hk_slstrData_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &hk_slstrData_ERD;
    instance->_base.parent = parent;
    instance->array.array = instance->_a_array;
    instance->array.lengthInBytes = sizeof(instance->_a_array);
    instance->array.dynamic = false;
}

static void
hk_slstrData__parseSelf(hk_slstrData_ *instance, PState *pstate)
{
    parse_hexBinary(&instance->array, pstate);
    if (pstate->pu.error) return;
}

static void
hk_slstrData__unparseSelf(const hk_slstrData_ *instance, UState *ustate)
{
    unparse_hexBinary(instance->array, ustate);
    if (ustate->pu.error) return;
}

static void
data_slstrType__initERD(data_slstrType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &data_slstrType_ERD;
    instance->_base.parent = parent;
}

static const Error *
data_slstrType__initChoice(data_slstrType_ *instance)
{
    static Error error = {ERR_CHOICE_KEY, {0}};

    int64_t key = ((isp_ *)instance->_base.parent->parent)->primaryHeader.PCAT;
    switch (key)
    {
    case 0:
    case 1:
    case 2:
    case 3:
    case 4:
    case 5:
    case 6:
    case 7:
    case 8:
    case 9:
    case 10:
        instance->_choice = 1;
        band_slstrData__initERD(&instance->band, (InfosetBase *)instance);
        break;
    case 11:
        instance->_choice = 2;
        scanpos_slstrData__initERD(&instance->scanpos, (InfosetBase *)instance);
        break;
    case 12:
        instance->_choice = 3;
        hk_slstrData__initERD(&instance->hk, (InfosetBase *)instance);
        break;
    default:
        error.arg.d64 = key;
        return &error;
    }

    return NULL;
}

static void
data_slstrType__parseSelf(data_slstrType_ *instance, PState *pstate)
{
    static Error error = {ERR_CHOICE_KEY, {0}};

    pstate->pu.error = instance->_base.erd->initChoice(&instance->_base);
    if (pstate->pu.error) return;

    switch (instance->_choice)
    {
    case 1:
        band_slstrData__parseSelf(&instance->band, pstate);
        if (pstate->pu.error) return;
        break;
    case 2:
        scanpos_slstrData__parseSelf(&instance->scanpos, pstate);
        if (pstate->pu.error) return;
        break;
    case 3:
        hk_slstrData__parseSelf(&instance->hk, pstate);
        if (pstate->pu.error) return;
        break;
    default:
        // Should never happen because initChoice would return an error first
        error.arg.d64 = (int64_t)instance->_choice;
        pstate->pu.error = &error;
        return;
    }
}

static void
data_slstrType__unparseSelf(const data_slstrType_ *instance, UState *ustate)
{
    static Error error = {ERR_CHOICE_KEY, {0}};

    ustate->pu.error = instance->_base.erd->initChoice(&instance->_base);
    if (ustate->pu.error) return;

    switch (instance->_choice)
    {
    case 1:
        band_slstrData__unparseSelf(&instance->band, ustate);
        if (ustate->pu.error) return;
        break;
    case 2:
        scanpos_slstrData__unparseSelf(&instance->scanpos, ustate);
        if (ustate->pu.error) return;
        break;
    case 3:
        hk_slstrData__unparseSelf(&instance->hk, ustate);
        if (ustate->pu.error) return;
        break;
    default:
        // Should never happen because initChoice would return an error first
        error.arg.d64 = (int64_t)instance->_choice;
        ustate->pu.error = &error;
        return;
    }
}

static void
sourceData_ispType__initERD(sourceData_ispType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &sourceData_ispType_ERD;
    instance->_base.parent = parent;
    header_slstrType__initERD(&instance->header, (InfosetBase *)instance);
    data_slstrType__initERD(&instance->data, (InfosetBase *)instance);
}

static void
sourceData_ispType__parseSelf(sourceData_ispType_ *instance, PState *pstate)
{
    header_slstrType__parseSelf(&instance->header, pstate);
    if (pstate->pu.error) return;
    data_slstrType__parseSelf(&instance->data, pstate);
    if (pstate->pu.error) return;
}

static void
sourceData_ispType__unparseSelf(const sourceData_ispType_ *instance, UState *ustate)
{
    header_slstrType__unparseSelf(&instance->header, ustate);
    if (ustate->pu.error) return;
    data_slstrType__unparseSelf(&instance->data, ustate);
    if (ustate->pu.error) return;
}

static void
isp__initERD(isp_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &isp_ERD;
    instance->_base.parent = parent;
    primaryHeader_ispType__initERD(&instance->primaryHeader, (InfosetBase *)instance);
    secondaryHeader_ispType__initERD(&instance->secondaryHeader, (InfosetBase *)instance);
    sourceData_ispType__initERD(&instance->sourceData, (InfosetBase *)instance);
}

static void
isp__parseSelf(isp_ *instance, PState *pstate)
{
    primaryHeader_ispType__parseSelf(&instance->primaryHeader, pstate);
    if (pstate->pu.error) return;
    secondaryHeader_ispType__parseSelf(&instance->secondaryHeader, pstate);
    if (pstate->pu.error) return;
    sourceData_ispType__parseSelf(&instance->sourceData, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->errorControl, 16, pstate);
    if (pstate->pu.error) return;
}

static void
isp__unparseSelf(const isp_ *instance, UState *ustate)
{
    primaryHeader_ispType__unparseSelf(&instance->primaryHeader, ustate);
    if (ustate->pu.error) return;
    secondaryHeader_ispType__unparseSelf(&instance->secondaryHeader, ustate);
    if (ustate->pu.error) return;
    sourceData_ispType__unparseSelf(&instance->sourceData, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->errorControl, 16, ustate);
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

