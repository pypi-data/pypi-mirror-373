Background Light Calibration
============================

.. note::
  A hardware fix for background light was implemented in November 2022. Data taken after Dec. 1st, 2022 are NOT
  processed with the algorithm described here. This page is preserved mainly for historical reasons.


**NOTE:** This page presents a general overview of the method used to identify background light. For the sake of brevity
there are a lot of small details that are not covered here.

Introduction
------------

The ViSP instrument has been shown to suffer from highly structured “background” light that affects all exposures.
There is an ongoing investigation to identify the exact source, but we currently know the following:

* It is NOT the so called “scattered” light that came from improper baffling of the instrument. This “background”
  light is likely caused by light that reflects around inside the instrument. Thus, baffling does not help mitigate this background light.

* It has a different signature (spatial and spectral) at different wavelengths and/or ViSP arms. As of this writing
  each arm has only observed a single wavelength so we can’t yet tell if the signal varies only with arm or wavelength (it’s probably both, though).

* It appears to be additive, much like a dark signal (this will be very important later). Thus it is most easily seen
  in frames with overall low flux.

The Background Light Algorithm
------------------------------

Background Light is Additive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The fundamental assumption of this algorithm is that the background light itself is additive (like a dark). Background
light is additive. A subtle point here is that the background signal will be constant at a particular exposure time;
a brighter source will not make a brighter background signal. Background light is additive.

POLCAL Frames Differ By a Multiplicative Factor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To understand the other piece of the puzzle we need to talk a little about the POLCAL task type. If you want to really
fall down the rabbit hole then check out `the docs of dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable/background.html>`_,
but the important thing to note is that every single POLCAL frame (except the darks, but we’ll ignore those) is
theoretically an exposure of exactly the same thing. Let's say that again: all POLCAL frames *observe* the same thing.
They have different values, however, because of polarizing optics that are placed in the beam path. Importantly, these
optics scale the input light by a constant multiple.

So to bring it all together, POCAL frames all *observe* the same thing, but *record* differently scaled values of that thing.

The Algorithm
^^^^^^^^^^^^^

To put what was just said into math we can say that the recorded signal, :math:`F_i`, for POLCAL frame :math:`i` can be written as

.. math::

  F_i = c_i f + B

where :math:`f` is the true, observed signal, :math:`c_i` is the multiplicative scale induced by polarizing optics,
and :math:`B` is the background light signal. Remember that :math:`f` is assumed to be constant for all POCAL frames.

Solving for :math:`f` we get

.. math::

  f = \frac{F_i - B}{c_i}

and arrive at the heart of the algorithm. With assumption that :math:`f` is constant we simply adjust :math:`B` until all
the inferred :math:`f` values are the same. In other words, we minimize the function

.. math::

  f(B) = \mathrm{stddev}_i\left(\frac{F_i - B}{c_i}\right)

If we have correctly measured :math:`B` then all of the recorded signals will be the same (modulo noise) and the
standard deviation will be very small.

Caveats and Limitations
^^^^^^^^^^^^^^^^^^^^^^^

The main issue here is that ViSP’s optics produce strong background light signals. Ultimately the best way to deal with
that is to fix it in the instrument itself. The algorithm presented above isn’t a perfect solution and comes with the
following caveats. It is only intended to get data “good enough” not “great”.

**Caveats**:

* Because the algorithm relies on POLCAL data it cannot be done when no POLCAL data exist. This means that
  “intensity only” ViSP observations are uncorrectable.

* The true observed signal, :math:`f`, actually does change over the course of a POCAL run because the Sun itself is changing.
  This is most evident in the spectral lines themselves, and the result is that part of these lines are identified as
  “background light”.

* This algorithm is very expensive and there is a huge trade-off between accuracy and time of execution (which can be
  10s of hours at the most accurate end). We are currently investigating how to get “good enough” in a reasonable time.

* We currently can make absolutely NO assumptions about the shape of the background signal, either spectrally or spatially,
  because the data we have show it to be very different across bandpass and ViSP arm. This means we need to sacrifice
  speed and accuracy for generality. In other words, the algorithm would be greatly improved if we could parameterize
  the background light, but we can’t.
