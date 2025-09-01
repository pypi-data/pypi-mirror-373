// auto-maintained by iwyu
// clang-format off
#include "generated_s1_ancillary.h"
#include <stdbool.h>    // for false, bool, true
#include <stddef.h>     // for NULL, size_t
#include <string.h>     // for memcmp, memset
#include "errors.h"     // for Error, PState, UState, ERR_CHOICE_KEY, Error::(anonymous), UNUSED
#include "parsers.h"    // for alloc_hexBinary, parse_hexBinary, parse_be_float, parse_be_int16, parse_be_bool32, parse_be_bool16, parse_be_int32, parse_be_uint16, parse_be_uint32, parse_le_bool32, parse_le_int64, parse_le_uint16, parse_le_uint8, parse_be_bool8, parse_be_double, parse_be_int64, parse_be_int8, parse_be_uint64, parse_be_uint8, parse_le_bool16, parse_le_bool8, parse_le_double, parse_le_float, parse_le_int16, parse_le_int32, parse_le_int8, parse_le_uint32, parse_le_uint64
#include "unparsers.h"  // for unparse_hexBinary, unparse_be_float, unparse_be_int16, unparse_be_bool32, unparse_be_bool16, unparse_be_int32, unparse_be_uint16, unparse_be_uint32, unparse_le_bool32, unparse_le_int64, unparse_le_uint16, unparse_le_uint8, unparse_be_bool8, unparse_be_double, unparse_be_int64, unparse_be_int8, unparse_be_uint64, unparse_be_uint8, unparse_le_bool16, unparse_le_bool8, unparse_le_double, unparse_le_float, unparse_le_int16, unparse_le_int32, unparse_le_int8, unparse_le_uint32, unparse_le_uint64
#include "validators.h" // for validate_array_bounds, validate_fixed_attribute, validate_floatpt_enumeration, validate_integer_enumeration, validate_schema_range
// clang-format on

// Declare prototypes for easier compilation

static void PVT_GPS_TIME_ancillaryType__parseSelf(PVT_GPS_TIME_ancillaryType_ *instance, PState *pstate);
static void PVT_GPS_TIME_ancillaryType__unparseSelf(const PVT_GPS_TIME_ancillaryType_ *instance, UState *ustate);
static void ATT_GPS_TIME_ancillaryType__parseSelf(ATT_GPS_TIME_ancillaryType_ *instance, PState *pstate);
static void ATT_GPS_TIME_ancillaryType__unparseSelf(const ATT_GPS_TIME_ancillaryType_ *instance, UState *ustate);
static void pointingStatus_ancillaryType__parseSelf(pointingStatus_ancillaryType_ *instance, PState *pstate);
static void pointingStatus_ancillaryType__unparseSelf(const pointingStatus_ancillaryType_ *instance, UState *ustate);
static void array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__parseSelf(temperatureStatus_ancillaryType_ *instance, PState *pstate);
static void array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__unparseSelf(const temperatureStatus_ancillaryType_ *instance, UState *ustate);
static size_t array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__getArraySize(const temperatureStatus_ancillaryType_ *instance);
static void temperatureStatus_ancillaryType__parseSelf(temperatureStatus_ancillaryType_ *instance, PState *pstate);
static void temperatureStatus_ancillaryType__unparseSelf(const temperatureStatus_ancillaryType_ *instance, UState *ustate);
static void temperatureTile_ancillaryType__parseSelf(temperatureTile_ancillaryType_ *instance, PState *pstate);
static void temperatureTile_ancillaryType__unparseSelf(const temperatureTile_ancillaryType_ *instance, UState *ustate);
static void array_temperatureTile_ancillaryType_ancillary__parseSelf(ancillary_ *instance, PState *pstate);
static void array_temperatureTile_ancillaryType_ancillary__unparseSelf(const ancillary_ *instance, UState *ustate);
static size_t array_temperatureTile_ancillaryType_ancillary__getArraySize(const ancillary_ *instance);
static void ancillary__parseSelf(ancillary_ *instance, PState *pstate);
static void ancillary__unparseSelf(const ancillary_ *instance, UState *ustate);

