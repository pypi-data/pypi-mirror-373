

Polarization Calibration
========================

Introduction
------------

The `~dkist_processing_visp.tasks.instrument_polarization` pipeline task produces demodulation matrices from input polcal
data. For a more detailed background on how DKIST approaches polarization calibration please see
`this page about dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable/background.html>`_. Much of
the language and information in that page will be referenced here.

This page explains the specifics of how ViSP produces demodulation matrices and how its approach differs from the general,
default strategy mentioned in the link above.

Important Features
------------------

There are two options that ViSP uses to make it deviate from the "standard" polarization calibration routine, both of
which have import implications for the accuracy of L1 science data.

#. The total system throughput, :math:`I_{sys}`, is freely fit for every single GOS input state (i.e., Calibration
   Unit configuration). This change mitigates any variations in the total incident intensity that occur during a minutes-long PolCal
   data collection sequence (e.g., from solar granulation, humidity, etc.) and results in more precise fits to the Calibration Unit (CU)
   parameters. Note that this change necessitates fixing the CU retarder and polarizer transmission fractions to database
   values.

#. All "global" parameters are fit during the "local" fits. In other words, the CU retardances (in addition to modulation
   matrices) are fit separately for each bin in the polcal data. In the default polcal scheme only the modulation matrices
   are fit for each input bin. This change was made to partially correct for the real variations in the retardance of
   the calibration optics over the ViSP FOV.

The change in #2 above was required because ViSP highly samples the spatial dimension when computing demodulation matrices.
In fact, we currently compute a separate demodulation matrix for every single spatial pixel. These matrices are then
fit with a high-order polynomial along the slit to smooth out any outliers.

Algorithm Detail
----------------

The general algorithm is:

#. Correct input PolCal data with dark, :doc:`background <background_light>`, :doc:`gain </gain_correction>`, and
   :doc:`geometric </geometric>` calibrations.

#. Bin "global" and "local" sets of polcal data.

#. Pass the binned data to `dkist-processing-pac <https://docs.dkist.nso.edu/projects/pac/en/stable/index.html>`_ for fitting.

#. Smooth the resulting demodulation matrices along the slit.

#. Up-sample the binned demodulation matrices to span the full ViSP FOV.

Calibrate Input PoCal Data
^^^^^^^^^^^^^^^^^^^^^^^^^^

PoCal data are calibration in exactly the same way as input science data. They first have dark and background signals
removed, then are normalized by a gain image before finally having their :doc:`geometric </geometric>` distortions
(spectral rotation, x/y offset, and spectral curvature) removed.

Bin PolCal Data
^^^^^^^^^^^^^^^

`dkist-processing-pac` requires two sets of input data; one "global" set with high signal to noise to fit CU parameters,
and one "local" set with higher FOV sampling. The "global" set is simply a global median over the entire FOV.

As mentioned above, ViSP makes its "local" data by first computing the median along the spectral axis (i.e., collapse the
spectral axis to a single pixel). The spatial axis is then smoothed with a median filter to clean any bad pixels (the
width of this filter is controlled with the ``polcal_spatial_median_filter_width_px`` parameter). No further binning
is performed in the spatial dimension so that all spatial pixels will have their own separate demodulation matrix.

Send Data to dkist-processing-pac
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The "global" and "local" data are sent to `dkist-processing-pac` for fitting and demodulation matrix computation. See
`here <https://docs.dkist.nso.edu/projects/pac/en/stable/layout.html>`_ for detailed info.

Smooth Demodulation Matrices
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

While fitting demodulation matrices for every location along the slit does allow us to accurately capture real variations
in retardance over the FOV, pixel to pixel variations in the fit quality, as well as outliers, require further smoothing
prior to applying them to the science data. To mitigate the impact of these outliers each modulation matrix element is
fit with a high-order polynomial along the slit. It is these fit polynomials that are used as the true demodulation matrices.

Upsample Demodulation Matrices to the Full FOV
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Demodulation matrices are applied to science frames on a per-pixel basis, and thus we require a demodulation matrix for
every pixel. To do this the fit demodulation matrices are "upsampled" to match the full ViSP FOV. Because a separate demodulation
matrix was fit for every spatial pixel this step involves simply copying those demodulation matrices uniformly across
the wavelength axis.
