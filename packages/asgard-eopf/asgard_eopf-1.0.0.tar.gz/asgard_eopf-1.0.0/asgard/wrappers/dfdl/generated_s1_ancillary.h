#ifndef GENERATED_CODE_H
#define GENERATED_CODE_H

// auto-maintained by iwyu
// clang-format off
#include <stdbool.h>  // for bool
#include <stddef.h>   // for size_t
#include <stdint.h>   // for uint8_t, int16_t, int32_t, int64_t, uint32_t, int8_t, uint16_t, uint64_t
#include "infoset.h"  // for InfosetBase, HexBinary
// clang-format on

// Define schema version (will be empty if schema did not define any version string)

extern const char *schema_version;

// Define infoset structures

typedef struct PVT_GPS_TIME_ancillaryType_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} PVT_GPS_TIME_ancillaryType_;

typedef struct ATT_GPS_TIME_ancillaryType_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} ATT_GPS_TIME_ancillaryType_;

typedef struct pointingStatus_ancillaryType_
{
    InfosetBase _base;
    uint8_t     AOCS_OP_MODE;
    uint8_t     _padding;
    uint8_t     RE;
    uint8_t     PE;
    uint8_t     YE;
} pointingStatus_ancillaryType_;

typedef struct temperatureStatus_ancillaryType_
{
    InfosetBase _base;
    uint8_t     _padding;
    uint8_t     TGU;
    uint8_t     Tile[14];
} temperatureStatus_ancillaryType_;

typedef struct temperatureTile_ancillaryType_
{
    InfosetBase _base;
    uint8_t     EFE_H;
    uint8_t     EFE_V;
    uint8_t     ACTIVE_TA;
} temperatureTile_ancillaryType_;

typedef struct ancillary_
{
    InfosetBase _base;
    double      POS_X;
    double      POS_Y;
    double      POS_Z;
    float       VEL_X;
    float       VEL_Y;
    float       VEL_Z;
    uint8_t     _padding1;
    PVT_GPS_TIME_ancillaryType_ PVT_GPS_TIME;
    float       ATT_Q0;
    float       ATT_Q1;
    float       ATT_Q2;
    float       ATT_Q3;
    float       SC_RATE_WX;
    float       SC_RATE_WY;
    float       SC_RATE_WZ;
    uint8_t     _padding2;
    ATT_GPS_TIME_ancillaryType_ ATT_GPS_TIME;
    pointingStatus_ancillaryType_ pointingStatus;
    temperatureStatus_ancillaryType_ temperatureStatus;
    temperatureTile_ancillaryType_ temperatureTile[14];
    uint16_t    _padding3;
    uint8_t     temperatureTGU;
} ancillary_;

#endif // GENERATED_CODE_H
