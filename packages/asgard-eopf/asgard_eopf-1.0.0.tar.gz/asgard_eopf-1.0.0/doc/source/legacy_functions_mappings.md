# Mappings of ASGARD's functions versus Legacy's funtions

**NOTE: To see how to use ASGARD and its Geometries, please refer to the `User manual: High-level API usage`**

Each sensor have a dedicated Geometry. And each geometry allows to compute the High-Level functions, to compute direct/inverse locations, angles and footprints.

In the following sections a mapping between Sentinel-1/Sentinel-2/Sentinel3 function is presented to help understanding what function of ASGARD needs to be called to perform the Legacy equivalent.

## Mappings of  ASGARD-Legacy implementations versus EO CFI

ASGARD-Legacy comes with an implementation of several products and models relying on EO CFI. This implementation only targets S1 and S3 products. It will become deprecated once Rugged/Orekit based implementation will support those sensors.

Here is the mapping between ASGARD models and EO CFI identifiers:

| Abstract class | EOCFI Implementation | Managed IDs |
 --- | --- | --- |
| {class}`AbstractTimeReference <asgard.core.time.AbstractTimeReference>` | {class}`ExplorerTimeReference <asgard_legacy.models.explorer.ExplorerTimeReference>` | `xl_time_id` |
| {class}`AbstractBody <asgard.core.body.AbstractBody>`                   | {class}`ExplorerEarthBody     <asgard_legacy.models.explorer.ExplorerEarthBody>`     | `xl_model_id`<br>`xp_dem_id` |
| {class}`AbstractOrbitModel <asgard.core.orbit.AbstractOrbitModel>`      | {class}`ExplorerOrbit         <asgard_legacy.models.explorer.ExplorerOrbit>`         | `xl_time_id`<br>`xl_model_id`<br>`xo_orbit_id` |

Here is the list of Sentinel products implemented with EOCFI backend:

* {class}`S3OLCILegacyGeometry <asgard_legacy.sensors.sentinel3.olci.S3OLCILegacyGeometry>`
* {class}`S3SLSTRLegacyGeometry <asgard_legacy.sensors.sentinel3.slstr.S3SLSTRLegacyGeometry>`
* {class}`S3SRALLegacyGeometry <asgard_legacy.sensors.sentinel3.sral.S3SRALLegacyGeometry>`
* {class}`S3MWRLegacyGeometry <asgard_legacy.sensors.sentinel3.mwr.S3MWRLegacyGeometry>`
* {class}`S1SARLegacyGeometry <asgard_legacy.sensors.sentinel1.csar.S1SARLegacyGeometry>`


### Sentinel 3 OLCI DPM mapping

Extracted from *S3IPF DPM 002 - i2r5 - Detailed Processing Model - OLCI Level 1*.