// Define schema version (will be empty if schema did not define any version string)

const char *schema_version = "";

// Define metadata for the infoset

static const ERD POS_X_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "POS_X", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD POS_Y_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "POS_Y", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD POS_Z_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "POS_Z", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_DOUBLE, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD VEL_X_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "VEL_X", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD VEL_Y_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "VEL_Y", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD VEL_Z_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "VEL_Z", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding1_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding1", // namedQName.local
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

static const PVT_GPS_TIME_ancillaryType_ PVT_GPS_TIME_ancillaryType__compute_offsets;

static const size_t PVT_GPS_TIME_ancillaryType__childrenOffsets[2] = {
    (const char *)&PVT_GPS_TIME_ancillaryType__compute_offsets.coarse - (const char *)&PVT_GPS_TIME_ancillaryType__compute_offsets,
    (const char *)&PVT_GPS_TIME_ancillaryType__compute_offsets.fine - (const char *)&PVT_GPS_TIME_ancillaryType__compute_offsets
};

static const ERD *const PVT_GPS_TIME_ancillaryType__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD PVT_GPS_TIME_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "PVT_GPS_TIME", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    PVT_GPS_TIME_ancillaryType__childrenOffsets,
    PVT_GPS_TIME_ancillaryType__childrenERDs,
    (ERDParseSelf)&PVT_GPS_TIME_ancillaryType__parseSelf,
    (ERDUnparseSelf)&PVT_GPS_TIME_ancillaryType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD ATT_Q0_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "ATT_Q0", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD ATT_Q1_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "ATT_Q1", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD ATT_Q2_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "ATT_Q2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD ATT_Q3_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "ATT_Q3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SC_RATE_WX_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "SC_RATE_WX", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SC_RATE_WY_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "SC_RATE_WY", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD SC_RATE_WZ_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "SC_RATE_WZ", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_FLOAT, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding2_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding2", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ATT_GPS_TIME_ancillaryType_ ATT_GPS_TIME_ancillaryType__compute_offsets;

static const size_t ATT_GPS_TIME_ancillaryType__childrenOffsets[2] = {
    (const char *)&ATT_GPS_TIME_ancillaryType__compute_offsets.coarse - (const char *)&ATT_GPS_TIME_ancillaryType__compute_offsets,
    (const char *)&ATT_GPS_TIME_ancillaryType__compute_offsets.fine - (const char *)&ATT_GPS_TIME_ancillaryType__compute_offsets
};

static const ERD *const ATT_GPS_TIME_ancillaryType__childrenERDs[2] = {
    &coarse_cucTime_ERD,
    &fine_cucTime_ERD
};

static const ERD ATT_GPS_TIME_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "ATT_GPS_TIME", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    2, // numChildren
    ATT_GPS_TIME_ancillaryType__childrenOffsets,
    ATT_GPS_TIME_ancillaryType__childrenERDs,
    (ERDParseSelf)&ATT_GPS_TIME_ancillaryType__parseSelf,
    (ERDUnparseSelf)&ATT_GPS_TIME_ancillaryType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD AOCS_OP_MODE_pointingStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "AOCS_OP_MODE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD _padding_pointingStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD RE_pointingStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "RE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD PE_pointingStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "PE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD YE_pointingStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "YE", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const pointingStatus_ancillaryType_ pointingStatus_ancillaryType__compute_offsets;

static const size_t pointingStatus_ancillaryType__childrenOffsets[5] = {
    (const char *)&pointingStatus_ancillaryType__compute_offsets.AOCS_OP_MODE - (const char *)&pointingStatus_ancillaryType__compute_offsets,
    (const char *)&pointingStatus_ancillaryType__compute_offsets._padding - (const char *)&pointingStatus_ancillaryType__compute_offsets,
    (const char *)&pointingStatus_ancillaryType__compute_offsets.RE - (const char *)&pointingStatus_ancillaryType__compute_offsets,
    (const char *)&pointingStatus_ancillaryType__compute_offsets.PE - (const char *)&pointingStatus_ancillaryType__compute_offsets,
    (const char *)&pointingStatus_ancillaryType__compute_offsets.YE - (const char *)&pointingStatus_ancillaryType__compute_offsets
};

