from pytest import approx, fixture, raises
from time import sleep

from lfo import LFO, Wave


@fixture
def lfo04():
    return LFO(0.4)


@fixture
def lfo1():
    return LFO()


@fixture
def lfo10():
    return LFO(10)


def test_defaults(lfo1):
    assert lfo1.period == 1
    assert lfo1.frequency == 1

    assert not lfo1.frozen

    assert lfo1.cycle == 0
    assert lfo1.cycles == 0

    assert lfo1.sine_attenuverter == 1.0
    assert lfo1.sine_offset == 0.0

    assert lfo1.cosine_attenuverter == 1.0
    assert lfo1.cosine_offset == 0.0

    assert lfo1.triangle_attenuverter == 1.0
    assert lfo1.triangle_offset == 0.0

    assert lfo1.sawtooth_attenuverter == 1.0
    assert lfo1.sawtooth_offset == 0.0

    assert lfo1.square_attenuverter == 1.0
    assert lfo1.square_offset == 0.0
    assert lfo1.pw == 0.5
    assert lfo1.pw_offset == 0.5

    assert lfo1.one_attenuverter == 1.0
    assert lfo1.one_offset == 0.0

    assert lfo1.zero_attenuverter == 1.0
    assert lfo1.zero_offset == 0.0

    assert lfo1.random_attenuverter == 1.0
    assert lfo1.random_offset == 0.0

    # assert approx(lt(), 0.01) == approx(lt(), 0.01)


def test_period_and_frequency(lfo10):
    assert lfo10.period == 10
    assert lfo10.frequency == 0.1

    lfo10.frequency = 0.5
    assert lfo10.period == 2

    lfo10.period = 4
    assert lfo10.frequency == 0.25


def test_sine(lfo1):
    sine, inv_sine, = lfo1.sine, lfo1.inv_sine

    assert approx(sine, abs=0.025) == 0.0
    assert approx(inv_sine, abs=0.025) == 0.0

    sleep(0.25)
    sine, inv_sine, = lfo1.sine, lfo1.inv_sine
    assert approx(sine, abs=0.025) == 1.0
    assert approx(inv_sine, abs=0.025) == -1.0


def test_cosine(lfo1):
    cosine, inv_cosine, = lfo1.cosine, lfo1.inv_cosine

    assert approx(cosine, abs=0.025) == 1.0
    assert approx(inv_cosine, abs=0.025) == -1.0

    sleep(0.25)
    cosine, inv_cosine, = lfo1.cosine, lfo1.inv_cosine
    assert approx(cosine, abs=0.025) == 0.0
    assert approx(inv_cosine, abs=0.025) == 0.0


def test_triangle(lfo1):
    triangle, inv_triangle = lfo1.triangle, lfo1.inv_triangle

    assert approx(triangle, abs=0.025) == 0.0
    assert approx(inv_triangle, abs=0.025) == 1.0

    sleep(0.25)
    triangle, inv_triangle = lfo1.triangle, lfo1.inv_triangle
    assert approx(triangle, abs=0.025) == 0.5
    assert approx(inv_triangle, abs=0.025) == 0.5

    sleep(0.25)
    triangle, inv_triangle = lfo1.triangle, lfo1.inv_triangle
    assert approx(triangle, abs=0.025) == 1
    assert approx(inv_triangle, abs=0.025) == 0.0

    sleep(0.5)
    triangle, inv_triangle = lfo1.triangle, lfo1.inv_triangle
    assert approx(triangle, abs=0.025) == 0.0
    assert approx(inv_triangle, abs=0.025) == 1.0


def test_sawtooth(lfo1):
    sawtooth, inv_sawtooth = lfo1.sawtooth, lfo1.inv_sawtooth

    assert approx(sawtooth, abs=0.025) == 1.0
    assert approx(inv_sawtooth, abs=0.025) == 0.0

    sleep(0.25)
    sawtooth, inv_sawtooth = lfo1.sawtooth, lfo1.inv_sawtooth
    assert approx(sawtooth, abs=0.025) == 0.75
    assert approx(inv_sawtooth, abs=0.025) == 0.25

    sleep(0.25)
    sawtooth, inv_sawtooth = lfo1.sawtooth, lfo1.inv_sawtooth
    assert approx(sawtooth, abs=0.025) == 0.5
    assert approx(inv_sawtooth, abs=0.025) == 0.5

    # Sleep just short of 1 since the sawtooth makes a jump that's outside
    # approx when it wraps
    sleep(0.49)
    sawtooth, inv_sawtooth = lfo1.sawtooth, lfo1.inv_sawtooth
    assert approx(sawtooth, abs=0.025) == 0.0
    assert approx(inv_sawtooth, abs=0.025) == 1.0