|L1 Step Name | Layer 1  | Layer 2 | Final Step ID| EOCFI function  | ASGARD class or function
| --- | --- | --- | --- | --- | --- |
| **Data extraction<br>and quality<br>checks** | O1_DE |||| `ExplorerTimeReference`<br> `S3LegacyDriver`<br> `S3OLCIGeometry`
|||O1_DE_0 |
|Initialise Time<br>Correlations|| | O1_DE_0_1-2             | *xl_time_ref_init_file* which return time_id | `ExplorerTimeReference`
|Initialise Data<br>Structures|| | O1_DE_0_2-4                 |  *xl_time_transport_to_processing*<br>which return processing times | `ExplorerTimeReference`<br>└─ `from_transport()`
||| | O1_DE_0_2-44 | *xl_model_init* which return model_id
||| | O1_DE_0_2-45 | *xo_orbit_init_file* which return orbit_id
||| | O1_DE_0_2-46 | *xo_orbit_info* ANX from orbit file    | `S3OLCIGeometry`<br>└─ `__init__()`
|*Extract NAVATT<br>Data* || O1-DE_4|
||||O1-DE_4-19|*xl_time_processing_to_processing*<br>Convert NAVATT time from<br>GPS to TAI, UTC and UT1 | `ExplorerDriver`<br>└─ `fill_other_timescales()`
||||O1-DE_4-7| *xl_change_cart_cs* Convert POS<br>and VEL from J2000 to Earth Fixed | `ExplorerDriver`<br>└─ `change_orbit_frame()`
||||O1-DE_4-11| *xl_time_processing_to_ascii*<br>create ascii string for<br>start and end time | `S3LegacyDriver`<br>└─ `read_navatt_file()`
||||O1-DE_4-12| *xd_write_orbit_file* write orbit file | `ExplorerDriver`<br>└─ `write_orbit_file()`
||||O1-DE_4-14| *xd_write_att* write attitude file | `ExplorerDriver`<br>└─ `write_attitude_file()`
| **Geo-Referencing** | O1-GR |||| `S3OLCIGeometry`<br>├─ `direct_loc()`<br>└─ `sun_angles()`   |
|*Geo-referencing<br>Initialisation* | | O1-GR_1           | | | `S3OLCIGeometry`<br>└─ `__init__()`
|Initialize CFI models | || O1-GR_1-1a        | *xl_model_init* 
| | || O1-GR_1-1                                                                        | *xo_orbit_init_file* 
| | || O1-GR_1-15                                                                       | *xo_orbit_info* 
| |||O1-GR_1-16| *xl_time_processing_to_processing*<br>GPS scale conversion                          
|Initialise<br>attitude<br>calculator |||O1-GR_1-3| *xp_sat_att_init_file*<br>use restituted attitude data from NAVATT 
| |||O1-GR_C-1| *xp_sat_nominal_att_init*<br>CFI model Yaw Steering Mode                           |
| |||O1-GR_C-1| *xp_sat_att_angle_init*                                                          |
| |||O1-GR_1-5| *xp_instr_att_matrix_init*<br>Id transfomation for each camera                      |
| |||O1-GR_1-6| *xp_attitude_init*<br>init attitude Id                                             
| |||O1-GR_1-7| Sat_to_OLCI_Trans  sat to<br>instrument, INTERNAL function<br>not provided by EOCFI     | `ThermoelasticModel`
|Initialize DEM<br>structure |||O1-GR_1-8| *xp_dem_init* ACE                                     | 
|Compute Sun<br>position vector<br>in EF |||O1-GR_1-9| *xl_sun* sun position                     |
 | *Satellite<br>Navigation<br>and Attitude* || O1-GR_2|
  |Compute satellite<br>navigation at<br>current time |||O1-GR_2-2| *xo_osv_compute* compute OSV   |
 | |||O1-GR_2-3| *xo_osv_compute_extra*<br>track direction,<br>earth fixed coordinates           |
| *OLCI / Satellite<br>Alignment* || O1-GR_3|
 | |||O1-GR_3-1| Sat_to_OLCI_Trans  sat to<br>instrument, INTERNAL function<br>not provided by EOCFI     | `ThermoelasticModel`
| |||O1-GR_3-2| *xp_instr_att_set_matrix* add transform                                          | |
| Overall Attitude |||O1-GR_3-3| *xp_attitude_compute*                                           | |
| *Pixel Georeferencing* || O1-GR_4|
|compute 1st<br>intersection with<br>reference ellipsoid| || O1-GR_4-1  | *xp_target_inter* first<br>intersection with ellipsoid | `S3OLCIGeometry`<br>└─ `direct_loc()`
|compute 1st<br>intersection with<br>DEM| || O1-GR_4-2                  | *xp_target_inter_extra*<br>first intersection with DEM | `S3OLCIGeometry`<br>└─ `direct_loc()`
|compute target<br>to sun direction| || O1-GR_4-3                       | *xp_target_inter_extra*<br>first intersection with DEM
| compute Target<br>to Sun directions ||| O1-GR_4-3 | *xp_target_extra_target_to_sun*  | `S3OLCIGeometry`<br>└─ `sun_angles()` |
| **Spatial Re-sampling** | O1-SRS |||| `GroundTrackGrid`<br>└─ `direct_loc()`<br>for FR and RR TiePoints |
|*Initialisation* | | O1-SRS_1         |
|Initialise Attitude<br>Ids for FR | |      | O1-SRS_1-3 | *xp_attitude_init* |
|Initialise Attitude<br>Ids for RR | |       | O1-SRS_1-4 | *xp_attitude_init* |
| |||O1-SRS_1-6| *xp_instr_att_matrix_init*<br>init with Id transfomation |
| *Tie Point Grids<br>computation* | | O1-SRS_2                    |
|Satellite<br>Navigation<br>and Attitude for FR | || O1-SRS_2_1-1           | *xo_osv_compute* orbit state vector
 | |||O1-SRS_2_1-3| Sat_to_OLCI_Trans  sat to<br>instrument, INTERNAL function<br>not provided by EOCFI     | 
