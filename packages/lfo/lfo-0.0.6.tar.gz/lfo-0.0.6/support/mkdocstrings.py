#!/bin/env python3

from os.path import isdir

DOCSTRINGS = {
    'MODULE':
"""LFO - Low-Frequency-Oscillators for python

This class transfers the concept of LFOs from modylar synthesizers to python.

So what is an LFO?  LFO stands for "Low Frequency Oscillator".  It's an
infinitely repeating curve that you can pull out values from.  The simplest
form is probably a sine wave.  Regardless of how often you travel along the
circle, you always get consistent and reproducible values out of it.

But LFOs come in many different shapes.  Here are the ones implemented right
now (see further below for descriptions), but I'm open to suggestions to
extend this list:

    * lfo.sine, lfo.cosine
    * lfo.triangle
    * lfo.sawtooth
    * lfo.square
    * lfo.one
    * lfo.zero
    * lfo.random
    * lfo.inv_<waveform> - All of the above, but inverted

The lfo registers the start time of its instantiation.  If no period length -
the duration of one single wave - is provided, it defaults to 1 second.

Whenever you now query a value from the lfo, it gives you the proper function
result of that wave for this specific point in time.  Also, you can query all
of these wave forms from the same lfo.  The lfo instance basically just
defines the heartbeat for all the waves.

Each waveform can be scaled and offset.  Note, that the inverted waves use the
same scale and offset as the normal ones, otherwise they would run out of
sync.

There's one important difference to the lfo you might know from your DAW or
synth.  Since most programmers will use these to ramp other values by
multiplication, this lfo is not centered around the 0 point of the y axis, but
all waves except sine and cosine variants are positioned so that they return a
value between 0 and 1. There are per-wave parameters to change this.
""",

    'LFO':
"""The actual LFO class

The following settings can be passed to the init and during runtime as
attributes:

    period: float
        The duration of one full wave

    frequency: float
        The frequency of the LFO is `1 / period.

    cycles: int = 0
        Limit the number of cycles the LFO runs.

        If the number is reached, the LFO will constantly return the proper
        value for the `lfo.period` time.

        **NOTE**: That means that the random wave will continue, since it's
        value is not dependent of time.

        If the LFO us used as an iterator, ending the cycle will raise
        StopIteration.

        lfo.reset() will set the cycle counter back to 0.

    default_wave: lfo.Wave = lfo.Wave.sine
        Set the default wave form.

        **Note:**  This is not a runtime attribute.  Use
            lfo.set_default_wave(...) instead.

These attributes are read-only:

    t: float
        The current time within the current wave

    normalized: float
        The current time within the current wave, normalized to 0-1

    cycle: int
        The number of waves this LFO has completed

    frozen: bool
        The frozen status of the LFO.  Same as `lfo.is_frozen()`.

Wave attributes:

    Every wave attribute `lfo.<wave>` also provides an inverted variant
    `lfo.<inv_wave>`. All wave attributes have their own attenuverter and
    offset, `lfo.<wave>_attenuverter` and `lfo.<wave>_offset`
    respectively.  While `lfo.<wave>` and `lfo.inv_<wave>` are read-only,
    the attenuverters and offsets can be set in the init and during
    runtime.

    Waves:

        Sine/Cosine:
            sine
            cosine
            inv_sine
            inv_cosine
            sine_attenuverter
            cosine_attenuverter
            sine_offset
            cosine_offset

        Triangle:

            triangle
            inv_triangle
            triangle_attenuverter
            triangle_offset

        Sawtooth:
            sawtooth
            inv_sawtooth
            sawtooth_attenuverter
            sawtooth_offset

        Square:
            The square wave has two additional control parameters.  The
            pulsewidth `pw` is the duration the square wave is up.

            The pw_offset sets the start of the up-phase.  pw_offset is
            normalized to 0-1, so it wont be necessary to update it every
            time the wave is attenuverted.

            square
            inv_square
            square_attenuverter
            square_offset
            pw
            pw_offset

        Zero/One:
            one
            zero
            inv_one
            inv_zero
            one_attenuverter
            zero_attenuverter
            one_offset
            zero_offset

        Random
            random
            inv_random
            random_attenuverter
            random_offset


Additional methods and features:

    LFO compares properly with int, float and bool objects.
    LFO can be used as an iterator and is iterable.  The default for these is
    the sine wave.  Use `lfo.set_default_wave()` to change this.

    If lfo.cycles is not set, the lfo will run infinitely.

    If the LFO object is called as function, it will return the value of
    the sine wave (or the alternative given by `lfo.set_default_wave`).

""",

    'FREEZE':
"""Freeze the LFO

A frozen LFO returns the value at the time it was frozen.

When the LFO is unfrozen again, it will adjust its phase so, that the
wave will not jump.
""",

    'UNFREEZE':
"""Unfreeze a frozen the LFO

See "freeze".

Unfreezing an already running LFO does nothing.
""",

    'ISFROZEN':
"""Check if the LFO is frozen""",

    'RESET':
"""Reset the wave so it's starting point is now""",

    'SETATTENUVERTERS':
"""Set all attenuverters to `value`""",

    'SETOFFSETS':
"""Set all offsets to `value`""",

    'DEFAULTWAVE':
"""Set the default wave for lfo(), float(lfo), int(lfo) and bool(lfo)

    `LFO(default_wave=n)`
    `lfo.set_default_wave(n)`

Use the `Wave` Enum instead of plain numbers.  The fields match the
wavefunctions.  E.g.

    lfo.set_default_wave(Wave.inv_triangle)
    wave = LFO(default_wave=Wave.inv_sawtooth)

""",

    'REWIND':
"""Rewind the lfo by the by the given fraction in the range of 0-1.

The actual rewind time will be `passed_time * lfo.period`.  This way, the
rewind amount doens't need to be corrected when the period is changed.

""",

    'SKIP':
"""Skip the lfo by the by the given fraction in the range of 0-1.

The actual skip time will be `passed_time * lfo.period`.  This way, the skip
amount doens't need to be corrected when the period is changed.

""",

    'PERIOD':
"""The duration of one full wave. (rw)""",

    'FREQUENCY':
"""The frequency of the LFO (rw, 1 / period) (rw)""",

    'CYCLES':
"""Limit the number of cycles the LFO runs. (rw)""",

    'CYCLE':
"""The number of waves this LFO has completed. (rw)""",

    'FROZEN':
"""The frozen status of the LFO.  Same as `lfo.is_frozen()`. (ro)""",

    'T':
"""The current time within the current wave.  (ro)""",

    'NORMALIZED':
"""The current time within the current wave, normalized to 0-1.  (ro)""",

    'SINE':
"""The sine wave""",

    'COSINE':
"""The cosine wave""",

    'TRIANGLE':
"""The triangle wave""",

    'SAWTOOTH':
"""The sawtooth wave""",

    'SQUARE':
"""The square wave""",

    'ONE':
"""Constant 1 * attenuverter + offset""",

    'ZERO':
"""Constant 0 * attenuverter + offset""",

    'RANDOM':
"""The random wave""",

    'INV_SINE':
"""The inverted sine wave""",

    'INV_COSINE':
"""The inverted cosine wave""",

    'INV_TRIANGLE':
"""The inverted triangle wave""",

    'INV_SAWTOOTH':
"""The inverted sawtooth wave""",

    'INV_SQUARE':
"""The inverted square wave""",

    'INV_ONE':
"""The inverted one wave""",

    'INV_ZERO':
"""The inverted zero wave""",

    'INV_RANDOM':
"""The inverted random wave""",

    'SINE_ATTENUVERTER':
"""The attenuverter for sine""",

    'COSINE_ATTENUVERTER':
"""The attenuverter for cosine""",

    'TRIANGLE_ATTENUVERTER':
"""The attenuverter for triangle""",

    'SAWTOOTH_ATTENUVERTER':
"""The attenuverter for sawtooth""",

    'SQUARE_ATTENUVERTER':
"""The attenuverter for square""",

    'ONE_ATTENUVERTER':
"""The attenuverter for one""",

    'ZERO_ATTENUVERTER':
"""The attenuverter for zero""",

    'RANDOM_ATTENUVERTER':
"""The attenuverter for random""",

    'SINE_OFFSET':
"""The offset for sine""",

    'COSINE_OFFSET':
"""The offset for cosine""",

    'TRIANGLE_OFFSET':
"""The offset for triangle""",

    'SAWTOOTH_OFFSET':
"""The offset for sawtooth""",

    'SQUARE_OFFSET':
"""The offset for square""",

    'ONE_OFFSET':
"""The offset for one""",

    'ZERO_OFFSET':
"""The offset for zero""",

    'RANDOM_OFFSET':
"""The offset for random""",

    'PW':
"""The pulse width of the square wave""",

    'PW_OFFSET':
"""The offset of the pulse width of the square wave""",
}


if not isdir('include'):
    raise SystemExit('include/ directory missing.  Must be run in top of project directory')

with open('include/docstrings.h', 'w') as f:
    for name, docstring in DOCSTRINGS.items():
        ds = '\\n'.join(docstring.replace('"', '\\"').splitlines())
        print(f'#define DOCSTRING_{name} "{ds}"', file=f)
