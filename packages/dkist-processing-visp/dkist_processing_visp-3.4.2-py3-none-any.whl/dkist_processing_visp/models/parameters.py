"""Visp calibration pipeline parameters."""

from datetime import datetime

from dkist_processing_common.models.parameters import ParameterBase
from dkist_processing_common.models.parameters import ParameterWavelengthMixin


class VispParsingParameters(ParameterBase):
    """
    Parameters specifically (and only) for the Parse task.

    Needed because the Parse task doesn't know what the wavelength is yet and therefore can't use the
    `ParameterWaveLengthMixin`.
    """

    @property
    def max_cs_step_time_sec(self):
        """Time window within which CS steps with identical GOS configurations are considered to be the same."""
        return self._find_most_recent_past_value(
            "visp_max_cs_step_time_sec", start_date=datetime.now()
        )


class VispParameters(ParameterBase, ParameterWavelengthMixin):
    """Put all Visp parameters parsed from the input dataset document in a single property."""

    @property
    def beam_border(self):
        """Pixel location of the border between ViSP beams."""
        return self._find_most_recent_past_value("visp_beam_border")

    @property
    def background_on(self) -> bool:
        """Return True if background light correct should be done."""
        return self._find_most_recent_past_value("visp_background_on")

    @property
    def background_num_spatial_bins(self) -> int:
        """Return number of spatial bins to use when computing background light."""
        return self._find_parameter_closest_wavelength("visp_background_num_spatial_bins")

    @property
    def background_wavelength_subsample_factor(self) -> int:
        """Return the sub-sampling factor used to reduce the number of wavelength samples."""
        return self._find_parameter_closest_wavelength(
            "visp_background_wavelength_subsample_factor"
        )

    @property
    def background_num_fit_iterations(self) -> int:
        """Maximum number of fit iterations used to fit the background light."""
        return self._find_parameter_closest_wavelength("visp_background_num_fit_iterations")

    @property
    def background_continuum_index(self) -> list:
        """Return indices of a region to use when normalizing modulated polcals in the background task."""
        return self._find_parameter_closest_wavelength("visp_background_continuum_index")

    @property
    def hairline_median_spatial_smoothing_width_px(self) -> int:
        """Size of median filter in the spatial dimension with which to smooth data for hairline identification."""
        return self._find_most_recent_past_value("visp_hairline_median_spatial_smoothing_width_px")

    @property
    def hairline_fraction(self):
        """Relative difference from median used to identify slit positions covered by the hairlines."""
        return self._find_most_recent_past_value("visp_hairline_fraction")

    @property
    def hairline_mask_spatial_smoothing_width_px(self) -> float:
        """Amount to smooth the hairling mask in the spatial direction.

        This helps capture the higher-flux wings of the hairlines that would otherwise require a `hairline_fraction`
        that was so low it captures other optical features.
        """
        return self._find_most_recent_past_value("visp_hairline_mask_spatial_smoothing_width_px")

    @property
    def hairline_mask_gaussian_peak_cutoff_fraction(self) -> float:
        """Fraction of the maximum smoothed mask value used to truncate the smoothed mask.

        This ensures that very very small values way out in the wings are not included in the mask. For example, if
        this value is 0.01 then any mask points less than 1% of the maximum will be ignored.
        """
        return self._find_most_recent_past_value("visp_hairline_mask_gaussian_peak_cutoff_fraction")

    @property
    def geo_binary_opening_diameter(self) -> int:
        """
        Diameter threshold of morphological opening performed on binary image prior to spatial smoothing.

        The opening removes dot-like feautres that are smaller than the given diameter. Because the hairlines are long
        and thin it is hard to set this value too high.
        """
        return self._find_most_recent_past_value("visp_geo_binary_opening_diameter")

    @property
    def geo_hairline_flat_id_threshold(self) -> float:
        """Minimum fraction of binary pixels in a single spatial column for that column to be considered a hairline."""
        return self._find_most_recent_past_value("visp_geo_hairline_flat_id_threshold")

    @property
    def geo_hairline_fit_width_px(self) -> int:
        """Plus/minus distance around initial guess to look at when fitting a Gaussian to the hairline signal."""
        return self._find_most_recent_past_value("visp_geo_hairline_fit_width_px")

    @property
    def geo_hairline_angle_fit_sig_clip(self) -> float:
        """Plus/minus number of standard deviations away from the median used to clip bad hairline center fits.

        Clipping deviant values can greatly improve the fit to the slope and thus the beam angle.
        """
        return self._find_most_recent_past_value("visp_geo_hairline_angle_fit_sig_clip")

    @property
    def geo_max_beam_2_angle_refinement(self) -> float:
        """Maximum allowable refinement to the beam 2 spectral tilt angle, in radians."""
        return self._find_most_recent_past_value("visp_geo_max_beam_2_angle_refinement")

    @property
    def geo_upsample_factor(self):
        """Pixel precision (1/upsample_factor) to use during phase matching of beam/modulator images."""
        return self._find_most_recent_past_value("visp_geo_upsample_factor")

    @property
    def geo_max_shift(self):
        """Max allowed pixel shift when computing spectral curvature."""
        return self._find_most_recent_past_value("visp_geo_max_shift")

    @property
    def geo_poly_fit_order(self):
        """Order of polynomial used to fit spectral shift as a function of slit position."""
        return self._find_most_recent_past_value("visp_geo_poly_fit_order")

    @property
    def solar_spectral_avg_window(self):
        """Pixel width of spatial median filter used to compute characteristic solar spectra."""
        return self._find_parameter_closest_wavelength("visp_solar_spectral_avg_window")

    @property
    def solar_characteristic_spatial_normalization_percentile(self) -> float:
        """Percentile to pass to `np.nanpercentile` when normalizing each spatial position of the characteristic spectra."""
        return self._find_most_recent_past_value(
            "visp_solar_characteristic_spatial_normalization_percentile"
        )

    @property
    def solar_zone_prominence(self):
        """Relative peak prominence threshold used to identify strong spectral features."""
        return self._find_parameter_closest_wavelength("visp_solar_zone_prominence")

    @property
    def solar_zone_width(self):
        """Pixel width used to search for strong spectral features."""
        return self._find_parameter_closest_wavelength("visp_solar_zone_width")

    @property
    def solar_zone_bg_order(self):
        """Order of polynomial fit used to remove continuum when identifying strong spectral features."""
        return self._find_parameter_closest_wavelength("visp_solar_zone_bg_order")

    @property
    def solar_zone_normalization_percentile(self):
        """Fraction of CDF to use for normalzing spectrum when search for strong features."""
        return self._find_parameter_closest_wavelength("visp_solar_zone_normalization_percentile")

    @property
    def solar_zone_rel_height(self):
        """Relative height at which to compute the width of strong spectral features."""
        return self._find_most_recent_past_value("visp_solar_zone_rel_height")

    @property
    def polcal_spatial_median_filter_width_px(self) -> int:
        """Return the size of the median filter to apply in the spatial dimension to polcal data."""
        return self._find_most_recent_past_value("visp_polcal_spatial_median_filter_width_px")

    @property
    def polcal_num_spatial_bins(self) -> int:
        """
        Return the number of spatial bins to pass to `dkist-processing-pac`.

        This sets the spatial resolution of the resulting demodulation matrices.
        """
        return self._find_most_recent_past_value("visp_polcal_num_spatial_bins")

    @property
    def polcal_demod_spatial_smooth_fit_order(self) -> int:
        """Return the polynomial fit order used to fit/smooth demodulation matrices in the spatial dimension."""
        return self._find_most_recent_past_value("visp_polcal_demod_spatial_smooth_fit_order")

    @property
    def polcal_demod_spatial_smooth_min_samples(self) -> float:
        """Return fractional number of samples required for the RANSAC regressor used to smooth demod matrices."""
        return self._find_most_recent_past_value("visp_polcal_demod_spatial_smooth_min_samples")

    @property
    def polcal_demod_upsample_order(self) -> int:
        """Interpolation order to use when upsampling the demodulation matrices to the full frame.

        See `skimage.transform.warp` for details.
        """
        return self._find_most_recent_past_value("visp_polcal_demod_upsample_order")

    @property
    def pac_remove_linear_I_trend(self) -> bool:
        """Flag that determines if a linear intensity trend is removed from the whole PolCal CS.

        The trend is fit using the average flux in the starting and ending clear steps.
        """
        return self._find_most_recent_past_value("visp_pac_remove_linear_I_trend")

    @property
    def pac_fit_mode(self):
        """Name of set of fitting flags to use during PAC Calibration Unit parameter fits."""
        return self._find_most_recent_past_value("visp_pac_fit_mode")