|| ||O1-SRS_2_1-7| *xp_instr_att_set_matrix* add transform                                      | |
| Compute satellite<br>attitude at<br>FR Tie Frame time |||O1-SRS_2_1-2| *xp_attitude_compute*  | |
|Satellite<br>Navigation<br>and Attitude for RR || | O1-SRS_2_1-4                         | *xo_osv_compute* orbit<br>state vector
 | |||O1-SRS_2_1-6| Sat_to_OLCI_Trans sat to<br>instrument, INTERNAL function<br>not provided by EOCFI     |  
| |||O1-SRS_2_1-8| *xp_instr_att_set_matrix* add transform                                          || |
| Compute satellite<br>attitude at RR<br>Tie Frame time |||O1-SRS_2_1-5| *xp_attitude_compute*       | |
|compute 1st<br>intersection with<br>reference ellipsoid<br>at required distance<br>from SSP for FR|||O1-SRS_2_2-2 | *xp_target_ground_range* 
|compute 1st<br>intersection with<br>reference ellipsoid |||O1-SRS_2_2-3 | *xp_target_extra_main*  | `GroundTrackGrid`<br>├─ `incidence_angles()`<br>└─ `across_track_pointing()`
|compute Target<br>to Sun direction |||O1-SRS_2_2-5 | *xp_target_extra_target_to_sun* | `GroundTrackGrid`<br>└─ `sun_angles()`
|compute 1st<br>intersection with<br>reference ellipsoid<br>at required distance<br>from SSP for RR|||O1-SRS_2_2-6 | *xp_target_ground_range* 
|compute 1st<br>intersection with<br>reference ellipsoid |||O1-SRS_2_2-7 | *xp_target_extra_main* | `GroundTrackGrid`<br>└─ `incidence_angles()`
|compute Target to<br>Sun direction |||O1-SRS_2_2-9| *xp_target_extra_target_to_sun* | `GroundTrackGrid`<br>└─ `sun_angles()`
| **Product Formatting** | O1-PF |
| *Writing the EO<br>L1b Metadata* || O1-PF_1| 
| Check occurrence<br>of Leap Second<br>and retrieve its time | || O1-PF_1-0        | *xl_time_get_leap_second_info* | `TimeReference`<br>└─ `leap_seconds()` 
| **Data extraction<br>and quality checks** |OC-DE |||| `TimeReference`<br> `S3OLCIGeometry`
| *Initialisation step* || OC-DE_0
|Initialise Time<br>Correlations ||| OC-DE_0_1-2| *xl_time_ref_init_file*<br>initialize time reference    
|Initialise Data<br>Structures|| | OC-DE_0_2-0.2                                                                    |  *xl_time_transport_to_processing*<br>which return processing times  
|*Compute DoY at<br>mid Level 0<br>product time* |||OC-DE_0_2-13 | *xl_time_processing_to_processing*<br>get mid date  
| **Acquisition geometry** | OC-GE |||| `S3OLCIGeometry`
| *Initialisation* | | OC-GE_1           |
|Initialize CFI models | || O1-GE_1-1a                        | *xl_model_init* 
|Initialise orbit<br>calculator | || O1-GE_1-1                   | *xo_orbit_init_file* 
|Compute ANX from<br>orbit file | || O1-GE_1-8                    | *xo_orbit_info* | `ExplorerOrbitModel` |
| |||O1-GE_1-9| *xl_time_processing_to_processing*<br>GPS scale conversion    
|Initialise attitude<br>calculator |||O1-GE_1-3| *xp_sat_att_init_file*<br>use restituted attitude<br>data from NAVATT  
| |||O1-GR_1_C-2| *xp_sat_nominal_att_init*<br>CFI model Yaw Steering Mode                           |
| |||O1-GR_1_C-3| *xp_sat_att_angle_init*                                                          |
| |||OC-GE_1-5| *xp_instr_att_matrix_init*<br>Id transfomation for each camera                      |
| |||OC-GE_1-6| *xp_attitude_init*<br>init attitude Id                                             
|*Satellite Navigation* ||OC-GE_2|
|Compute satellite<br>navigation at<br>current time |||OC-GE_2-2| *xo_osv_compute* compute OSV     |
 | |||OC-GR_2-3| *xo_osv_compute_extra*<br>track direction,<br>earth fixed coordinates                  |
