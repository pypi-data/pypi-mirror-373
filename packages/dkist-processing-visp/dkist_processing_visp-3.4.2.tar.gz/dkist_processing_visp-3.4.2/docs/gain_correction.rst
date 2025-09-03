Gain Calibration
================

Introduction
------------

NOTE: The usage of the term "gain" throughout this document refers to total system response of the DKIST/ViSP optical
train; it does NOT refer to the detector gain that has units of ADU / electron. Sometimes the term "flat" is used in
a way that is interchangeable with the usage of "gain" in this document.

The ViSP gain calibration is broken down into the following steps across two pipeline tasks
(`~dkist_processing_visp.tasks.lamp` and `~dkist_processing_visp.tasks.solar`). Each step is explained in more detail below.

#. Subtract dark and :doc:`background <background_light>` signals from all input gain images.

#. Compute an average, equalized lamp gain and mask the hairlines.

#. Divide the solar gain by the resulting lamp image and correct for :doc:`geometric </geometric>` rotation/shifts and
   spectral curvature.

#. Mask hairlines and compute 2D characteristic solar spectra with spatial median filter.

#. Re-curve/shift/rotate the characteristic spectra into the same coordinates as the input frames.

#. Remove the characteristic spectra from solar gain images that have NOT had a lamp correction applied.

The result is a final gain image that can be applied to science data. Note that all steps happen separately for every
modulator state and beam. This is because the geometric x/y shifts have been found to be significantly different for each
modulator state and beam.

Important Features
------------------

The final gain images (those used to correct science frames) are *not* normalized; they retain their original input values.
As a result, pixel values in the L1 data will be normalized to the average solar signal at disk center on the day of calibration
acquisition (usually the same day as science acquisition). Note that this is **NOT** intended to be an accurate photometric calibration.

Algorithm Detail
----------------

Subtract Dark and Background Signals
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is exactly how it sounds. Pre-computed dark and :doc:`background light <background_light>` frames are subtracted
from all input frames.

.. _hairline-description:

Average Lamp Frames and Mask Hairlines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All lamp frames for a particular modulator state and beam are averaged into a single array. The slit hairlines are then
identified by smoothing the image in the spatial dimension and then computing the relative difference between this smoothed
image and the original image. Any pixels that deviate by a large amount (set by the ``hairline_fraction`` parameter) are
considered to be hairline pixels. These hairline pixels are masked by replacing them with values from the smoothed array.

Lamp gains for all modulator states are then compared and equalized so each individual modulator state has the same
median as the median of all (pre-equalized) modulator states. This step helps to mitigate any residual polarization that
may exist in input gain images that would otherwise affect the residual continuum polarization in the processed
science frames.

Finally, all lamp gain images have any spatial intensity gradients removed by normalizing each spatial position by its
median. This removes known gradients caused by the different input illumination of the lamp compared to the Sun.

Prepare and Rectify Solar Frames
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The averaged modulated lamp frames from the previous step are applied to dark/background subtracted solar gain frames through
division. Then the pre-computed :doc:`geometric </geometric>` correction removes any spectral rotation, x/y shifts, and
spectral curvature (in that order). At the end of this step the dispersion axis will be parallel to a pixel axis and a
single spectral pixel will have the same physical wavelength value for all spatial pixels.

Compute Characteristic Spectra
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First, the slit hairlines are masked using the same method as :ref:`above <hairline-description>`.

The goal of this step is to derive pure solar spectra, free from any optical effects of the DKIST/ViSP system. By applying
lamp gain frames to our solar images we have already removed a lot of optical effects, but some spatial variations still
remain. Thus, the characteristic spectra is computed by applying a median filter (with width controlled by the
``solar_spectral_avg_window`` parameter) in the spatial direction. Previously, a single, median spectrum had been used,
but it did not accurately capture small, but important variations in spectral shape along the slit.

Finally, the smooth characteristic spectra has any spatial gradients removed by normalizing each spatial positions by its
median. This ensures that the characteristic spectra contain *only* pure solar spectra, and thus any real spatial
gradients are preserved in the final gain image. This normalization also ensures the absolute flux of the final
gain images is preserved so that science frames will have values relative to average disk center (where the solar images
are taken).

Un-rectify Characteristic Spectra
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The characteristic spectra have spectral shifts, x/y offsets, and spectral rotation re-applied to bring them back into
raw input pixel coordinates.

The spectral curvature is NOT applied using the precomputed curvature. Instead, for each spatial position a new spectral
shift is computed that minimizes the residual of the final gain image at that position. This step is needed because the
characteristic spectra have *slightly* different spectral shapes than the input solar image (see above) and any small
misalignment causes large, sharp residuals in the line wings. By explicitly minimizing final gain residuals we ensure
that the new spectral shifts remove the solar signal as much as possible.

Remove Characteristic Solar Spectra from Input Solar Frames
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The dark/background corrected solar gain image is simply divided by the re-distorted characteristic spectra. Because we
do NOT use a solar image with a lamp correction applied, the resulting gain image includes the full optical response of
the system and can be applied directly to the science data.

As mentioned above, these gain calibration images are not normalized. The result is that L1 science data will have
values that are relative to solar disk center (where the solar gain images are observed).
