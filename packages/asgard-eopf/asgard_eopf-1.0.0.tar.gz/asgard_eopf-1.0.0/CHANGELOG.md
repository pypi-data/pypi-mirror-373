
# Release history

## Upcomming changes not yet merged


## 1.0.0 (2025-08-29)

### Core features and fixes

* Finalize the scope of ASGARD to cover S1/S2/S3:
    * Read the OSF information and use them to get orbit information or for orbit propagation (for Sentinel-3)
    * Allow to compute Sun distances (solar_path)

### Notable changes

* New distances to sun at given times and optional ground locations function (#330)
* Orbit propagator from OSF (#298)
* OSV and ANX information can be computed with OSF initialisation (#298)

### Additional changes

* Modifications:
    * pyproject clean pinned dep matching cpm

## 0.9.0 (2025-07-30)

 * Move to Orekit 13 (#320)
 * Move drivers into tests folder (#314)
 * Remove Dockerfile.requirements.txt file (#304)
 * Published to [The Python Package Index](https://pypi.org/project/asgard-eopf/) (PyPI)
 
## 0.8.0 (2025-07-10)

### Core features and fixes

* Direct locations can be performed on not integer values (only for line detector sensors, not in SAR)
* Extrapolation outside of the swath is performed (only for line detector sensors, not in SAR)

### Additional changes

* Additions:
    * Direct locations can be performed on not integer values (only for line detector sensors, not in SAR), closes #234 (f7e1b797f5a485cad2e00f4985cc6282df023b33)
    * Extrapolation outside of the swath is performed (only for line detector sensors, not in SAR)
* Fixes:
    * Computation of Max line of S2MSI corrected when not provided when only one band is configured: closes #295(d25ab1e06221f414d5bc9c7deeacc8722ca0896c)
* Modifications:
    * Notebooks and documentation updates


## 0.7.1 (2025-06-06)

### Core features and fixes

* Lower the restriction of Numpy version from 2.2.X to >= 2.1.0

## 0.7.0 (2025-04-30)

### Core features and fixes

* L0 footprint computation enabled through new Geometries for S1 and S3
* Verification of Frame of orbits before merging. It is now mandatory to have them in the same Frame
* First step of documentation's reworking

### Notable changes

* L0 footprint computation enabled through new Geometries for S1 and S3, closes #287 & #288 (9f65acedeabd421aeefb7293847e177015da8664)
* Verification of Frame of orbits before merging, closes #296 (0bcc09d0f90f54e01428c3c5d82d890d0d119f54)

### Additional changes

* Additions:
    * First step of documentation's reworking
* Fixes:
    * Computation of Max line of S2MSI corrected when not provided when only one band is configured: closes #295(d25ab1e06221f414d5bc9c7deeacc8722ca0896c)
* Modifications:
    * Add modern pyproject.toml python packaging conf (2fc8a139c975f0bc7b0a65256471cc366ce8eec7)

## 0.6.1 (2025-04-08)

### Core features and fixes

* Inclusion of the handling of the Orbit Scenario File (OSF) in ASGARD-Legacy which required some schemas changes

### Notable changes
* Change input json dictionnaries' schemas required as input S3 Geometries initialisation:
    * Have a new ``orbit_aux_info`` field instead of ``fos_orbits``
    * Have in this field the possibility to configure with **one and only one** of the following new fields:
        * ``orbit_state_vectors``: previously ``fos_orbits`` comming from FRO or FPO
        * ``orbit_scenario``: comming from the OSF

### Miscellaneous
* Update of documentation,
* Additional validation tests handling of OSF,
* Additional validation test for orbit information determination through OSF,
* A type name in input of S1 JSON dictionnary has been change, which is transparent to user.


## 0.6.0 (2025-03-18)

### Core features and fixes

* Alignment versions of libraries of CPM
* Addition of new TDS for OLCI/SLSTR/S1
* Correction of small issue, at antemeridian for example

### Notable changes

* Dependencies version upgraded to match the new release of CPM, closes #289 (522da00681c180e97e89cede5e65a90a61e19d32):
    * Numpy version changed to 2.2.X
    * xarray version changed to 2024.11.0
    * dask version changed to 2024.5.2
    * bokeh version changed to 3.4.X
* Schemas of input dictionnary changed (example with DEM):
``    "resources": {
 "dem_path": dem_path,
 "dem_type": "ZARR",
 }``

### Additional changes

* Additions:
    * sral and mwr instanciation examples (e70696053bca0cdf25537fe34e435c11ecc3bad6)
    * sar geometry example (ccf997aaa6bf58e6f0c46ceb28e9fe1733f9e3a1)
* Fixes:
    * Border cases when searching for ANX for SLSTR, closes #282 (232703a035478e0d3d544e4efd676bf12cf1b8f1)
    * DEM handling at antemeridian, closes #276 (f87319e3edeae6fb9275f00cba04d137a85eeb99)
    * Direct loc bug on quasi cartesian grid (e36d545cf6540a53777b824b02862979f09b07fe)
    * Angle separation when 2 vectors are close (61ab0e7aa879ff32ea543029fc657028ef6132a4)
* Modifications:
    * Reframe orbit method in EarthBody, closes #233 (3de55f25e9a2a371326fdcca298c4550b8fe0f56)
    * Add absolute value in altitude error computation (1a9a597b8aed204ef7af7966fa9d84531367fe65)
    * Raise error when test validation failed instead of warnings (a8aa50ab9e0cb4f4dd0db40e01bcc81ffeaa3f42)
    * Use reference ground data in inputs of inverse location and resample ground (9a5197612e5c2269a389d64c30d4373fb7512125)

### Miscellaneous
* Update of documentation
* Additional validation tests for S1 L1 SAR:
   * Creation of validation tests (c1cb893c57a464c0777214d7ca86d5318b01cd4e)
   * Creation of inverse location tests (41b9d376684d8ad1ef1124781eab7f6286d35f03)
   * Creation of a new validation test at antemeridian, closes #283 (f18c54d410377d161253de8b3ce9c282655d7ff7)
* Additional validation tests for S3 L1:
   * Creation of a new validation S3 SLSTR test that crosses pole (71441bc1fa2186026806ead23f3b964f95dfbfeb)
   * Creation of a new OLCI validation test at antimeridian, closes #275 (4ab9a2262c05a54ed4cf2f17b658633eba5e7743)
   * Creation of a new SLSTR validation test at antimeridian, closes #275 (4ab9a2262c05a54ed4cf2f17b658633eba5e7743)
* Adapt test crosstrack pointing (7f5481f3c48bcb7fc319e16d0f2f12b6eb82e6fe)

## 0.5.2 (2024-10-24)

### Core features and fixes

* Move for loop calling orekit function in java
* Uptade JSON configuration for SAR, OLCI, SLSTR, SRAL and MWR to synchronize with asgard-legacy
* Add new test case using dask
* Support UT1 from orbit to instantiante TImeReference model

## 0.5.1 (2024-07-29)

### Core features and fixes

* Addition of a script to generate results table for MSI validation
* Addition of remote geoid access
* Addition of the possibility to use iers data as content
* Fix MSI bugs

## 0.5.0 (2024-06-21)

### Core features and fixes

* Major release v5, rename Product into Geometry
