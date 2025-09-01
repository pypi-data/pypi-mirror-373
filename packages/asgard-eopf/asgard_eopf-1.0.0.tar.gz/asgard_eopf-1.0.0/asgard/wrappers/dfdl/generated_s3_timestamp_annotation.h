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

typedef struct gpsTime_annotationType_
{
    InfosetBase _base;
    uint32_t    days;
    uint32_t    seconds;
    uint32_t    microseconds;
} gpsTime_annotationType_;

typedef struct annotation_
{
    InfosetBase _base;
    gpsTime_annotationType_ gpsTime;
    HexBinary   fepAnnotationData;
    uint8_t     _a_fepAnnotationData[18];
} annotation_;

#endif // GENERATED_CODE_H