static const ERD *const pointingStatus_ancillaryType__childrenERDs[5] = {
    &AOCS_OP_MODE_pointingStatusType_ERD,
    &_padding_pointingStatusType_ERD,
    &RE_pointingStatusType_ERD,
    &PE_pointingStatusType_ERD,
    &YE_pointingStatusType_ERD
};

static const ERD pointingStatus_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "pointingStatus", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    5, // numChildren
    pointingStatus_ancillaryType__childrenOffsets,
    pointingStatus_ancillaryType__childrenERDs,
    (ERDParseSelf)&pointingStatus_ancillaryType__parseSelf,
    (ERDUnparseSelf)&pointingStatus_ancillaryType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD _padding_temperatureHKUpdateStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD TGU_temperatureHKUpdateStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "TGU", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD Tile_temperatureHKUpdateStatusType_ERD = {
    {
        NULL, // namedQName.prefix
        "Tile", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const temperatureStatus_ancillaryType_ array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__compute_offsets;

static const size_t array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__childrenOffsets[1] = {
    (const char *)&array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__compute_offsets.Tile[1] - (const char *)&array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__compute_offsets.Tile[0]
};

static const ERD *const array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__childrenERDs[1] = {
    &Tile_temperatureHKUpdateStatusType_ERD
};

static const ERD array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "Tile", // namedQName.local
        NULL, // namedQName.ns
    },
    ARRAY, // typeCode
    14, // maxOccurs
    array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__childrenOffsets,
    array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__childrenERDs,
    (ERDParseSelf)&array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__parseSelf,
    (ERDUnparseSelf)&array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__unparseSelf,
    {.getArraySize = (GetArraySize)&array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__getArraySize}
};

static const temperatureStatus_ancillaryType_ temperatureStatus_ancillaryType__compute_offsets;

static const size_t temperatureStatus_ancillaryType__childrenOffsets[3] = {
    (const char *)&temperatureStatus_ancillaryType__compute_offsets._padding - (const char *)&temperatureStatus_ancillaryType__compute_offsets,
    (const char *)&temperatureStatus_ancillaryType__compute_offsets.TGU - (const char *)&temperatureStatus_ancillaryType__compute_offsets,
    (const char *)&temperatureStatus_ancillaryType__compute_offsets.Tile[0] - (const char *)&temperatureStatus_ancillaryType__compute_offsets
};

static const ERD *const temperatureStatus_ancillaryType__childrenERDs[3] = {
    &_padding_temperatureHKUpdateStatusType_ERD,
    &TGU_temperatureHKUpdateStatusType_ERD,
    &array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType_ERD
};

static const ERD temperatureStatus_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "temperatureStatus", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    3, // numChildren
    temperatureStatus_ancillaryType__childrenOffsets,
    temperatureStatus_ancillaryType__childrenERDs,
    (ERDParseSelf)&temperatureStatus_ancillaryType__parseSelf,
    (ERDUnparseSelf)&temperatureStatus_ancillaryType__unparseSelf,
    {.initChoice = NULL}
};