| *OLCI / Satellite<br>Alignment* ||OC-GE_3 |
 | |||O1-GE_3-1| Sat_to_OLCI_Trans sat to<br>instrument, INTERNAL function<br>not provided by EOCFI     | 
| |||O1-GE_3-2| *xp_instr_att_set_matrix* add transform        | |
| Overall Attitude |||O1-GE_3-3| *xp_attitude_compute*      | |
| *Sun direction* || O1-GE_4| | | `S3OLCIGeometry`<br>└─ `instrument_to_sun()` |
|Compute Sun<br>position vector<br>in EF |||OC-GE_4-1 | *xl_sun* 
| Convert to<br>Mission CFI<br>Instrument Frame|||OC-GE_4-4 | *xp_change_frame* 
| **Product Formatting** | OC-PF |
| *Writing the<br>Radiometric Calibration<br>Metadata* || OC-PF_1| 
| Check occurrence<br>of Leap Second<br>and retrieve its time | || OC-PF_1-0           | *xl_time_get_leap_second_info* | `TimeReference`<br>└─ `leap_seconds()` |
| **Product Formatting** | OS-PF |
| *Writing the Spectral<br>Calibration Metadata* || OS-PF_1| 
| Check occurrence<br>of Leap Second<br>and retrieve its time | || OC-PF_1-0       | *xl_time_get_leap_second_info* | `TimeReference`<br>└─ `leap_seconds()` |


Notes for V1:

* The cross-track looking geometry for O1-SRS is implemented as a special mode of class
  `GroundTrackGrid`. When available, it uses attitude file and thermoelastic model to define
  the platform attitude. The so-called "track" (the succession of sub-satellite points) is replaced
  by the points seen by the instrument nadir (pointing of 90° elevation angle). 
* For O1-SRS_2, the target to satellite elevation angle in instrument frame can be computed by EOCFI
  with option `XP_TARG_EXTRA_MAIN_SAT2TARG_ATTITUDE`. This option is not exposed in
  `GroundTrackGrid.direct_loc()`. It is now exposed from `GroundTrackGrid.across_track_pointing()`.
  The angle is derived from the 3 cartesian positions (target point, satellite, reference ground
  point) using Numpy (scalar product + arccos).
* In calibration mode (OC), the call to `xp_change_frame` in OC-GE_4-4 is not wrapped in a
  standalone function. The computation of Sun coordinates in instrument frame is done by
  `S3OLCIGeometry.instrument_to_sun()`.

### Sentinel 3 SLSTR DPM mapping

Extracted from *S3IPF DPM 003 - i5r9 - Detailed Processing Model - SLSTR Level 1*.

