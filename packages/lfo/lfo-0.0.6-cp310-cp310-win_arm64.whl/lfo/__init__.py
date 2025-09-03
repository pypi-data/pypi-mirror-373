from enum import IntEnum, auto

from lfo._lfo import LFO, __doc__  # noqa: F401

class Wave(IntEnum):
    sine = auto(0)
    cosine = auto()
    triangle = auto()
    sawtooth = auto()
    square = auto()
    one = auto()
    zero = auto()
    random = auto()
    inv_sine = auto()
    inv_cosine = auto()
    inv_triangle = auto()
    inv_sawtooth = auto()
    inv_square = auto()
    inv_one = auto()
    inv_zero = auto()
    inv_random = auto()
