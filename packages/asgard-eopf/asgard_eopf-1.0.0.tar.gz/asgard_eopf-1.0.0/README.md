# ASGARD

ASGARD is "A Sensor Geometry Application Reusable by-Design". 

NOTE:
Check ASGARD documentation on the following link: https://geolib.pages.eopf.copernicus.eu/asgard/

## Purpose

Main purposes of the GEOLIB are to:
* Serve as a base geometry bloc for different types of sensors
* Provide a flexible abstraction layer
* Support the generation of L1/L2 products.
* Provide compatibility with Sentinel missions 1, 2, 3 and beyond

The current Legacy codes for geometry application are:
* EOCFI library for Sentinel-1/3,
* S2GEO library, which SXGEO is a simplification for Sentinel-2

However, these codes are not in Python and not Open source.
ASGARD was first developed to tackle those points of the Sentinel-1/2/3 geo-libraries, being in Python and Open-source.

Two versions of ASGARD can be used:
* ASGARD (refactored): Full re-implemented library not calling the Legacy code (EOCFI and SXGEO) of Sentinel1/2/3. It contains all the Geometry init schemas and Generic Models presented below
* ASGARD-Legacy: It is based on ASGARD in order to take and have the same the Geometry init schemas than ASGARD. It also uses generic parts of ASGARD as some models for example. It was developed to have a common interface than ASGARD but calling Legacy libraries instead of the Python re-implementation. This version can be used to assess geometric quality and processing performances of ASGARD. However, it will be deprecated at the end, once the ASGARD library will be fully validated and deployed.
Note: It is to be noted that ASGARD is already intensively validated as presented in the [Validation](#validation), but not yet fully deployed.


## High-level API
### Geometries

![](doc/source/resources/asgard_product.png)

This tool is based on a `Geometry` abstraction, derived into specialized types of sensors. At the
end, you find a geometry object for each Sentinel sensor. These geometries expose the
[High-level API](#high-level-functions). This object is initialized from a JSON-like structure with necessary metadata.
This metadata must be extracted from products, auxiliary data files.

Each geometry builds a set of coherent [Low-level Models](#low-level-models).

### Geometries initialization

The abstract class `AbstractGeometry` is derived for each sensor:

* {class}`S1SARGeometry <asgard.sensors.sentinel1.csar.S1SARGeometry>`
* {class}`S2MSIGeometry <asgard.sensors.sentinel2.msi.S2MSIGeometry>`
* {class}`S3OLCIGeometry <asgard.sensors.sentinel3.olci.S3OLCIGeometry>`
* {class}`S3SLSTRGeometry <asgard.sensors.sentinel3.slstr.S3SLSTRGeometry>`
* ...

Each class is initialized with a custom dictionary. This dictionary must match the JSON schema
given by the `init_schema` method. This will look like:

```python
from asgard.sensors.sentinel3 import S3OLCIGeometry

config = {
  "sat": "SENTINEL_3",
  "orbit_aux_info": {
    "orbit_state_vectors": [
      {
        "times": {
            "TAI": {"offsets": np.array([...])},
            "UTC": {"offsets": np.array([...])},
            "UT1": {"offsets": np.array([...])},
        },
        "positions": np.array([...]),
        "velocities": np.array([...]),
        "absolute_orbit": np.array([...]),
      },
    ],
  },
  "dem_config_file": "path_to_dem",
  "pointing_vectors": {
    "X": np.array([...]),
    "Y": np.array([...]),
  },
  "thermoelastic": {
    "julian_days": np.array([...]),
    "quaternions_1": np.array([...]),
    "quaternions_2": np.array([...]),
    "quaternions_3": np.array([...]),
    "quaternions_4": np.array([...]),
    "on_orbit_positions_angle": np.array([...]),
  },
  "frame": {
      "times": {"offsets": np.array([...])},
  },
}

my_product = S3OLCIGeometry(**config)
```

The input dictionary should contain all numeric and string values necessary to initialize the
geometry. Most of the parsing from L0/L1 product tree metadata files should be done before. When
the input data is large, Numpy arrays will be used instead of plain Python Lists.

### High-level functions

Each class implementing the `Geometry` abstraction should provide the following features:

* `direct_loc()`: perform direct location for a set of measurements
* `inverse_loc()`: perform inverse location for a set of ground locations
* `sun_angles()`: compute Sun angles for a set of ground locations and times
* `sun_distances()`: compute Sun distances given times and optional ground locations
* `incidence_angles()`: compute the viewing angles (ground to satellite) for a set of ground
  locations and times
* `footprint()`: compute the ground footprint of a geometric unit

## Low-level models

Each geometry builds a set of coherent models.
For example for Sentinel-2:

![](doc/source/resources/asgard_models.png)

These models are an abstraction layers to provide a
set of features:

* _TimestampModel_:
  * Give a timestamp for each measurement
* _OrbitModel_:
  * Propagates the orbit
  * Interpolates the orbit to retrieve  position, velocity and acceleration
* _PlatformModel_:
  * Models the different frame transformation between the satellite orbital frame and the instrument
    frame
  * Computes the attitude of the instrument frame at a given time
* _PointingModel_:
  * Models the directions where the instrument can look. Examples:
    - field of view of an optical sensor
    - synthetic antenna orientation
  * Computes the line of sight (at the sensor side) for a given measurement/detector/time.
* _PropagationModel_:
  * Handles the propagation of a signal (micro-wave, light, ...) from a target (Earth, Moon, star)
    to the sensor.
  * Examples:
    - Intersection of a line-of-sight (estimated at the instrument side) with a DEM.
    - Intersection of a range/azimuth SAR pointing with a DEM

Other objects provide some base functions:

* _Frame_:
  * Handles frames and coordinate system
* _Transform_:
  * Handles frames transforms (maybe time dependant)
* _Body_:
  * Model of the Earth, Moon and Sun
  * Handles Earth position bulletin
  * Handle surface models (ellipsoid, DEM)
* _TimeReference_:
  * Handles conversion between time references


## Low-level API
The low-level API rely on the `Model` abstraction. Each model will implement a part of the
"georeferencing pipeline". Most of them use the Rugged/Orekit wrappers as backend. Only two are 
also available with the EOCFI backend:

* {class}`ExplorerTimeReference <asgard-legacy.models.explorer.ExplorerTimeReference>`
* {class}`ExplorerEarthBody     <asgard-legacy.models.explorer.ExplorerEarthBody>`

All the models are initialized based on keyword arguments, which conform to the JSON schema returned
by `init_schema()`. Here is a list of low-level models, by category:

| Category | Model | Role |
| --- | --- | --- |
| Time | {class}`TimeReference <asgard.models.time.TimeReference>` | Conversion between timescales<br>leap seconds<br>Conversion from ascii, cuc, transport |
| Body | {class}`EarthBody <asgard.models.body.EarthBody>` | Cartesian geodetic conversion<br>Frame conversion<br>Sun position<br>Topocentric conversion |
| Timestamp | {class}`LineDetectorTimestampModel <asgard.models.lineardetector.LineDetectorTimestampModel>` | Line datation for line detector sensors |
| Timestamp | {class}`ScanningDetectorTimestampModel <asgard.models.scanningdetector.ScanningDetectorTimestampModel>` | Sample datation for scanning detector<br>(used for SLSTR) |
| Orbit | {class}`GenericOrbitModel <asgard.models.orbit.GenericOrbitModel>` | Interpolate OSV<br>Interpolate attitude<br>Orbit information (ANX, ...) |
| Platform | {class}`GenericPlatformModel <asgard.models.platform.GenericPlatformModel>` | Transform instrument frame to satellite frame |
| Pointing | {class}`LineDetectorPointingModel <asgard.models.lineardetector.LineDetectorPointingModel>` | Poining vector for line detector sensors |
| Pointing | {class}`ScanningDetectorPointingModel <asgard.models.scanningdetector.ScanningDetectorPointingModel>` | SLSTR pointing model |
| Propagation | {class}`PropagationModel <asgard.models.propagation.PropagationModel>` | Line of sight propagation<br>DEM and ellipsoid intersection |
| Propagation | {class}`GroundRangePropagationModel <asgard.models.range.GroundRangePropagationModel>` | Ground range propagation<br>Replacement of xp_target_ground_range |


## Validation

The validation of ASGARD and ASGARD-Legacy implementations is presented in the 
[validation document](doc/source/resources/ASGARD_Validation_document_V5.pdf).

Some complementary and new results (overwriting the ones from the validation document) for 0.5.2 are available in the [Additional_results_for_V5_2024-12](doc/source/resources/Additional_results_for_V5_2024-12.pdf)

Additional comparisons/validations were performed (0.5.2) to compare asgard-legacy behaviour versus EOCFI and are available in [EOCFI_ASGARD_Comparison_TechnicalNote.pdf](doc/source/resources/EOCFI_ASGARD_Comparison_TechnicalNote.pdf)

New dedicated L0 footprints validation (0.7.0) is available here:[FootprintL0Validation.pdf](doc/source/resources/FootprintL0Validation.pdf)
Please note that this is in complement to the tests implemented directly in ASGARD.