def test_square(lfo1):
    square, inv_square = lfo1.square, lfo1.inv_square

    assert approx(square, abs=0.025) == 0.0
    assert approx(inv_square, abs=0.025) == 1.0

    sleep(0.49)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert approx(square, abs=0.025) == 0.0
    assert approx(inv_square, abs=0.025) == 1.0

    sleep(0.02)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert approx(square, abs=0.025) == 1.0
    assert approx(inv_square, abs=0.025) == 0.0

    lfo1.reset()
    lfo1.pw = 0.2
    lfo1.pw_offset = 0.4

    sleep(0.39)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert square == 0
    assert inv_square == 1

    sleep(0.02)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert square == 1
    assert inv_square == 0

    sleep(0.18)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert square == 1
    assert inv_square == 0

    sleep(0.02)
    square, inv_square = lfo1.square, lfo1.inv_square
    assert square == 0
    assert inv_square == 1


def test_one_and_zero(lfo1):
    one, inv_one, zero, inv_zero = lfo1.one, lfo1.inv_one, lfo1.zero, lfo1.inv_zero

    assert one == 1.0
    assert inv_one == 0.0
    assert zero == 0.0
    assert inv_zero == 1.0

    sleep(0.25)
    assert one == 1.0
    assert inv_one == 0.0
    assert zero == 0.0
    assert inv_zero == 1.0


def test_random(lfo1):
    assert approx(lfo1.random, abs=0.001) != lfo1.random

    rand, inv_rand = lfo1.random, lfo1.inv_random
    assert rand != 1 - inv_rand


def test_attenuverters(lfo1):
    lfo1.set_attenuverters(2)
    sleep(0.5)
    (
        sine, inv_sine,
        cosine, inv_cosine,
        triangle, inv_triangle,
        sawtooth, inv_sawtooth,
        square, inv_square,
        one, inv_one,
        zero, inv_zero,
    ) = (
        lfo1.sine, lfo1.inv_sine,
        lfo1.cosine, lfo1.inv_cosine,
        lfo1.triangle, lfo1.inv_triangle,
        lfo1.sawtooth, lfo1.inv_sawtooth,
        lfo1.square, lfo1.inv_square,
        lfo1.one, lfo1.inv_one,
        lfo1.zero, lfo1.inv_zero,
    )

    assert approx(sine, abs=0.025) == 0.0
    assert approx(inv_sine, abs=0.025) == 0.0
    assert approx(cosine, abs=0.025) == -2.0
    assert approx(inv_cosine, abs=0.025) == 2.0
    assert approx(triangle, abs=0.025) == 2.0
    assert approx(inv_triangle, abs=0.025) == 0.0
    assert approx(sawtooth, abs=0.025) == 1.0
    assert approx(inv_sawtooth, abs=0.025) == 1.0
    assert approx(square, abs=0.025) == 2.0
    assert approx(inv_square, abs=0.025) == 0.0
    assert approx(one, abs=0.025) == 2.0
    assert approx(inv_one, abs=0.025) == 0.0
    assert approx(zero, abs=0.025) == 0.0
    assert approx(inv_zero, abs=0.025) == 2.0
    assert any(lfo1.random > 1 for _ in range(100))
    assert any(lfo1.random > 1 for _ in range(100))


