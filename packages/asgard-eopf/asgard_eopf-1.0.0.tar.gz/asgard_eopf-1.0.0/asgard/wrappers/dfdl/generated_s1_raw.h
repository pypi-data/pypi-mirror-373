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

typedef struct time_secondaryHeaderType_
{
    InfosetBase _base;
    uint32_t    coarse;
    uint16_t    fine;
} time_secondaryHeaderType_;

typedef struct subcommutatedAncillary_secondaryHeaderType_
{
    InfosetBase _base;
    uint8_t     wordIndex;
    HexBinary   word;
    uint8_t     _a_word[2];
} subcommutatedAncillary_secondaryHeaderType_;

typedef struct secondaryHeader_ispType_
{
    InfosetBase _base;
    time_secondaryHeaderType_ time;
    uint32_t    syncMarker;
    uint32_t    dataTakeID;
    uint8_t     ECC;
    uint8_t     _padding1;
    uint8_t     testMode;
    uint8_t     RXChannelID;
    uint32_t    instrumentConfigID;
    subcommutatedAncillary_secondaryHeaderType_ subcommutatedAncillary;
    uint32_t    spacePacketCount;
    uint32_t    PRICount;
    uint8_t     errorFlag;
    uint8_t     _padding2;
    uint8_t     BAQMode;
    uint8_t     BAQBlockLength;
    uint8_t     _padding3;
    uint8_t     rangeDecimation;
    uint8_t     rxGain;
    uint16_t    txPulseRampRate;
    uint16_t    txPulseStartFrequency;
    uint32_t    txPulseLength;
    uint8_t     _padding4;
    uint8_t     rank;
    uint32_t    PRI;
    uint32_t    SWST;
    uint32_t    SWL;
    HexBinary   SSBMessageSAS;
    uint8_t     _a_SSBMessageSAS[3];
    HexBinary   SSBMessageSES;
    uint8_t     _a_SSBMessageSES[3];
    uint16_t    numberOfQuad;
    uint8_t     _padding5;
} secondaryHeader_ispType_;

typedef struct isp_
{
    InfosetBase _base;
    primaryHeader_ispType_ primaryHeader;
    secondaryHeader_ispType_ secondaryHeader;
    HexBinary   sourceData;
} isp_;

#endif // GENERATED_CODE_H