|L1 Step Name | Layer 1 | Layer 2 | Final Step ID  | EOCFI function | ASGARD Function
|---|---|---|-----------------------------------------------------------------|---|---|
| **L1a processing** |  |
| *Source Packet<br>Processing* | S1-L1A_1  | | | | `TimeReference`<br> `TimestampModel`
|Defining Time<br>and Scan limits ||S1-L1A_1_0|
|Initialise Time<br>Correlations|||S1-L1A_1_1-10 | _xl_time_ref_init_file_<br>which returns time_id|
||| | S1-L1A_1_1-12 | _xl_time_transport_to_processing_<br>which return processing times
|Source Packet<br>Quality Check || S1-L1A_1_1 |
||| | S1-L1A_1_1-42 |  *xl_model_init* which return model_id 
||| | S1-L1A_1_1-43 |  *xo_orbit_init_file* which return orbit_id
||| |S1-L1A_1_1-44 |  *xo_orbit_info*<br>ANX from orbit file | `ExplorerOrbitModel`
|Science Data<br>Processing | |S1-L1A_1_7| | | `TimeReference`
||||S1-L1A_1_7-103 | _xl_time_transport_to_processing_
||||S1-L1A_1_7-26 | _xl_time_transport_to_processing_
||||S1-L1A_1_7-32 | _xl_time_transport_to_processing_
|NAVATT Packet<br>Processing ||S1-L1A_1_8| | | `S3LegacyDriver`<br>└─ `read_navatt_file()`<br> `TimeReference`<br>├─ `convert()`<br>└─ `to_str()`
||||S1-L1A_1_8-3|_xl_time_processing_to_processing_  | 
||||S1-L1A_1_8-10a|_xl_time_processing_to_processing_<br>Convert NAVATT time from<br>GPS to TAI, UTC and UT1 |  
||||S1-L1A_1_8-33| _xl_time_processing_to_ascii_<br>create ascii string<br>for start and end time  
||||S1-L1A_1_8-34| _xl_time_processing_to_ascii_<br>create ascii string<br>for start and end time  
||||S1-L1A_1_8-58| _xd_write_att_<br>write attitude file
||||S1-L1A_1_8-60| _xo_orbit_init_file_<br>write orbit file  
||||S1-L1A_1_8-62b| _xl_time_processing_to_processing_<br>ANX time to GPS
|Time Calibration |S1-L1A_4| ||| `S3LegacyDriver`<br>└─ `parse_timestamps()` |
|Geolocation |S1-L1A_5| | | | `S3SLSTRGeometry`<br>└─ `direct_loc()` |
|Quasi-cartesian<br>grid generation ||S1-L1A_5_1| | | `GroundTrackGrid`<br>└─ `direct_loc()` |
| | ||S1-L1A_5_1_1-4| *xo_orbit_init_file*  
| |||S1-L1A_5_1_1-6| *xp_attitude_init*<br>init attitude Id 
| |||S1-L1A_5_1_1-7| *xp_sat_nominal_att_init*<br>CFI model Yaw Steering Mode|
  |Compute satellite<br>navigation at current<br>time |||S1-L1A_5_1_2-1| *xo_osv_compute*<br>compute OSV |
 | geolocation coordinates |||S1-L1A_5_1_2-2| *xo_osv_compute_extra* |  *Frame* transform
| ||| S1-L1A_5_1_3-4| *xp_attitude_compute* | 
| |||S1-L1A_5_1_3-6| *xp_target_ground_range* | 
| |||S1-L1A_5_1_3-7| *xp_target_extra_main* | 
|Sentinel-3 orbit<br>position and attitude<br>interpolation || S1-L1A_5_2| | | `S3SLSTRGeometry`<br>├─ `direct_loc()`<br>├─ `quasi_cartesian_grid()`<br>└─ `tie_points_grid()`
| |||S1-L1A_5_2_1| *xp_dem_init* |
| |||S1-L1A_5_2_2 | *xp_sat_att_init_file* |
| |||S1-L1A_5_2_3a | *xp_sat_nominal_att_init* |
| |||S1-L1A_5_2_3b | *xp_sat_att_angle_init* |
| |||S1-L1A_5_2_4a| Sat_to_STR_Trans  sat to<br>instrument, INTERNAL function<br>not provided by EOCFI| `ThermoelasticModel`
| |||S1-L1A_5_2-10| *xp_instr_att_matrix_init*<br>init attitude Id 
| |||S1-L1A_5_2-11| *xp_attitude_init*  
  |Compute satellite<br>navigation at current<br>time |||S1-L1A_5_2-29| *xo_osv_compute*<br>compute OSV | 
 | Geolocation coordinates |||S1-L1A_5_2_29a| *xo_osv_compute_extra* | 
 || ||S1-L1A_5_2_32| *xp_instr_att_set_matrix* add transform |            || ||S1-L1A_5_2_33| *xp_attitude_compute*  |
