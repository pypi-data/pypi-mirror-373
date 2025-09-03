L1 Science Calibration
======================

Introduction
------------

The `~dkist_processing_visp.tasks.science` module takes L0 input science frames and fully calibrates them into L1 science
products. This page describes the basic steps in this processes as well as import features of the ViSP algorithm that
may not be obvious.

Important Features
------------------

Pixel Units
^^^^^^^^^^^

The :doc:`gain arrays </gain_correction>` used to correct science data are *not* normalized; they retain their original input values.
As a result, pixel values in the L1 data will be normalized to the average solar signal at disk center on the day of calibration
acquisition (usually the same day as science acquisition). Note that this is **NOT** intended to be an accurate photometric calibration.

Beam Combination
^^^^^^^^^^^^^^^^

Apart from the order in which the basic corrections are applied (described below), it is important to state how the two
polarimetric beams of ViSP are combined to produce a single L1 data frame. After demodulation the 4 Stokes components of
the two beams are combined thusly:

.. math::

  I_{comb} &= (I_1 + I_2) / 2 \\
  Q_{comb} &= I_{comb} \left(\frac{Q_1}{I_1} + \frac{Q_2}{I_2}\right) / 2 \\
  U_{comb} &= I_{comb} \left(\frac{U_1}{I_1} + \frac{U_2}{I_2}\right) / 2 \\
  V_{comb} &= I_{comb} \left(\frac{V_1}{I_1} + \frac{V_2}{I_2}\right) / 2,

where numbered subscripts correspond to beam number. This combination scheme improves the signal-to-noise of the data
and mitigates residual polarization artifacts caused by temporal-based modulation (e.g., atmospheric seeing).

L1 Coordinate System
^^^^^^^^^^^^^^^^^^^^

The final step of the science pipeline places L1 data into a coordinate frame that matches the coordinates used by
SDO/HMI and HINDOE-SP. Namely, -Q and +Q will be aligned parallel and perpendicular to the central meridian of the Sun,
respectively.

Algorithm
---------

Input science data is processed into L1 science data via the following steps:

#. Dark and :doc:`background <background_light>` signals are subtracted from input data.

#. A :doc:`gain </gain_correction>` calibration frame is divided from the data.

#. :doc:`Geometric </geometric>` distortions (spectral rotation, x/y shift, spectral curvature) are removed via
   interpolation. This step aligns the dispersion axis with a pixel axis, places both beams on the same pixel grid, and
   straightens the spectra so that a single spectral pixel corresponds to the same physical wavelength for all locations
   along the slit.

#. :doc:`Demodulation </polarization_calibration>` matrices are applied.

#. The beams are combined as described above. For non-polarimetric data, the combination is a simple average.

#. The Telescope Polarization is removed. This removes the polarization effects of all DKIST mirrors upstream of ViSP.
   This step also includes the rotation into the coordinate frame described above.