static const ERD EFE_H_temperatureTileType_ERD = {
    {
        NULL, // namedQName.prefix
        "EFE_H", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD EFE_V_temperatureTileType_ERD = {
    {
        NULL, // namedQName.prefix
        "EFE_V", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD ACTIVE_TA_temperatureTileType_ERD = {
    {
        NULL, // namedQName.prefix
        "ACTIVE_TA", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const temperatureTile_ancillaryType_ temperatureTile_ancillaryType__compute_offsets;

static const size_t temperatureTile_ancillaryType__childrenOffsets[3] = {
    (const char *)&temperatureTile_ancillaryType__compute_offsets.EFE_H - (const char *)&temperatureTile_ancillaryType__compute_offsets,
    (const char *)&temperatureTile_ancillaryType__compute_offsets.EFE_V - (const char *)&temperatureTile_ancillaryType__compute_offsets,
    (const char *)&temperatureTile_ancillaryType__compute_offsets.ACTIVE_TA - (const char *)&temperatureTile_ancillaryType__compute_offsets
};

static const ERD *const temperatureTile_ancillaryType__childrenERDs[3] = {
    &EFE_H_temperatureTileType_ERD,
    &EFE_V_temperatureTileType_ERD,
    &ACTIVE_TA_temperatureTileType_ERD
};

static const ERD temperatureTile_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "temperatureTile", // namedQName.local
        NULL, // namedQName.ns
    },
    COMPLEX, // typeCode
    3, // numChildren
    temperatureTile_ancillaryType__childrenOffsets,
    temperatureTile_ancillaryType__childrenERDs,
    (ERDParseSelf)&temperatureTile_ancillaryType__parseSelf,
    (ERDUnparseSelf)&temperatureTile_ancillaryType__unparseSelf,
    {.initChoice = NULL}
};

static const ancillary_ array_temperatureTile_ancillaryType_ancillary__compute_offsets;

static const size_t array_temperatureTile_ancillaryType_ancillary__childrenOffsets[1] = {
    (const char *)&array_temperatureTile_ancillaryType_ancillary__compute_offsets.temperatureTile[1] - (const char *)&array_temperatureTile_ancillaryType_ancillary__compute_offsets.temperatureTile[0]
};

static const ERD *const array_temperatureTile_ancillaryType_ancillary__childrenERDs[1] = {
    &temperatureTile_ancillaryType_ERD
};

static const ERD array_temperatureTile_ancillaryType_ancillary_ERD = {
    {
        NULL, // namedQName.prefix
        "temperatureTile", // namedQName.local
        NULL, // namedQName.ns
    },
    ARRAY, // typeCode
    14, // maxOccurs
    array_temperatureTile_ancillaryType_ancillary__childrenOffsets,
    array_temperatureTile_ancillaryType_ancillary__childrenERDs,
    (ERDParseSelf)&array_temperatureTile_ancillaryType_ancillary__parseSelf,
    (ERDUnparseSelf)&array_temperatureTile_ancillaryType_ancillary__unparseSelf,
    {.getArraySize = (GetArraySize)&array_temperatureTile_ancillaryType_ancillary__getArraySize}
};

static const ERD _padding3_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "_padding3", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT16, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ERD temperatureTGU_ancillaryType_ERD = {
    {
        NULL, // namedQName.prefix
        "temperatureTGU", // namedQName.local
        NULL, // namedQName.ns
    },
    PRIMITIVE_UINT8, // typeCode
    0, NULL, NULL, NULL, NULL, {NULL}
};

static const ancillary_ ancillary__compute_offsets;

static const size_t ancillary__childrenOffsets[22] = {
    (const char *)&ancillary__compute_offsets.POS_X - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.POS_Y - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.POS_Z - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.VEL_X - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.VEL_Y - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.VEL_Z - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets._padding1 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.PVT_GPS_TIME - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.ATT_Q0 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.ATT_Q1 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.ATT_Q2 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.ATT_Q3 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.SC_RATE_WX - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.SC_RATE_WY - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.SC_RATE_WZ - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets._padding2 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.ATT_GPS_TIME - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.pointingStatus - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.temperatureStatus - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.temperatureTile[0] - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets._padding3 - (const char *)&ancillary__compute_offsets,
    (const char *)&ancillary__compute_offsets.temperatureTGU - (const char *)&ancillary__compute_offsets
};

static const ERD *const ancillary__childrenERDs[22] = {
    &POS_X_ancillaryType_ERD,
    &POS_Y_ancillaryType_ERD,
    &POS_Z_ancillaryType_ERD,
    &VEL_X_ancillaryType_ERD,
    &VEL_Y_ancillaryType_ERD,
    &VEL_Z_ancillaryType_ERD,
    &_padding1_ancillaryType_ERD,
    &PVT_GPS_TIME_ancillaryType_ERD,
    &ATT_Q0_ancillaryType_ERD,
    &ATT_Q1_ancillaryType_ERD,
    &ATT_Q2_ancillaryType_ERD,
    &ATT_Q3_ancillaryType_ERD,
    &SC_RATE_WX_ancillaryType_ERD,
    &SC_RATE_WY_ancillaryType_ERD,
    &SC_RATE_WZ_ancillaryType_ERD,
    &_padding2_ancillaryType_ERD,
    &ATT_GPS_TIME_ancillaryType_ERD,
    &pointingStatus_ancillaryType_ERD,
    &temperatureStatus_ancillaryType_ERD,
    &array_temperatureTile_ancillaryType_ancillary_ERD,
    &_padding3_ancillaryType_ERD,
    &temperatureTGU_ancillaryType_ERD
};

static const ERD ancillary_ERD = {
    {
        NULL, // namedQName.prefix
        "ancillary", // namedQName.local
        "http://www.esa.int/safe/sentinel-1.0/", // namedQName.ns
    },
    COMPLEX, // typeCode
    22, // numChildren
    ancillary__childrenOffsets,
    ancillary__childrenERDs,
    (ERDParseSelf)&ancillary__parseSelf,
    (ERDUnparseSelf)&ancillary__unparseSelf,
    {.initChoice = NULL}
};

// Initialize, parse, and unparse nodes of the infoset

static void
PVT_GPS_TIME_ancillaryType__initERD(PVT_GPS_TIME_ancillaryType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &PVT_GPS_TIME_ancillaryType_ERD;
    instance->_base.parent = parent;
}

static void
PVT_GPS_TIME_ancillaryType__parseSelf(PVT_GPS_TIME_ancillaryType_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
PVT_GPS_TIME_ancillaryType__unparseSelf(const PVT_GPS_TIME_ancillaryType_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
ATT_GPS_TIME_ancillaryType__initERD(ATT_GPS_TIME_ancillaryType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &ATT_GPS_TIME_ancillaryType_ERD;
    instance->_base.parent = parent;
}

static void
ATT_GPS_TIME_ancillaryType__parseSelf(ATT_GPS_TIME_ancillaryType_ *instance, PState *pstate)
{
    parse_be_uint32(&instance->coarse, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint32(&instance->fine, 24, pstate);
    if (pstate->pu.error) return;
}

static void
ATT_GPS_TIME_ancillaryType__unparseSelf(const ATT_GPS_TIME_ancillaryType_ *instance, UState *ustate)
{
    unparse_be_uint32(instance->coarse, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint32(instance->fine, 24, ustate);
    if (ustate->pu.error) return;
}

static void
pointingStatus_ancillaryType__initERD(pointingStatus_ancillaryType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &pointingStatus_ancillaryType_ERD;
    instance->_base.parent = parent;
}

static void
pointingStatus_ancillaryType__parseSelf(pointingStatus_ancillaryType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->AOCS_OP_MODE, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding, 5, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->RE, 1, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->PE, 1, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->YE, 1, pstate);
    if (pstate->pu.error) return;
}

static void
pointingStatus_ancillaryType__unparseSelf(const pointingStatus_ancillaryType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->AOCS_OP_MODE, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding, 5, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->RE, 1, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->PE, 1, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->YE, 1, ustate);
    if (ustate->pu.error) return;
}

static void
array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__initERD(temperatureStatus_ancillaryType_ *instance, InfosetBase *parent)
{
    UNUSED(instance);
    UNUSED(parent);
}

static void
array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__parseSelf(temperatureStatus_ancillaryType_ *instance, PState *pstate)
{
    const size_t arraySize = array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__getArraySize(instance);
    validate_array_bounds("array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType_", arraySize, 14, 14, &pstate->pu);
    if (pstate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        parse_be_uint8(&instance->Tile[i], 1, pstate);
        if (pstate->pu.error) return;
    }
}

static void
array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__unparseSelf(const temperatureStatus_ancillaryType_ *instance, UState *ustate)
{
    const size_t arraySize = array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__getArraySize(instance);
    validate_array_bounds("array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType_", arraySize, 14, 14, &ustate->pu);
    if (ustate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        unparse_be_uint8(instance->Tile[i], 1, ustate);
        if (ustate->pu.error) return;
    }
}

static size_t
array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__getArraySize(const temperatureStatus_ancillaryType_ *instance)
{
    UNUSED(instance);
    return 14;
}

static void
temperatureStatus_ancillaryType__initERD(temperatureStatus_ancillaryType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &temperatureStatus_ancillaryType_ERD;
    instance->_base.parent = parent;
    array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__initERD(instance, parent);
}

static void
temperatureStatus_ancillaryType__parseSelf(temperatureStatus_ancillaryType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->_padding, 1, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->TGU, 1, pstate);
    if (pstate->pu.error) return;
    array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__parseSelf(instance, pstate);
    if (pstate->pu.error) return;
}

static void
temperatureStatus_ancillaryType__unparseSelf(const temperatureStatus_ancillaryType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->_padding, 1, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->TGU, 1, ustate);
    if (ustate->pu.error) return;
    array_Tile_temperatureHKUpdateStatusType_temperatureStatus_ancillaryType__unparseSelf(instance, ustate);
    if (ustate->pu.error) return;
}

static void
temperatureTile_ancillaryType__initERD(temperatureTile_ancillaryType_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &temperatureTile_ancillaryType_ERD;
    instance->_base.parent = parent;
}

static void
temperatureTile_ancillaryType__parseSelf(temperatureTile_ancillaryType_ *instance, PState *pstate)
{
    parse_be_uint8(&instance->EFE_H, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->EFE_V, 8, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->ACTIVE_TA, 8, pstate);
    if (pstate->pu.error) return;
}

static void
temperatureTile_ancillaryType__unparseSelf(const temperatureTile_ancillaryType_ *instance, UState *ustate)
{
    unparse_be_uint8(instance->EFE_H, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->EFE_V, 8, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->ACTIVE_TA, 8, ustate);
    if (ustate->pu.error) return;
}

static void
array_temperatureTile_ancillaryType_ancillary__initERD(ancillary_ *instance, InfosetBase *parent)
{
    UNUSED(parent);
    for (size_t i = 0; i < 14; i++)
    {
        temperatureTile_ancillaryType__initERD(&instance->temperatureTile[i], (InfosetBase *)instance);
    }
}

static void
array_temperatureTile_ancillaryType_ancillary__parseSelf(ancillary_ *instance, PState *pstate)
{
    const size_t arraySize = array_temperatureTile_ancillaryType_ancillary__getArraySize(instance);
    validate_array_bounds("array_temperatureTile_ancillaryType_ancillary_", arraySize, 14, 14, &pstate->pu);
    if (pstate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        temperatureTile_ancillaryType__parseSelf(&instance->temperatureTile[i], pstate);
        if (pstate->pu.error) return;
    }
}

static void
array_temperatureTile_ancillaryType_ancillary__unparseSelf(const ancillary_ *instance, UState *ustate)
{
    const size_t arraySize = array_temperatureTile_ancillaryType_ancillary__getArraySize(instance);
    validate_array_bounds("array_temperatureTile_ancillaryType_ancillary_", arraySize, 14, 14, &ustate->pu);
    if (ustate->pu.error) return;

    for (size_t i = 0; i < arraySize; i++)
    {
        temperatureTile_ancillaryType__unparseSelf(&instance->temperatureTile[i], ustate);
        if (ustate->pu.error) return;
    }
}

static size_t
array_temperatureTile_ancillaryType_ancillary__getArraySize(const ancillary_ *instance)
{
    UNUSED(instance);
    return 14;
}

static void
ancillary__initERD(ancillary_ *instance, InfosetBase *parent)
{
    instance->_base.erd = &ancillary_ERD;
    instance->_base.parent = parent;
    PVT_GPS_TIME_ancillaryType__initERD(&instance->PVT_GPS_TIME, (InfosetBase *)instance);
    ATT_GPS_TIME_ancillaryType__initERD(&instance->ATT_GPS_TIME, (InfosetBase *)instance);
    pointingStatus_ancillaryType__initERD(&instance->pointingStatus, (InfosetBase *)instance);
    temperatureStatus_ancillaryType__initERD(&instance->temperatureStatus, (InfosetBase *)instance);
    array_temperatureTile_ancillaryType_ancillary__initERD(instance, parent);
}

static void
ancillary__parseSelf(ancillary_ *instance, PState *pstate)
{
    parse_be_double(&instance->POS_X, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->POS_Y, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_double(&instance->POS_Z, 64, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->VEL_X, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->VEL_Y, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->VEL_Z, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding1, 8, pstate);
    if (pstate->pu.error) return;
    PVT_GPS_TIME_ancillaryType__parseSelf(&instance->PVT_GPS_TIME, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->ATT_Q0, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->ATT_Q1, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->ATT_Q2, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->ATT_Q3, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->SC_RATE_WX, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->SC_RATE_WY, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_float(&instance->SC_RATE_WZ, 32, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->_padding2, 8, pstate);
    if (pstate->pu.error) return;
    ATT_GPS_TIME_ancillaryType__parseSelf(&instance->ATT_GPS_TIME, pstate);
    if (pstate->pu.error) return;
    pointingStatus_ancillaryType__parseSelf(&instance->pointingStatus, pstate);
    if (pstate->pu.error) return;
    temperatureStatus_ancillaryType__parseSelf(&instance->temperatureStatus, pstate);
    if (pstate->pu.error) return;
    array_temperatureTile_ancillaryType_ancillary__parseSelf(instance, pstate);
    if (pstate->pu.error) return;
    parse_be_uint16(&instance->_padding3, 9, pstate);
    if (pstate->pu.error) return;
    parse_be_uint8(&instance->temperatureTGU, 7, pstate);
    if (pstate->pu.error) return;
}

static void
ancillary__unparseSelf(const ancillary_ *instance, UState *ustate)
{
    unparse_be_double(instance->POS_X, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->POS_Y, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_double(instance->POS_Z, 64, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->VEL_X, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->VEL_Y, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->VEL_Z, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding1, 8, ustate);
    if (ustate->pu.error) return;
    PVT_GPS_TIME_ancillaryType__unparseSelf(&instance->PVT_GPS_TIME, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->ATT_Q0, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->ATT_Q1, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->ATT_Q2, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->ATT_Q3, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->SC_RATE_WX, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->SC_RATE_WY, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_float(instance->SC_RATE_WZ, 32, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->_padding2, 8, ustate);
    if (ustate->pu.error) return;
    ATT_GPS_TIME_ancillaryType__unparseSelf(&instance->ATT_GPS_TIME, ustate);
    if (ustate->pu.error) return;
    pointingStatus_ancillaryType__unparseSelf(&instance->pointingStatus, ustate);
    if (ustate->pu.error) return;
    temperatureStatus_ancillaryType__unparseSelf(&instance->temperatureStatus, ustate);
    if (ustate->pu.error) return;
    array_temperatureTile_ancillaryType_ancillary__unparseSelf(instance, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint16(instance->_padding3, 9, ustate);
    if (ustate->pu.error) return;
    unparse_be_uint8(instance->temperatureTGU, 7, ustate);
    if (ustate->pu.error) return;
}

// Get an infoset (optionally clearing it first) for parsing/walking

InfosetBase *
get_infoset(bool clear_infoset)
{
    static ancillary_ infoset;

    if (clear_infoset)
    {
        // If your infoset contains hexBinary prefixed length elements,
        // you may want to walk infoset first to free their malloc'ed
        // storage - we are not handling that case for now...
        memset(&infoset, 0, sizeof(infoset));
        ancillary__initERD(&infoset, (InfosetBase *)&infoset);
    }

    return &infoset._base;
}

const int packet_size = 128;