def test_offsets(lfo1):
    lfo1.set_offsets(1)
    sleep(0.5)
    (
        sine, inv_sine,
        cosine, inv_cosine,
        triangle, inv_triangle,
        sawtooth, inv_sawtooth,
        square, inv_square,
        one, inv_one,
        zero, inv_zero,
    ) = (
        lfo1.sine, lfo1.inv_sine,
        lfo1.cosine, lfo1.inv_cosine,
        lfo1.triangle, lfo1.inv_triangle,
        lfo1.sawtooth, lfo1.inv_sawtooth,
        lfo1.square, lfo1.inv_square,
        lfo1.one, lfo1.inv_one,
        lfo1.zero, lfo1.inv_zero,
    )

    assert approx(sine, abs=0.025) == 1.0
    assert approx(inv_sine, abs=0.025) == 1.0
    assert approx(cosine, abs=0.025) == 0.0
    assert approx(inv_cosine, abs=0.025) == 2.0
    assert approx(triangle, abs=0.025) == 2.0
    assert approx(inv_triangle, abs=0.025) == 1.0
    assert approx(sawtooth, abs=0.025) == 1.5
    assert approx(inv_sawtooth, abs=0.025) == 1.5
    assert approx(square, abs=0.025) == 2.0
    assert approx(inv_square, abs=0.025) == 1.0
    assert approx(one, abs=0.025) == 2.0
    assert approx(inv_one, abs=0.025) == 1.0
    assert approx(zero, abs=0.025) == 1.0
    assert approx(inv_zero, abs=0.025) == 2.0
    assert all(lfo1.random > 1 for _ in range(100))
    assert all(lfo1.random > 1 for _ in range(100))


def test_cycles(lfo1):
    lfo1.cycles = 1
    sleep(1.5)
    (
        sine, inv_sine,
        cosine, inv_cosine,
        triangle, inv_triangle,
        sawtooth, inv_sawtooth,
        square, inv_square,
        one, inv_one,
        zero, inv_zero,
    ) = (
        lfo1.sine, lfo1.inv_sine,
        lfo1.cosine, lfo1.inv_cosine,
        lfo1.triangle, lfo1.inv_triangle,
        lfo1.sawtooth, lfo1.inv_sawtooth,
        lfo1.square, lfo1.inv_square,
        lfo1.one, lfo1.inv_one,
        lfo1.zero, lfo1.inv_zero,
    )

    assert approx(sine, abs=0.025) == 0.0
    assert approx(inv_sine, abs=0.025) == 0.0
    assert approx(cosine, abs=0.025) == 1.0
    assert approx(inv_cosine, abs=0.025) == -1.0
    assert approx(triangle, abs=0.025) == 0.0
    assert approx(inv_triangle, abs=0.025) == 1.0
    assert approx(sawtooth, abs=0.025) == 0.0
    assert approx(inv_sawtooth, abs=0.025) == 1.0
    assert approx(square, abs=0.025) == 1.0
    assert approx(inv_square, abs=0.025) == 0.0
    assert approx(one, abs=0.025) == 1.0
    assert approx(inv_one, abs=0.025) == 0.0
    assert approx(zero, abs=0.025) == 0.0
    assert approx(inv_zero, abs=0.025) == 1.0


def test_set_default_wave(lfo1):
    lfo1.set_default_wave(Wave.triangle)
    sleep(0.5)
    assert approx(lfo1(), abs=0.025) == 1.0

    lfo1.set_default_wave(Wave.inv_sawtooth)
    lfo1.reset()
    assert approx(lfo1(), abs=0.025) == 0.0
    sleep(0.5)
    assert approx(lfo1(), abs=0.025) == 0.5

    lfo = LFO(default_wave=Wave.sawtooth)
    assert approx(lfo(), abs=0.025) == 1.0
    sleep(0.5)
    assert approx(lfo(), abs=0.025) == 0.5


def test_richcompare(lfo1):
    lfo1.set_default_wave(Wave.inv_sawtooth)

    assert lfo1 < 0.1
    sleep(0.5)
    assert lfo1 > 0.5
    assert lfo1 < lfo1
    assert not (lfo1 > lfo1)


def test_conversions(lfo1):
    lfo1.set_default_wave(Wave.inv_sawtooth)
    lfo1.sawtooth_attenuverter = 2.0

    assert approx(float(lfo1), abs=0.025) == 0
    assert int(lfo1) == 0
    assert not bool(lfo1)

    sleep(0.5)
    assert float(lfo1) > 1.0
    assert int(lfo1) == 1
    assert bool(lfo1)


def test_rewind_skip(lfo1):
    lfo1.reset()
    sleep(0.5)

    lfo1.rewind(0.1)
    assert approx(lfo1.t, abs=0.025) == 0.4

    lfo1.skip(0.2)
    assert approx(lfo1.t, abs=0.025) == 0.6

    with raises(TypeError):
        lfo1.rewind('xyzzy')
    with raises(TypeError):
        lfo1.skip('xyzzy')
