.. include:: ./HOWTO.md
   :parser: myst_parser.sphinx_

High-level API usage
--------------------

The following section show how to instantiate ASGARD and ASGARD-Legacy "Geometry", which implement the
high-level API. The method is similar in all cases:

* gather this data in a Python `dict` (similar to a JSON tree, but with Numpy arrays support)
* initialize an:
    * ASGARD `geometry` with the `dict`.
    * ASGARD-Legacy `geometry` with the **same** `dict`. The only differences will be the Geometry Class will be imported thourgh ASGARD-Legacy instead of ASGARD.

.. note:: All the work on initialisation in the Python `dict` can be perfomed by external tools, or take advantages of the Low-levels functions as presented in `Usage of ASGARD for basic operations (low-level functions)`.

Example of Initialisation of S3 OLCI Geometry using ASGARD

.. code-block:: python
    :linenos:

    # Import ASGARD Geometry
    from asgard.sensors.sentinel3 import S3OLCIGeometry

    # Define the config
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

    # Instantiate the Geometry
    my_product = S3OLCIGeometry(**config)

    #Call Direct/Inverse locations/Angles/Footprint functions of the Geometry

The equivalent using ASGARD-Legacy would be:

.. code-block:: python
    :linenos:

    # Import ASGARD-Legacy Geometry
    from asgard_legacy.sensors.sentinel3 import S3OLCILegacyGeometry

    # Define the config
    config = # Same Config from ASGARD example

    # Instantiate the Geometry
    my_product = S3OLCILegacyGeometry(**config)

    #Call Direct/Inverse locations/Angles/Footprint functions of the Geometry


Common fields description
=========================

The input 'dict' contains common fields between sensors. This section describes several of them.

Satellite Orbit schemas
^^^^^^^^^^^^^^^^^^^^^^^

It's separated into 2 parts:

* orbit_aux_info: It can contains **only one** of this 2 possibilities:

  * orbit_state_vectors (which corresponds to fos for S3 for example)
  * orbit_scenario (which corresponds to osf for example)

* navatt

Please find below a description of the fields related to the orbit:

.. code-block:: python
    :linenos:

    ORBIT_STATE_VECTORS_SCHEMA = {
    "type": "object",
        "properties": {
            "times": TIMESCALE_ARRAY_SCHEMA,
            "positions": generate_float64_array_schema(":", 3),
            "velocities": generate_float64_array_schema(":", 3),
            "accelerations": generate_float64_array_schema(":", 3),
            "absolute_orbit": {"type": "array", "dtype": "int32", "shape": (":",)},
            "frame": {"type": "string"},
            "time_ref": TIMESCALE_NAME_SCHEMA,
            "start_date": ASCII_TIMESTAMP_SCHEMA,
            "stop_date": ASCII_TIMESTAMP_SCHEMA,
        },
        "required": [
            "times",
            "positions",
            "velocities",
        ],
        "additionalProperties": False,
    }

    ORBIT_SCENARIO_SCHEMA = {
        "type": "object",
        "properties": {
            "orbit": {
                "type": "object",
                "properties": {
                    "Absolute_Orbit": generate_array_schema("int", [":", 1]),
                    "Relative_Orbit": generate_array_schema("int", [":", 1]),
                    "Cycle_Number": generate_array_schema("int", [":", 1]),
                    "Phase_Number": generate_array_schema("int", [":", 1]),
                },
                "required": ["Absolute_Orbit", "Relative_Orbit", "Cycle_Number", "Phase_Number"],
                "additionalProperties": False,
            },
            "cycle": {
                "type": "object",
                "properties": {
                    "Repeat_Cycle": generate_float64_array_schema(":"),
                    "Cycle_Length": generate_float64_array_schema(":"),
                    "ANX_Longitude": generate_float64_array_schema(":"),
                    "MLST": generate_array_schema("<U15", [":", 1]),
                    "MLST_Drift": generate_float64_array_schema(":"),
                },
                "required": ["Repeat_Cycle", "Cycle_Length", "ANX_Longitude", "MLST", "MLST_Drift"],
                "additionalProperties": False,
            },
            "anx_time": {
                "type": "object",
                "properties": {
                    "TAI": generate_float64_array_schema(":"),
                    "UTC": generate_float64_array_schema(":"),
                    "UT1": generate_float64_array_schema(":"),
                },
                "required": ["TAI", "UTC", "UT1"],
                "additionalProperties": False,
            },
            "required": [
                "orbit",
                "cycle",
                "anx_time",
            ],
            "additionalProperties": False,
        },
    }

    ORBIT_AUX_INFO_SCHEMA = {
        "type": "object",
        "properties": {
            "orbit_state_vectors": ORBIT_STATE_VECTORS_SCHEMA,
            "orbit_scenario": ORBIT_SCENARIO_SCHEMA
         },
        "oneOf": [{"required": ["orbit_state_vector"]}, {"required": ["orbit_scenario"]}],
    }

    # Which can give for example:
    orbit_aux_info = {
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
    }

    NAVATT_SCHEMA = {
        "type": "object",
        "properties": {
            "orbit": ORBIT_STATE_VECTORS_SCHEMA,
            "attitude": ATTITUDE_SCHEMA,
            "times": TIME_ARRAY_SCHEMA,  # expect GPS
            "oop": {
                "type": "array",
                "description": "On-orbit position  for each navatt packet (deg)",
                "minItems": 1,
                "items": {"type": "number"},
            },
        },
        "required": [
            "orbit",
            "attitude",
            "times",
            "oop",
        ],
        "additionalProperties": False,
    }


Detailed description of each config file expected by each Geometry can be found in the following sections.

