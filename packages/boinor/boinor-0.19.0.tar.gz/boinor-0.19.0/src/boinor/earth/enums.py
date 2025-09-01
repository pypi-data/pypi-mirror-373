"""Earth Gravity perturbations."""

from enum import Enum, auto


class EarthGravity(Enum):
    """class to define different kind of perturbations."""

    SPHERICAL = auto()
    J2 = auto()
