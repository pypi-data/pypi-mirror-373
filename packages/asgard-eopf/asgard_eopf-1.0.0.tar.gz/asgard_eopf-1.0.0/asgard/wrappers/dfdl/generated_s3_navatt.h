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

typedef struct primaryHeader_ispType_
{
    InfosetBase _base;
    uint8_t     packetVersionNumber;
    uint8_t     packetType;
    uint8_t     dataFieldHeaderFlag;
    uint8_t     PID;
    uint8_t     PCAT;
    uint8_t     groupingFlags;
    uint16_t    sequenceCount;
    uint16_t    packetLength;
} primaryHeader_ispType_;

typedef struct time_dataFieldHeaderType_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} time_dataFieldHeaderType_;

typedef struct secondaryHeader_ispType_
{
    InfosetBase _base;
    uint8_t     spareBit;
    uint8_t     PUSversion;
    uint8_t     spare4Bit;
    uint8_t     servicePacketType;
    uint8_t     servicePacketSubType;
    uint8_t     destinationID;
    time_dataFieldHeaderType_ time;
    uint8_t     timeStatus;
} secondaryHeader_ispType_;

typedef struct PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_;

typedef struct PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_;

typedef struct SPACECRAFT_CENTRAL_TIME_navatt_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint32_t    fine;
} SPACECRAFT_CENTRAL_TIME_navatt_;

typedef struct sourceData_ispType_
{
    InfosetBase _base;
    HexBinary   cswField;
    uint8_t     _a_cswField[4];
    HexBinary   PM_DAT_GNSS_TIME_VALIDITY_FLAG;
    uint8_t     _a_PM_DAT_GNSS_TIME_VALIDITY_FLAG[1];
    PM_DAT_NAVATT_CORRELATION_PPS_OBT_navatt_ PM_DAT_NAVATT_CORRELATION_PPS_OBT;
    PM_DAT_NAVATT_CORRELATION_GNSS_TIME_navatt_ PM_DAT_NAVATT_CORRELATION_GNSS_TIME;
    SPACECRAFT_CENTRAL_TIME_navatt_ SPACECRAFT_CENTRAL_TIME;
    double      AO_DAT_I_POS_I_SC_EST_1;
    double      AO_DAT_I_POS_I_SC_EST_2;
    double      AO_DAT_I_POS_I_SC_EST_3;
    double      AO_DAT_I_VEL_I_SC_EST_1;
    double      AO_DAT_I_VEL_I_SC_EST_2;
    double      AO_DAT_I_VEL_I_SC_EST_3;
    double      AO_DAT_Q_I_SC_EST_1;
    double      AO_DAT_Q_I_SC_EST_2;
    double      AO_DAT_Q_I_SC_EST_3;
    double      AO_DAT_Q_I_SC_EST_4;
    double      AO_DAT_SC_RATE_I_SC_EST_1;
    double      AO_DAT_SC_RATE_I_SC_EST_2;
    double      AO_DAT_SC_RATE_I_SC_EST_3;
    double      AO_DAT_Q_SC_ERR_1;
    double      AO_DAT_Q_SC_ERR_2;
    double      AO_DAT_Q_SC_ERR_3;
    double      AO_DAT_Q_SC_ERR_4;
    uint8_t     AO_DAT_GDCMODEFLG;
    uint8_t     SPACECRAFT_MODE;
    uint8_t     AO_DAT_THRUST_FLG;
    uint8_t     AO_AJ_IP_OP_FLG;
    uint8_t     AO_DAT_GNSS_VALIDDATA_ITG;
    uint32_t    AO_DAT_NAVATT_ORBITNUMBER_EST_ITG;
    uint32_t    AO_DAT_NAVATT_OOP_EST_ITG;
    uint8_t     AO_DAT_NEWGNSSDATAFLG_ITG;
} sourceData_ispType_;

typedef struct measurements_
{
    InfosetBase _base;
    primaryHeader_ispType_ primaryHeader;
    secondaryHeader_ispType_ secondaryHeader;
    sourceData_ispType_ sourceData;
    uint16_t    errorControl;
} measurements_;

#endif // GENERATED_CODE_H