|compute  intersection<br>with DEM| || S1-L1A_5_3-8 |   *xp_target_inter*   
|| ||S1-L1A_5_3-9 | *xp_target_extra_main* compute lon/lat
|compute  intersection<br>with DEM| || S1-L1A_5_3-21 |   *xp_target_inter*<br>F1 measurment |
|| ||S1-L1A_5_3-22 | *xp_target_extra_main*<br>compute lon/lat
|| ||S1-L1A_5_3-11a | *xp_target_extra_main* | `S3SLSTRGeometry`<br>└─ `incidence_angles()`
| compute Target to<br>Sun directions ||| S1-L1A_5_3-12 |*xp_target_extra_target_to_sun*<br>sun angels| `S3SLSTRGeometry`<br>└─ `sun_angles()`
| Sun position vector ||| S1-L1A_5_3-12a |*xl_sun* | `S3SLSTRGeometry`<br>└─ `sun_distances()`
| (x,y) coordinates calculation ||S1-L1A_5_4| | | `GroundTrackGrid`<br>└─ `ground_to_xy()`
||||S1-L1A_5_4-4 | *xl_geod_distance*| `ExplorerEarthBody`<br>└─ `geodetic_distance()`
||||S1-L1A_5_4-5 | *xl_geod_distance*| `ExplorerEarthBody`<br>└─ `geodetic_distance()`
|distances |||S1-L1A_5_4-18| *xp_target_extra_aux* |
||||S1-L1A_5_4-19| *xp_target_ground_range*
||||S1-L1A_5_4-20| *xp_target_extra_main*
||||S1-L1A_5_4-21| *xl_geod_distance*
||||S1-L1A_5_4-30| *xl_geod_distance*
||||S1-L1A_5_4-44| *xp_target_ground_range*
||||S1-L1A_5_4-45| *xp_target_extra_main*
||||S1-L1A_5_4-46| *xl_geod_distance*
||||S1-L1A_5_4-46| *xl_geod_distance*
| **L1b processing** |  |
| **Product Formatting** |S1-L1PF  |
| *Writing the SLSTR<br>metadata file* || S1-L1PF_4| 
| Check occurrence of<br>Leap Second and<br>retrieve its time | ||S1-L1PF_4_11| *xl_time_get_leap_second_info* | `TimeReference`<br>└─ `leap_seconds()`

Notes:

* The Quasi-Cartesian grid (QC) is handled as a standalone product `GroundTrackGrid`, which performs
  cross-track lookup instead of line-of-sight intersection
* The TiePoint grid (TPix) is handled with the same class `S3SLSTRGeometry` but with different
  time and sampling parameters
* For S1-L1A_5_4, although a function is provided to compute geodetic distance,
  `ExplorerEarthBody.geodetic_distance`, the search loop to compute (x,y) coordinates is implemented
  in Cython with `GroundTrackGrid.ground_to_xy`

### Sentinel 3 SRAL DPM mapping

Extracted from *S3IPF DPM 005 - i4r12- Detailed Processing Model - SRAL Level 1* and
*S3IPF DPM 011 - i3r14 - Detailed Processing Model - SRAL Level 2*.

| Step Name | Layer 1 Step ID | Final Step ID | EOCFI function | ASGARD Function |
| --- | --- | --- | --- | --- |
| **SRAL L1b pre-processing** |  |  |  |  |
|  | A2 |  |  |  |
| Convert GPS time into UTC |  | A24 | xl_time_ref_init_file<br>xl_time_processing_to_processing<br>xl_time_get_leap_second_info | TimeReference.leap_seconds() |
| Locate measurements | A3 |  | xl_time_ref_init_file<br>xo_orbit_init_file<br>xo_osv_compute<br>xo_osv_compute_extra | S3SRALGeometry.direct_loc |
| **SRAL/MWR L2 core processing**  |  |  |  |  |
|  | A2 |  |  |  |
| Locate measurements | | A22 | xl_time_ref_init_file<br>xo_orbit_init_file<br>xo_osv_compute<br>xo_osv_compute_extra | S3RALGeometry.direct_loc |
|  | C6 |  |  |  |
| GEN_ENV_ECH_01 |  | C63 | geodetic/cartesian conversions | EOCFIEarthBody |

### Sentinel 3 MWR DPM mapping

Extracted from *S3IPF DPM 009 - i3r1- Detailed Processing Model - MWR Level 1*.

