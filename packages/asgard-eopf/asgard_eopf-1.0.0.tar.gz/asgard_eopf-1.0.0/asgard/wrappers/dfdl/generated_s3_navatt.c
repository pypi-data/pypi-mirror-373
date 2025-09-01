// auto-maintained by iwyu
// clang-format off
#include "generated_s3_navatt.h"
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
static void PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__parseSelf(PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ *instance, PState *pstate);
static void PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__unparseSelf(const PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ *instance, UState *ustate);
static void PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__parseSelf(PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ *instance, PState *pstate);
static void PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__unparseSelf(const PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ *instance, UState *ustate);
static void SPACECRAFT_CENTRAL_TIME_navatt__parseSelf(SPACECRAFT_CENTRAL_TIME_navatt_ *instance, PState *pstate);
static void SPACECRAFT_CENTRAL_TIME_navatt__unparseSelf(const SPACECRAFT_CENTRAL_TIME_navatt_ *instance, UState *ustate);
static void sourceData_ispType__parseSelf(sourceData_ispType_ *instance, PState *pstate);
static void sourceData_ispType__unparseSelf(const sourceData_ispType_ *instance, UState *ustate);
static void measurements__parseSelf(measurements_ *instance, PState *pstate);
static void measurements__unparseSelf(const measurements_ *instance, UState *ustate);

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

static const ERD cswField_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "cswField", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PM_DAT_GNSS_TIME_VALIDITY_FLAG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "PM_DAT_GNSS_TIME_VALIDITY_FLAG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_HEXBINARY, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__compute_offsets;

static const size_t PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__childrenOffsets[2] = {
    (const char *)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__compute_offsets.coarse - (const char *)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__compute_offsets,
    (const char *)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__compute_offsets.fine - (const char *)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__compute_offsets
};

static const ERD *const PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "PM_DAT_NAVATT_CORRELATION_PPS_OBT", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__childrenOffsets,
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__childrenERDs,
    (ERDParseSelf)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__parseSelf,
    (ERDUnparseSelf)&PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__unparseSelf,
    {.initChoice = NULL}
};

static const PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__compute_offsets;

static const size_t PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__childrenOffsets[2] = {
    (const char *)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__compute_offsets.coarse - (const char *)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__compute_offsets,
    (const char *)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__compute_offsets.fine - (const char *)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__compute_offsets
};

static const ERD *const PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "PM_DAT_NAVATT_CORRELATION_GNSS_TIME", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__childrenOffsets,
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__childrenERDs,
    (ERDParseSelf)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__parseSelf,
    (ERDUnparseSelf)&PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__unparseSelf,
    {.initChoice = NULL}
};

static const SPACECRAFT_CENTRAL_TIME_navatt_ SPACECRAFT_CENTRAL_TIME_navatt__compute_offsets;

static const size_t SPACECRAFT_CENTRAL_TIME_navatt__childrenOffsets[2] = {
    (const char *)&SPACECRAFT_CENTRAL_TIME_navatt__compute_offsets.coarse - (const char *)&SPACECRAFT_CENTRAL_TIME_navatt__compute_offsets,
    (const char *)&SPACECRAFT_CENTRAL_TIME_navatt__compute_offsets.fine - (const char *)&SPACECRAFT_CENTRAL_TIME_navatt__compute_offsets
};

static const ERD *const SPACECRAFT_CENTRAL_TIME_navatt__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD SPACECRAFT_CENTRAL_TIME_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "SPACECRAFT_CENTRAL_TIME", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    SPACECRAFT_CENTRAL_TIME_navatt__childrenOffsets,
    SPACECRAFT_CENTRAL_TIME_navatt__childrenERDs,
    (ERDParseSelf)&SPACECRAFT_CENTRAL_TIME_navatt__parseSelf,
    (ERDUnparseSelf)&SPACECRAFT_CENTRAL_TIME_navatt__unparseSelf,
    {.initChoice = NULL}
};

