Geometric Calibration
=====================

Introduction
------------

The `~dkist_processing_visp.tasks.geometric` task does three things:

#. Compute the angle of rotation for each beam. This is the angle between the dispersion direction and the pixel axis of
   the detector. Applying/correcting this angle will align the dispersion direction with the pixel axes. The two beams
   are expected to have similar, but opposite angles.

#. Compute the (X, Y) offsets needed to align all modulation states for both beams with a single reference modulation
   state (currently modulation state 1 of beam 1). These offsets are caused by the "wobbling" of the ViSP modulator as
   it spins to different modulation states. After applying/correcting these state offsets the same (x, y) pixel will
   correspond to exactly the same (spectral, spatial) location for all modulation states in both beams.

#. Compute a relative wavelength calibration for each beam. After applying/correcting this calibration a single pixel
   in the spectral axis will correspond to the same physical wavelength across all spatial pixels. Because the relative
   wavelength calibration is computed after aligning all modulation states (step #2) the solution will be the same for both beams.

The results of these three calibrations are saved for use in downstream pipeline steps.

Generally speaking the full algorithm is broken down into the following steps. See below for more details on each step:

#. Gather dark-corrected lamp and solar gain frames

#. Calculate the rotation angle for each beam using lamp gain data

#. Remove the rotation angle from solar gain arrays

#. Using the angle-corrected solar gain arrays, find the state offsets for all modulation states across both beams

#. Remove state offsets from the angle-corrected solar gain arrays and average all of each beam's modulation states together

#. Calculate the spectral shifts (i.e., relative wavelength calibration) for each beam

Important Features
------------------

It is important to note that this pipeline step does NOT compute an *absolute* wavelength calibration; it only ensures
that all spectra are on the same *relative* wavelength scale.

Algorithm Detail
----------------

Gather Lamp and Solar Gain Images
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Raw input lamp and solar gain images are collected and have the corresponding dark signal removed. An average lamp and
solar gain image is then computed for each modulation state.

Calculate Rotation Angle
^^^^^^^^^^^^^^^^^^^^^^^^

The ViSP hairlines are two small dark spots at the slit aperture that create strong, sharp dark regions that are prefectly
aligned with the dispersion direction. These hairlines are used as fiducials to compute the angle between the dispersion
direction and the camera pixel axes using the following steps. All of these steps are performed on lamp gain frames because
solar gain frames have strong spectral features that complicate the separation of the hairlines from the background.

#. For each modulation state the hairline signals are roughly identified. In some cases there can be more two hairlines
   in a single beam image. These "extra" hairlines are likely caused by dust on the slit, but their presence can
   actually improve the precision of the angle measurement.

#. A single angle is found for each hairline by:

   #. Creating a binary image that separates hairline pixels from background pixels. This is done by taking a difference
      between a lamp gain array and a median smoothed version of the same array. The strong signal of the hairlines stands
      out in this difference.

   #. Use the binary image to get an initial guess for the hairline center as a function of spectral pixel. This is a simple
      center-of-mass calculation.

   #. Use the rough centers as starting guesses to refine the hairline centers by fitting a Gaussian to each spectral pixel.

   #. Fit a line to the refined hairline centers as a function of spectral pixel.

   #. The angle between the hairline direction (i.e., dispersion direction) and the pixel axis is the arc-tangent of the
      slope of the fit line.

#. Take the median of all angles computed across all hairlines for all modulation states for a single beam. This median
   is the final rotation angle for this beam.

#. Repeat the above steps for the second beam.

We expect the rotation angles for each of the two beams to be opposites of each other. Repeated testing has shown that
computing the angles for each beam completely independent of one another can lead to small, but noticeable, misalignment
when the two beams are combined. As a result a final step is to refine the angle of beam 2 by comparing it directly with
data from beam 1. This refinement is always small (<< 0.1 deg), and improves the results of beam combination in the Science
task.

Remove Rotation Angle
^^^^^^^^^^^^^^^^^^^^^

The computed rotation angles are removed/corrected from the previously prepared solar gain images. After this correction
the dispersion direction is aligned with the pixel axes.

Calculate State Offsets
^^^^^^^^^^^^^^^^^^^^^^^

This step aligns all modulation states from both beams to the same pixel coordinates. The alignment is measured with
arrays that have had their rotation angle removed, and the transformation is constrained to be a simple shift in both
pixel dimensions. Solar gain images are used because the hairline and solar spectral lines provide strong correlation
signals in the spatial and spectral dimensions, respectively.

The first modulation state from beam 1 is chosen as the reference image and the shifts are found with scikit-image's
`phase cross correlation <https://scikit-image.org/docs/stable/api/skimage.registration.html#skimage.registration.phase_cross_correlation>`_.
To enhance the signal of the hairlines and spectral lines, and to mitigate the effects of any large-scale illumination
difference, all arrays are sent through a high-pass filter before being correlated.

Remove Modstate Offsets
^^^^^^^^^^^^^^^^^^^^^^^

The per-modulation-state offsets measured in the previous step are removed/corrected from the angle-corrected solar gain
images. After this correction the same (x, y) pixel location corresponds to the same (spectral, spatial) location in
all modulation states across both beams.

After the offset correction has been applied, all modulation states for a single beam are averaged together. This improves
the signal-to-noise for the next step.

Relative Wavelength Calibration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step removes spectral curvature along the slit and ensures that a single spectral pixel corresponds to the same
wavelength for all spatial pixels.

The relative wavelength solution is parameterized as simple spectral shifts as a function of spatial pixel, with the
spectrum at slit center is used as a reference. For each spatial pixel a rough offset is measured by correlating that
spectrum with the reference spectrum. The shift is then refined with a chi-squared minimization.

After all spatial pixels have had their shifts measured, the shift amount as a function of spatial position is fit with
a polynomial, which helps mitigate noise in the individual shifts. The polynomial fit order is a pipeline parameter.