| Step Name | Layer 1 Step ID | Final Step ID | EOCFI function | ASGARD Function |
| --- | --- | --- | --- | --- |
| **MWR L1b pre-processing** |  |  |  |  |
|  | A2 |  |  |  |
| Convert GPS to UTC |  | A22 | xl_time_ref_init_file<br>xl_time_processing_to_processing<br>xl_time_get_leap_second_info | TimeReference.leap_seconds() |
| Locate measurements | A3 |  | xl_model_init<br>xd_read_orbit_file<br>xl_time_ref_init<br>xo_orbit_init_file<br>xo_orbit_get_osv_compute_validity<br>xp_attitude_init<br>xp_sat_nominal_att_init<br>xp_sat_att_angle_init<br>xo_osv_compute<br>xo_osv_compute_extra<br>xp_target_inter<br>xp_target_inter_extra | S3MWRGeometry.direct_loc |

### Sentinel 1 SAR DPM mapping

Unfortunately, we do not have any detailed DPM for S1SAR L1 processor thus we cannot do the same mapping made for other sensors.

Here is a list of geometric function ASGARD supports :
* direct_location
* slant_range_localisation
* terrain_height
* zero_doppler_to_attitude (compute roll/pitch/yaw angles between Zero-Doppler attitude and satellite actual attitude)

## Mappings of ASGARD-Legacy implementations versus S2GEO (using SXGEO)

Sentinel2 MSI instrument geometric modeling was handled by S2GEO JAVA library, which rely on Rugged
and Orekit. Since IPF (Image Processing Facilities) IDP-SCs are all implemented in C++ whereas
S2Geo is a Java library, a system call is performed to communicate. The C++ IDP-SCs describes
geometry tasks to be performed in an XML interface file (similar to a job order) and calls S2Geo as
a system call instantiating the Java virtual machine. S2Geo then reads input files defined in the
XML interface and outputs result files in the working directory of the IDP-SC. It will become
deprecated once an open-source based implementation  will be able to support those sensors.

In the frame of ASGARD V1, the S2Geo component has been reworked and simplified into a "SXGEO"
component, removing as much as possible the S2 specific data structures. In the following versions
of ASGARD, this interface layer will tend to disappear, replaced either by contributions to Rugged
library (for sensor agnostic parts), or by Python code in ASGARD (for sensor specific parts).

ASGARD `S2MSILegacyGeometry` class interfaces with Rugged through SXGeo, which simplifies the
initialization.

### S2MSIGeometry initialisation

An `S2MSIGeometry`  is initialized with a custom dictionary as described `User manul: High-level API usage`.

The Orekit library relies on some external data for physical models. Typical data are the Earth
Orientation Parameters and the leap seconds history, both being provided by the IERS or the
planetary ephemerides provided by JPL or IMCCE. There are two internal data used by SXGEO:

* [DE-430-ephemerides](https://ui.adsabs.harvard.edu/abs/2014IPNPR.196C...1F) for planets ephemerides
* UTC-TAI.history, which contains utc/tai history 

Explicit Orekit_data_path can be set at `S2MSIGeometry` class initialisation. Some IERS bulletins
can be added to this context.

### Tasks 

The list of legacy S2GEO task are given below, these functions are available as `S2MSIGeometry` methods:

|S2GEO task| ASGARD S2MSIGeometry method |
|--|--|
|ComputeGranuleBandFootprint()| call footprint() function for all band and detector (step in GIPP)|
|ComputeGranuleFootprint()| footprint() |
|ComputeDetectorFootprint()| footprint() |
|ComputeFullResGlobalFootprint()| footprint() |
|ComputeGranuleQLFootprint()| *no specific function* |
|ComputeGlobalFootprint()| footprint() |
|L1BMaskProjection()| direct_loc() |
|ComputeTileInitTileAngles()| sun_angles() |
|ComputeIncidenceAngles()| incidence_angles() |
|ComputeTOAGRID()|  inverse_loc() |
|ComputeGeometricHeadertList()| incidence_angles()<br> sun_angles() |
|ComputeCollocationGrid()| direct_loc()<br> inverse_loc() |
|CloudMaskProjection()| direct_loc()<br>at constant altitude |
|ComputeQLDatationModel()| *no specific function* |