static const ERD AO_DAT_I_POS_I_SC_EST_1_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_POS_I_SC_EST_1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_I_POS_I_SC_EST_2_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_POS_I_SC_EST_2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_I_POS_I_SC_EST_3_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_POS_I_SC_EST_3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_I_VEL_I_SC_EST_1_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_VEL_I_SC_EST_1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_I_VEL_I_SC_EST_2_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_VEL_I_SC_EST_2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_I_VEL_I_SC_EST_3_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_I_VEL_I_SC_EST_3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_I_SC_EST_1_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_I_SC_EST_1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_I_SC_EST_2_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_I_SC_EST_2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_I_SC_EST_3_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_I_SC_EST_3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_I_SC_EST_4_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_I_SC_EST_4", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_SC_RATE_I_SC_EST_1_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_SC_RATE_I_SC_EST_1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_SC_RATE_I_SC_EST_2_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_SC_RATE_I_SC_EST_2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_SC_RATE_I_SC_EST_3_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_SC_RATE_I_SC_EST_3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_SC_ERR_1_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_SC_ERR_1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_SC_ERR_2_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_SC_ERR_2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_SC_ERR_3_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_SC_ERR_3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_Q_SC_ERR_4_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_Q_SC_ERR_4", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_GDCMODEFLG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_GDCMODEFLG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SPACECRAFT_MODE_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "SPACECRAFT_MODE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_THRUST_FLG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_THRUST_FLG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_AJ_IP_OP_FLG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_AJ_IP_OP_FLG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_GNSS_VALIDDATA_ITG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_GNSS_VALIDDATA_ITG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_NAVATT_ORBITNUMBER_EST_ITG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_NAVATT_ORBITNUMBER_EST_ITG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_NAVATT_OOP_EST_ITG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_NAVATT_OOP_EST_ITG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT32, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD AO_DAT_NEWGNSSDATAFLG_ITG_navatt_ERD = {
    {
        NULL, // namedQName.prefix
        "AO_DAT_NEWGNSSDATAFLG_ITG", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const sourceData_ispType_ sourceData_ispType__compute_offsets;

static const size_t sourceData_ispType__childrenOffsets[30] = {
    (const char *)&sourceData_ispType__compute_offsets.cswField - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.PM_DAT_GNSS_TIME_VALIDITY_FLAG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.PM_DAT_NAVATT_CORRELATION_PPS_OBT - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.PM_DAT_NAVATT_CORRELATION_GNSS_TIME - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.SPACECRAFT_CENTRAL_TIME - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_POS_I_SC_EST_1 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_POS_I_SC_EST_2 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_POS_I_SC_EST_3 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_VEL_I_SC_EST_1 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_VEL_I_SC_EST_2 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_I_VEL_I_SC_EST_3 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_I_SC_EST_1 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_I_SC_EST_2 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_I_SC_EST_3 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_I_SC_EST_4 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_SC_RATE_I_SC_EST_1 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_SC_RATE_I_SC_EST_2 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_SC_RATE_I_SC_EST_3 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_SC_ERR_1 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_SC_ERR_2 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_SC_ERR_3 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_Q_SC_ERR_4 - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_GDCMODEFLG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.SPACECRAFT_MODE - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_THRUST_FLG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_AJ_IP_OP_FLG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_GNSS_VALIDDATA_ITG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_NAVATT_ORBITNUMBER_EST_ITG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_NAVATT_OOP_EST_ITG - (const char *)&sourceData_ispType__compute_offsets,
    (const char *)&sourceData_ispType__compute_offsets.AO_DAT_NEWGNSSDATAFLG_ITG - (const char *)&sourceData_ispType__compute_offsets
};

static const ERD *const sourceData_ispType__childrenERDs[30] = {
    &cswField_navatt_ERD,
    &PM_DAT_GNSS_TIME_VALIDITY_FLAG_navatt_ERD,
    &PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ERD,
    &PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ERD,
    &SPACECRAFT_CENTRAL_TIME_navatt_ERD,
    &AO_DAT_I_POS_I_SC_EST_1_navatt_ERD,
    &AO_DAT_I_POS_I_SC_EST_2_navatt_ERD,
    &AO_DAT_I_POS_I_SC_EST_3_navatt_ERD,
    &AO_DAT_I_VEL_I_SC_EST_1_navatt_ERD,
    &AO_DAT_I_VEL_I_SC_EST_2_navatt_ERD,
    &AO_DAT_I_VEL_I_SC_EST_3_navatt_ERD,
    &AO_DAT_Q_I_SC_EST_1_navatt_ERD,
    &AO_DAT_Q_I_SC_EST_2_navatt_ERD,
    &AO_DAT_Q_I_SC_EST_3_navatt_ERD,
    &AO_DAT_Q_I_SC_EST_4_navatt_ERD,
    &AO_DAT_SC_RATE_I_SC_EST_1_navatt_ERD,
    &AO_DAT_SC_RATE_I_SC_EST_2_navatt_ERD,
    &AO_DAT_SC_RATE_I_SC_EST_3_navatt_ERD,
    &AO_DAT_Q_SC_ERR_1_navatt_ERD,
    &AO_DAT_Q_SC_ERR_2_navatt_ERD,
    &AO_DAT_Q_SC_ERR_3_navatt_ERD,
    &AO_DAT_Q_SC_ERR_4_navatt_ERD,
    &AO_DAT_GDCMODEFLG_navatt_ERD,
    &SPACECRAFT_MODE_navatt_ERD,
    &AO_DAT_THRUST_FLG_navatt_ERD,
    &AO_AJ_IP_OP_FLG_navatt_ERD,
    &AO_DAT_GNSS_VALIDDATA_ITG_navatt_ERD,
    &AO_DAT_NAVATT_ORBITNUMBER_EST_ITG_navatt_ERD,
    &AO_DAT_NAVATT_OOP_EST_ITG_navatt_ERD,
    &AO_DAT_NEWGNSSDATAFLG_ITG_navatt_ERD
};

static const ERD sourceData_ispType_ERD = {
    {
        NULL, // namedQName.prefix
        "sourceData", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    30, // numChildren
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

static const measurements_ measurements__compute_offsets;

static const size_t measurements__childrenOffsets[4] = {
    (const char *)&measurements__compute_offsets.primaryHeader - (const char *)&measurements__compute_offsets,
    (const char *)&measurements__compute_offsets.secondaryHeader - (const char *)&measurements__compute_offsets,
    (const char *)&measurements__compute_offsets.sourceData - (const char *)&measurements__compute_offsets,
    (const char *)&measurements__compute_offsets.errorControl - (const char *)&measurements__compute_offsets
};

static const ERD *const measurements__childrenERDs[4] = {
    &primaryHeader_ispType_ERD,
    &secondaryHeader_ispType_ERD,
    &sourceData_ispType_ERD,
    &errorControl_ispType_ERD
};

static const ERD measurements_ERD = {
    {
        NULL, // namedQName.prefix
        "measurements", // namedQName.local
        "http://www.esa.int/safe/sentinel-1.0/", // namedQName.ns
    },
    COMPLEX, // typeCode
    4, // numChildren
    measurements__childrenOffsets,
    measurements__childrenERDs,
    (ERDParseSelf)&measurements__parseSelf,
    (ERDUnparseSelf)&measurements__unparseSelf,
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
PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__initERD(PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ERD;
    instance->_base.parent = parent;
}

static void
PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__parseSelf(PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__unparseSelf(const PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__initERD(PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ERD;
    instance->_base.parent = parent;
}

static void
PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__parseSelf(PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__unparseSelf(const PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
SPACECRAFT_CENTRAL_TIME_navatt__initERD(SPACECRAFT_CENTRAL_TIME_navatt_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &SPACECRAFT_CENTRAL_TIME_navatt_ERD;
    instance->_base.parent = parent;
}

static void
SPACECRAFT_CENTRAL_TIME_navatt__parseSelf(SPACECRAFT_CENTRAL_TIME_navatt_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
SPACECRAFT_CENTRAL_TIME_navatt__unparseSelf(const SPACECRAFT_CENTRAL_TIME_navatt_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
sourceData_ispType__initERD(sourceData_ispType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &sourceData_ispType_ERD;
    instance->_base.parent = parent;
    instance->cswField.array = instance->_a_cswField;
    instance->cswField.lengthInBytes = sizeof(instance->_a_cswField);
    instance->cswField.dynamic = false;
    instance->PM_DAT_GNSS_TIME_VALIDITY_FLAG.array = instance->_a_PM_DAT_GNSS_TIME_VALIDITY_FLAG;
    instance->PM_DAT_GNSS_TIME_VALIDITY_FLAG.lengthInBytes = sizeof(instance->_a_PM_DAT_GNSS_TIME_VALIDITY_FLAG);
    instance->PM_DAT_GNSS_TIME_VALIDITY_FLAG.dynamic = false;
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__initERD(&instance->PM_DAT_NAVATT_CORRELATION_PPS_OBT, (InfosetBase *)instance);
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__initERD(&instance->PM_DAT_NAVATT_CORRELATION_GNSS_TIME, (InfosetBase *)instance);
    SPACECRAFT_CENTRAL_TIME_navatt__initERD(&instance->SPACECRAFT_CENTRAL_TIME, (InfosetBase *)instance);
}

static void
sourceData_ispType__parseSelf(sourceData_ispType_ *instance, PState *pstate)
{
    parse_hexBinary(&instance->cswField, pstate);
    if (pstate->pu.error) return;
    parse_hexBinary(&instance->PM_DAT_GNSS_TIME_VALIDITY_FLAG, pstate);
    if (pstate->pu.error) return;
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__parseSelf(&instance->PM_DAT_NAVATT_CORRELATION_PPS_OBT, pstate);
    if (pstate->pu.error) return;
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__parseSelf(&instance->PM_DAT_NAVATT_CORRELATION_GNSS_TIME, pstate);
    if (pstate->pu.error) return;
    SPACECRAFT_CENTRAL_TIME_navatt__parseSelf(&instance->SPACECRAFT_CENTRAL_TIME, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_POS_I_SC_EST_1, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_POS_I_SC_EST_2, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_POS_I_SC_EST_3, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_VEL_I_SC_EST_1, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_VEL_I_SC_EST_2, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_I_VEL_I_SC_EST_3, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_I_SC_EST_1, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_I_SC_EST_2, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_I_SC_EST_3, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_I_SC_EST_4, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_SC_RATE_I_SC_EST_1, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_SC_RATE_I_SC_EST_2, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_SC_RATE_I_SC_EST_3, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_SC_ERR_1, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_SC_ERR_2, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_SC_ERR_3, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->AO_DAT_Q_SC_ERR_4, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->AO_DAT_GDCMODEFLG, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->SPACECRAFT_MODE, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->AO_DAT_THRUST_FLG, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->AO_AJ_IP_OP_FLG, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->AO_DAT_GNSS_VALIDDATA_ITG, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->AO_DAT_NAVATT_ORBITNUMBER_EST_ITG, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->AO_DAT_NAVATT_OOP_EST_ITG, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->AO_DAT_NEWGNSSDATAFLG_ITG, 8, pstate);
    if (pstate->pu.error) return;
}

static void
sourceData_ispType__unparseSelf(const sourceData_ispType_ *instance, UState *ustate)
{
    unparse_hexBinary(instance->cswField, ustate);
    if (ustate->pu.error) return;
    unparse_hexBinary(instance->PM_DAT_GNSS_TIME_VALIDITY_FLAG, ustate);
    if (ustate->pu.error) return;
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt__unparseSelf(&instance->PM_DAT_NAVATT_CORRELATION_PPS_OBT, ustate);
    if (ustate->pu.error) return;
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt__unparseSelf(&instance->PM_DAT_NAVATT_CORRELATION_GNSS_TIME, ustate);
    if (ustate->pu.error) return;
    SPACECRAFT_CENTRAL_TIME_navatt__unparseSelf(&instance->SPACECRAFT_CENTRAL_TIME, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_POS_I_SC_EST_1, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_POS_I_SC_EST_2, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_POS_I_SC_EST_3, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_VEL_I_SC_EST_1, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_VEL_I_SC_EST_2, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_I_VEL_I_SC_EST_3, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_I_SC_EST_1, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_I_SC_EST_2, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_I_SC_EST_3, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_I_SC_EST_4, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_SC_RATE_I_SC_EST_1, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_SC_RATE_I_SC_EST_2, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_SC_RATE_I_SC_EST_3, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_SC_ERR_1, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_SC_ERR_2, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_SC_ERR_3, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->AO_DAT_Q_SC_ERR_4, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->AO_DAT_GDCMODEFLG, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->SPACECRAFT_MODE, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->AO_DAT_THRUST_FLG, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->AO_AJ_IP_OP_FLG, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->AO_DAT_GNSS_VALIDDATA_ITG, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->AO_DAT_NAVATT_ORBITNUMBER_EST_ITG, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->AO_DAT_NAVATT_OOP_EST_ITG, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->AO_DAT_NEWGNSSDATAFLG_ITG, 8, ustate);
    if (ustate->pu.error) return;
}

static void
measurements__initERD(measurements_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &measurements_ERD;
    instance->_base.parent = parent;
    primaryHeader_ispType__initERD(&instance->primaryHeader, (InfosetBase *)instance);
    secondaryHeader_ispType__initERD(&instance->secondaryHeader, (InfosetBase *)instance);
    sourceData_ispType__initERD(&instance->sourceData, (InfosetBase *)instance);
}

static void
measurements__parseSelf(measurements_ *instance, PState *pstate)
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
measurements__unparseSelf(const measurements_ *instance, UState *ustate)
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
    static measurements_ infoset;

    if (clear_infoset)
    {
        // If your infoset contains hexBinary prefixed length elements,
        // you may want to walk infoset first to free their malloc'ed
        // storage - we are not handling that case for now...
        memset(&infoset, 0, sizeof(infoset));
        measurements__initERD(&infoset, (InfosetBase *)&infoset);
    }

    return &infoset._base;
}

const int packet_size = 196;