S1
===

S1 L0
^^^^^
Currently, L0 Geometry only allows footprint computation. The S1 L0 geomtery object :py:class:`S1L0Geometry <asgard.sensors.sentinel1.l0.>` is initialized through a dictionnary composed by the following keys:

* "start_time": "string", in ISO 8601 format
* "stop_time": "string", in ISO 8601 format
* "orbit_state_vectors": ORBIT_STATE_VECTORS_SCHEMA, Expect orbit data in EF
* "angles":,  dict with beam angle in degrees:
           
    * "nearRange": "float",
    * "farRange": "float",

* "look_side": "string" among ("LEFT", "RIGHT")

The footprint is computed in zero doppler aocs mode, using four sub-satellite points (SSP), on the WSG84 ellipsoid:
* Start time, near range beam angle
* Start time, far range beam angle
* Stop time, near range beam angle
* Stop time, far range beam angle

For example:

.. code-block:: python
    :linenos:

    from asgard.sensors.sentinel1.l0 import S1L0Geometry

    conf = {
        "start_time": '2025-02-12T05:52:32.432274Z',
        "stop_time": '2025-02-12T05:53:04.832222Z',
        "orbit_state_vectors": orbits,
        "angles": {
            "nearRange": 26.72,
            "farRange": 39.6,
        },
        "look_side": "RIGHT",
    }
    S1L0Geom = S1L0Geometry(**conf)
    # Compute footprint
    gp_calc = S1L0Geom.footprint()[:, :-1]

Please note that this Geometry is only available in ASGARD and not in ASGARD-Legacy but was properly validated using L0 and L1 footprints as describe in the validation and through tests.

S1 SAR
^^^^^^

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S1SARGeometry <asgard.sensors.sentinel1.csar.S1SARGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel1_sar.ipynb

S2 MSI
======

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S2MSIGeometry <asgard.sensors.sentinel2.msi.S2MSIGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel2_msi.ipynb


S3
===

ASGARD and ASGARD-Legacy provides S3 sensors related geometry models ([S3SLSTRGeometry, S3SRALGeometry, S3OLCIGeometry, and S3MWRLegacyGeometry], [S3SLSTRLegacyGeometry, S3SRALLegacyGeometry, S3OLCILegacyGeometry, and S3MWRLegacyGeometry]).

These models need information about the satellite's orbit. To match the Legacy processor behavior, 3 different types of inputs can be used, from the most accurate to the least accurate: NAVATT, FOS (FRO:restitued orbit or FPO:preditec orbit), OSF(Orbit Scenario File). Only the following combinations are accepted:

* Only FOS
* NAVATT + FOS (FOS used for orbit info, NAVATT for georeferencing)
* Only OSF
* NAVATT + OSF (OSF used for orbit info, NAVATT for georeferencing)

Please note that initialisation with OSF only is for now only available in ASGARD-Legacy.
Examples of intialisation can be found in the ASGARD-Legacy test section (test_legacy_sentinel3_mwr.py, test_legacy_sentinel3_olci.py, test_legacy_sentinel3_sral.py,test_legacy_sentinel3_slstr.py).

S3 L0
^^^^^
Currently, L0 Geometry only allows footprint computation. The S3 L0 geometry object :py:class:`S3L0Geometry <asgard.sensors.sentinel3.l0.>` is initialized through a dictionnary composed by the following keys:

* "start_time": "string", in ISO 8601 format
* "stop_time": "string", in ISO 8601 format
* "orbit_aux_info": ORBIT_AUX_INFO_SCHEMA, Expect orbit data in EME2000 for YSM
* "angles":,  dict with angles in degrees:
           
    * "nearRange": "float",
    * "farRange": "float",

* "pairs_number": "int",

The footprint is computed in Orekit's Yaw steering mode. And, is composed by N pairs of points distributed along the track, on the WSG84 ellipsoid. 
The two points forming the pair correspond to the near and far Range angles of the configuration.
No specific correction is applied when geolocating footprint points (light time correction, ...).

The results of the footprint method is a np.ndarray of shape: (2N,2), the first N lines are the near Range points, and the last N ones are the far Range points.

For example:

.. code-block:: python
    :linenos:

    from asgard.sensors.sentinel3.l0 import S3L0Geometry

    conf = {
        "start_time": '2022-05-11T20:23:27.868231Z',
        "stop_time": '2022-05-11T20:24:13.409581Z',
        "orbit_aux_info": {
            "orbit_state_vectors": orbits_eme2000,
        },
        "angles": {
            "nearRange": 0.00,
            "farRange": -0.02,
        },
        "pairs_number": 12,
    }
    S3L0Geom = S3L0Geometry(**conf)
    gp_calc = S3L0Geom.footprint()

S3 OLCI
^^^^^^^

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S3OLCIGeometry <asgard.sensors.sentinel3.olci.S3OLCIGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel3_olci.ipynb

S3 SLSTR
^^^^^^^^

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S3SLSTRGeometry <asgard.sensors.sentinel3.slstr.S3SLSTRGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel3_slstr.ipynb

S3 SRAL
^^^^^^^

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S3SRALGeometry <asgard.sensors.sentinel3.sral.S3SRALGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel3_sral.ipynb

S3 MWR
^^^^^^

.. note:: The Geometry and in particular the **config** waited by the Geometry can be found at: :py:class:`S3MWRGeometry <asgard.sensors.sentinel3.mwr.S3MWRGeometry>`

Please find below an example of instantiation.

* https://gitlab.eopf.copernicus.eu/geolib/asgard/-/blob/main/examples/run_sentinel3_mwr.ipynb

