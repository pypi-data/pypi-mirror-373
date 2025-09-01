"""get ephemerides from different sources
   at the moment only data from SBDB can be retrieved
"""
from astropy import units as u
from astropy.time import Time
from astroquery.jplsbdb import SBDB
import numpy as np

from boinor.bodies import Sun
from boinor.frames import Planes
from boinor.twobody.angles import (
    D_to_nu,
    E_to_nu,
    F_to_nu,
    M_to_D,
    M_to_E,
    M_to_F,
)
from boinor.twobody.orbit import Orbit


def orbit_from_sbdb(name, **kwargs):
    """read orbit data from SBDB (Small-Body DataBase"""
    obj = SBDB.query(name, full_precision=True, **kwargs)

    if "count" in obj:
        # No error till now ---> more than one object has been found
        # Contains all the name of the objects
        objects_name = obj["list"]["name"]
        objects_name_in_str = (
            ""  # Used to store them in string form each in new line
        )
        for i in objects_name:
            objects_name_in_str += i + "\n"

        raise ValueError(
            str(obj["count"])
            + " different objects found: \n"
            + objects_name_in_str
        )

    if "object" not in obj.keys():
        raise ValueError(f"Object {name} not found")

    a = obj["orbit"]["elements"]["a"]
    ecc = float(obj["orbit"]["elements"]["e"]) * u.one
    inc = obj["orbit"]["elements"]["i"]
    raan = obj["orbit"]["elements"]["om"]
    argp = obj["orbit"]["elements"]["w"]

    # Since JPL provides Mean Anomaly (M) we need to make
    # the conversion to the true anomaly (nu)
    M = obj["orbit"]["elements"]["ma"].to(u.rad)
    # NOTE: It is unclear how this conversion should happen,
    # see https://ssd-api.jpl.nasa.gov/doc/sbdb.html
    if ecc < 1:
        M = (M + np.pi * u.rad) % (2 * np.pi * u.rad) - np.pi * u.rad
        nu = E_to_nu(M_to_E(M, ecc), ecc)
    elif ecc == 1:
        nu = D_to_nu(M_to_D(M))
    else:
        nu = F_to_nu(M_to_F(M, ecc), ecc)

    epoch = Time(obj["orbit"]["epoch"].to(u.d), format="jd")

    return Orbit.from_classical(
        attractor=Sun,
        a=a,
        ecc=ecc,
        inc=inc,
        raan=raan,
        argp=argp,
        nu=nu,
        epoch=epoch.tdb,
        plane=Planes.EARTH_ECLIPTIC,
    )
