"""Low level calculations for oblate spheroid locations."""

from numba import njit as jit
import numpy as np

from boinor._math.linalg import norm


@jit
def cartesian_cords(a, c, lon, lat, h):
    """Calculates cartesian coordinates.

    Parameters
    ----------
    a : float
        Semi-major axis
    c : float
        Semi-minor axis
    lon : float
        Geodetic longitude
    lat : float
        Geodetic latitude
    h : float
        Geodetic height


    ND: float
       prime vertical radius of curvature (normal distance from the ellipsoid surface to the polar axis)
       sometimes called N
    """
    e2 = 1 - (c / a) ** 2
    ND = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)

    x = (ND + h) * np.cos(lat) * np.cos(lon)
    y = (ND + h) * np.cos(lat) * np.sin(lon)
    z = ((1 - e2) * ND + h) * np.sin(lat)
    return x, y, z


@jit
def f(a, c):
    """Get first flattening.

    Parameters
    ----------
    a : float
        Semi-major axis
    c : float
        Semi-minor axis

    """
    return 1 - c / a


@jit
def N(a, b, c, cartesian_cords_parameter):
    """Normal vector of the ellipsoid at the given location.

    Parameters
    ----------
    a : float
        Semi-major axis
    b : float
        Equatorial radius
    c : float
        Semi-minor axis
    cartesian_cords_parameter : numpy.ndarray
        Cartesian coordinates

    """
    x, y, z = cartesian_cords_parameter
    ND = np.array([2 * x / a**2, 2 * y / b**2, 2 * z / c**2])
    ND /= norm(ND)
    return ND


@jit
def tangential_vecs(ND):
    """Returns orthonormal vectors tangential to the ellipsoid at the given location.

    Parameters
    ----------
    ND : numpy.ndarray
         Normal vector of the ellipsoid

    """
    u = np.array([1.0, 0, 0])
    u -= (u @ ND) * ND
    u /= norm(u)
    v = np.cross(ND, u)

    return u, v


@jit
def radius_of_curvature(a, c, lat):
    """Radius of curvature of the meridian at the latitude of the given location.

    Parameters
    ----------
    a : float
        Semi-major axis
    c : float
        Semi-minor axis
    lat : float
        Geodetic latitude

    """
    e2 = 1 - (c / a) ** 2
    rc = a * (1 - e2) / (1 - e2 * np.sin(lat) ** 2) ** 1.5
    return rc


@jit
def distance(cartesian_cords_parameter, px, py, pz):
    """Calculates the distance from an arbitrary point to the given location (Cartesian coordinates).

    Parameters
    ----------
    cartesian_cords_parameter : numpy.ndarray
        Cartesian coordinates
    px : float
        x-coordinate of the point
    py : float
        y-coordinate of the point
    pz : float
        z-coordinate of the point

    """
    c = cartesian_cords_parameter
    u = np.array([px, py, pz])
    d = norm(c - u)
    return d


@jit
def is_visible(cartesian_cords_parameter, px, py, pz, ND):
    """Determine whether an object located at a given point is visible from the given location.

    Parameters
    ----------
    cartesian_cords_parameter : numpy.ndarray
        Cartesian coordinates
    px : float
        x-coordinate of the point
    py : float
        y-coordinate of the point
    pz : float
        z-coordinate of the point
    ND : numpy.ndarray
         Normal vector of the ellipsoid at the given location.

    """
    c = cartesian_cords_parameter
    u = np.array([px, py, pz])

    d = -(ND @ c)
    p = (ND @ u) + d
    return p >= 0


@jit
def cartesian_to_ellipsoidal(a, c, x, y, z):
    """Converts cartesian coordinates to ellipsoidal coordinates for the given ellipsoid.
    Instead of the iterative formula, the function uses the approximation introduced in
    Bowring, B. R. (1976). TRANSFORMATION FROM SPATIAL TO GEOGRAPHICAL COORDINATES.

    Parameters
    ----------
    a : float
        Semi-major axis
    c : float
        Semi-minor axis
    x : float
        x coordinate
    y : float
        y coordinate
    z : float
        z coordinate

    """
    e2 = 1 - (c / a) ** 2
    e2_ = e2 / (1 - e2)
    p = np.sqrt(x**2 + y**2)
    th = np.arctan(z * a / (p * c))
    lon = np.arctan2(
        y, x
    )  # Use `arctan2` so that lon lies in the range: [-pi, +pi]
    lat = np.arctan(
        (z + e2_ * c * np.sin(th) ** 3) / (p - e2 * a * np.cos(th) ** 3)
    )

    v = a / np.sqrt(1 - e2 * np.sin(lat) ** 2)
    h = (
        np.sqrt(x**2 + y**2) / np.cos(lat) - v
        if lat < abs(1e-18)  # to avoid errors very close and at zero
        else z / np.sin(lat) - (1 - e2) * v
    )

    return lon, lat, h
