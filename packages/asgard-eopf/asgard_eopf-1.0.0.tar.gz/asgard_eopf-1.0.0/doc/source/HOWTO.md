# Conventions

## Time encoding

The time in ASGARD is encoded using:

* a reference epoch (always 2000-01-01T00:00:00 for EOCFI based implementations)
* a delta from this epoch (encoded in `float64`)
* a unit (always Julian days for EOCFI based implementations)

Usually, times arrays are handled by ASGARD, so we store the fields:

* "epoch": reference epoch as `str`
* "offset": Numpy array of `float64`
* "unit": Unit for offsets ("d" or "s") (resp. Julian days or seconds)

The time scale is independent from the time encoding. The time encoding may be expressed in any of
these time scales:

* TAI
* UTC
* UT1
* GPS

## Geodetic coordinates

The geodetic coordinates are usually expressed as:

* longitude (in deg)
* latitude (in deg)
* altitude (in m)

## Cartographic coordinates

ASGARD handles most of the computations in geodetic coordinates (lon, lat, height). For conversions
with other cartographic projections, users should rely on
[pyproj](https://pyproj4.github.io/pyproj/stable/index.html). This library has a comprehensive list
of supported projection. In particular, it is possible to apply transforms to Numpy arrays
efficiently, like in this
[example](https://pyproj4.github.io/pyproj/stable/advanced_examples.html#repeated-transformations).

## Style/Typography

When refering to ASGARD and ASGARD-Legacy, please comply with the following guidelines:

| context  | typography      |
| -------- | --------------- |
| name/doc | `ASGARD-Legacy` |
| file/url | `asgard-legacy` |
| variable | `asgard_legacy` |
| constant | `ASGARD_LEGACY` |

The idea is the same for ASGARD, except that the Python package is called
`asgard_eopf` due to a conflict in [Python package index](https://pypi.org).

Please refer to [PEP 8](https://peps.python.org/pep-0008/)
for more information on that matter.


# Basic functions

To instantiate a Geometry, a dictionnary shall be define.
In order to define this dictionnary, some basic functions of ASGARD can be used.
This sections presents the main ones.

## Orbit transformation

Orbit can be expressed in different frames.
A transforataion between Frame can be performed using
`EarthBody.transform_orbit`,
see [API documentation](https://geolib.pages.eopf.copernicus.eu/asgard/apidoc/asgard.models.html#asgard.models.body.EarthBody.transform_orbit).
It is for example mandatory before a merge is done, to make sure orbits are all in the same frame
An example is available in `test_merge_orbits` in `tests/test_models_orbit.py`.

```python
bulletin = open("bulletinb-413.txt").readlines() # from datacenter.iers.org
time_model = TimeReference(iers_bulletin_b=bulletin)
body_model = EarthBody(time_reference=time_model)
body_model.transform_orbit(orbit, FrameId.EF)
```

`TimeReference` [IERS bulletin](https://datacenter.iers.org/bulletins.php)
should match the `orbit` start/end date range.

Please note that the transformation is done in-place. If you need to keep the
original orbit, you will have to make a copy using: `dict.copy()`.

More information on frames can be found on [Orekit website](https://www.orekit.org/site-orekit-11.3.3/architecture/frames.html).

## Getting Orbit Information

Orbit information can be computed through orbits Low-level models. There are two orbit model available:
* `GenericOrbitModel` : taking as input a list of OSV from NAVATT or FRO/FPO files, orbit info like anx are found by interpolation. 
Note that cycle and phase number are not computed in this case.   
* `OrbitScenarioModel` : taking as input a list of orbit information from OSF. An orbit propagation is performed.   

Example using ASGARD:

### using orbit states vector 

```python
from asgard.models.time import TimeReference
from asgard.models.body import EarthBody
from asgard.models.orbit import GenericOrbitModel

#Configure the TimeReference
config_time = {
    "iers_bulletin_a": iers_data,
}
time_model = TimeReference(**config_time)

#Configure the EarthBody
config_earth_body = {"time_reference": time_model}
earth_body = EarthBody(**config_earth_body)

# Configure the Orbit
time_orb_gps = 8338.064236111111
time_orb_str = f"GPS={time_model.to_str(time_orb_gps, ref_in=TimeRef.GPS)}"

config_orbit_model = {
    "orbit": [ORBIT],
    "attitude": [ATTITUDE],
    "time_orb": time_orb_str,
    "earth_body": earth_body,
}
orbit_model = GenericOrbitModel(**config_orbit_model)

# Get the orbit information
orbit_info = orbit_model.info

# Get orbit information at another date
orbit_info = orbit_model.get_info(date)
```

> Please note that cycle and phase are not computed.

### using orbit scenario  

```python
from asgard.models.time import TimeReference
from asgard.models.body import EarthBody
from asgard.models.orbit import OrbitScenarioModel

#Configure the TimeReference
config_time = {
    "iers_bulletin_a": iers_data,
}
time_model = TimeReference(**config_time)

#Configure the EarthBody
config_earth_body = {"time_reference": time_model}
earth_body = EarthBody(**config_earth_body)

# Configure the Orbit propagation initialization 
time_orb_gps = 8338.064236111111
time_orb_str = f"GPS={time_model.to_str(time_orb_gps, ref_in=TimeRef.GPS)}"

config_orbit_model = {
    "orbit": [ORBIT],
    "orbit_frame": "EME2000",
    "attitude": {"aocs_mode": "YSM"},
    "time_orb": time_orb_str,
    "earth_body": earth_body,
}
orbit_model = OrbitScenarioModel(**config_orbit_model)

# Get the orbit information for L0 (absolute orbit number,relative orbit number,phase id,cycle number)
light_orbit_info = orbit_model.get_info(date, light=True)

# Get complete orbit info (ANX, mean Keplerians elements, ...), by perfoming orbit propagation
orbit_info = orbit_model.get_info(date)
```


Example using ASGARD-Legacy:
```python
    from asgard_legacy.wrappers.eocfi.product import GenericProduct

    # Get orbit_scenario
    orbit_scenario = [...]

    # Init Orbit Model
    gpd = GenericProduct("SENTINEL_3A")
    gpd.init_model()
    gpd.init_time(orbit_scenario=[orbit_scenario])
    gpd.init_orbit(orbits=[], orbit_scenario=[orbit_scenario])

    # Get orbit information
    anx = gpd.orbit_info(8338.064236111111)
```
Please note that if the orbit is not containing OSF information, cycle and phase number won't be computed.

## Time conversion

To convert time, use methods from `TimeReference` class, see [API documentation](https://geolib.pages.eopf.copernicus.eu/asgard/apidoc/asgard.models.html#asgard.models.time.TimeReference.convert)

```python
with open("/path/to/iers/bulletin.txt", "r", encoding="utf-8") as iers_file:
    iers_lines = iers_file.readlines()

tai_value = 8330.890787037037
trf = TimeReference(iers_bulletin_a=iers_lines)
trf.convert(tai_value, TimeRef.TAI, TimeRef.UTC)
>>> 8330.890358796296
```

More examples available in `tests/test_models_time.py`.

More information on time can be found on [Orekit website](https://www.orekit.org/site-orekit-11.3.3/architecture/time.html).
