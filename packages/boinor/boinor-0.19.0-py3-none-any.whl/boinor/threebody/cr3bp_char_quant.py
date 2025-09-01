"""@author: Dhruv Jain, Multi-Body Dynamics Research Group, Purdue University."""
from astropy import units as u

from boinor.core.threebody.cr3bp_quantities_calculations import (
    calculate_mu,
    calculate_tstar,
)


class SystemChars:
    """Computes and stores the properties (mu, l*, t*) of a CR3BP system
    'mu': mass ratio of P1-P2 primary bodies
    'l*': characterisitic lenght of P1-P2 system
    't*': characterisitic time of P1-P2 system
    If P2 is more massive than P1 then swap the Pi, so that P1 is the more massive body.
    """

    def __init__(self, name, mu, lstar, tstar):
        """Constructor.

        Parameters
        ----------
        name: string
            System name, format: 'Body1Body2', e.g. 'EarthMoon', 'SunEarth'
        mu: float, dimensionless
           mass ratio of P1-P2 primary bodies
        lstar: float, km
           Characterisitc length of P1-P2 system
        tstar: float, sec
            Characterisitc time of P1-P2 system
        """
        self._name = name
        self._mu = mu
        self._lstar = lstar
        self._tstar = tstar
        self._L_ND = u.def_unit("dist_nd", u.one)
        self._V_ND = u.def_unit("vel_nd", u.one)
        self._T_ND = u.def_unit("time_nd", u.one)
        u.add_enabled_units("dist_nd")
        u.add_enabled_units("vel_nd")
        u.add_enabled_units("time_nd")

    @classmethod
    def from_primaries(cls, p1, p2):
        """Computes and sets the characteristic quanitites based on p1 and p2 bodies.

        Parameters
        ----------
        p1: ~boinor.bodies.Body
        p2: ~boinor.bodies.Body
        """
        name, mu, lstar, tstar = cls.bodies_char_compute(p1, p2)
        return cls(name, mu, lstar, tstar)

    @classmethod
    def bodies_char_compute(cls, p1, p2):
        """Calculates mu, lstar, and tstar of the 'p1' and 'p2' system.

        Also, if M2>M1, then swaps p1 and p2, so that M1>M2

        Parameters
        ----------
        p1: ~boinor.bodies.Body
        p2: ~boinor.bodies.Body

        Returns
        -------
        name: string
            System name, format: 'Body1Body2', e.g. 'EarthMoon', 'SunEarth'
        mu: float, dimensionless
           mass ratio of P1-P2 primary bodies
        lstar: float, km
           Characterisitc length of P1-P2 system
        tstar: float, sec
            Characterisitc time of P1-P2 system
        """
        assert (
            p1 == p2.parent or p2 == p1.parent
        ) is True, (
            "P1 and P2 are not part of the same system. Recheck body.parent"
        )

        if p1.k < p2.k:
            # swap p1 and p2, as p1 should be the more massive body
            p1, p2 = p2, p1

        name = p1.name + p2.name

        mu = calculate_mu(
            p1.k.to(u.km**3 * u.s**-2), p2.k.to(u.km**3 * u.s**-2)
        )
        lstar = p2.mean_a
        tstar = calculate_tstar(
            p1.k.to(u.km**3 * u.s**-2),
            p2.k.to(u.km**3 * u.s**-2),
            lstar,
        )

        return name, mu, lstar, tstar

    # All the attributes are made private to make them constant and avoid being mistakenly changed
    @property
    def name(self):
        """Name of P1-P2 system."""
        return self._name

    @property
    def mu(self):
        """Mass ratio of P1-P2 primary bodies in CR3BP."""
        return self._mu

    @property
    def lstar(self):
        """Characterisitc length of P1-P2 system."""
        return self._lstar

    @property
    def tstar(self):
        """Characterisitc time of P1-P2 system."""
        return self._tstar

    @property
    def L_ND(self):
        """Non-dimensional length unit of P1-P2 system"""
        return self._L_ND

    @property
    def V_ND(self):
        """Non-dimensional velocity unit of P1-P2 system"""
        return self._V_ND

    @property
    def T_ND(self):
        """Non-dimensional time unit of P1-P2 system"""
        return self._T_ND
