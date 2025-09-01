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

typedef struct header_slstrType_
{
    InfosetBase _base;
    uint16_t    SCAN_SYNC_COUNTER;
    uint8_t     DPM_MODE;
    uint8_t     VALIDITY;
    uint8_t     TARGET_ID;
    uint16_t    TARGET_FIRST_ACQ;
    uint16_t    TARGET_LENGTH;
} header_slstrType_;

typedef struct band_slstrData_
{
    InfosetBase _base;
    uint16_t    array[40000];
} band_slstrData_;

typedef struct array_slstrScanEncoderArray_
{
    InfosetBase _base;
    uint32_t    nad;
    uint32_t    obl;
    int16_t     flip;
} array_slstrScanEncoderArray_;

typedef struct scanpos_slstrData_
{
    InfosetBase _base;
    array_slstrScanEncoderArray_ array[4000];
} scanpos_slstrData_;

typedef struct hk_slstrData_
{
    InfosetBase _base;
    HexBinary   array;
    uint8_t     _a_array[997];
} hk_slstrData_;

typedef struct data_slstrType_
{
    InfosetBase _base;
    size_t      _choice; // choice of which union field to use
    union
    {
        band_slstrData_ band;
        scanpos_slstrData_ scanpos;
        hk_slstrData_ hk;
    };
} data_slstrType_;

typedef struct sourceData_ispType_
{
    InfosetBase _base;
    header_slstrType_ header;
    data_slstrType_ data;
} sourceData_ispType_;

typedef struct isp_
{
    InfosetBase _base;
    primaryHeader_ispType_ primaryHeader;
    secondaryHeader_ispType_ secondaryHeader;
    sourceData_ispType_ sourceData;
    uint16_t    errorControl;
} isp_;

#endif // GENERATED_CODE_H
