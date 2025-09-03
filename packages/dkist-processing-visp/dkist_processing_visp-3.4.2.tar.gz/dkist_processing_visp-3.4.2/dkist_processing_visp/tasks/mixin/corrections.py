"""Helper for ViSP array corrections."""

from typing import Generator
from typing import Iterable

import numpy as np
import scipy.ndimage as spnd
from dkist_processing_math.transform import affine_transform_arrays
from dkist_processing_math.transform import rotate_arrays_about_point


class CorrectionsMixin:
    """Mixin to provide support for various array corrections used by the workflow tasks."""

    @staticmethod
    def corrections_correct_geometry(
        arrays: Iterable[np.ndarray] | np.ndarray,
        shift: np.ndarray = np.zeros(2),
        angle: float = 0.0,
    ) -> Generator[np.ndarray, None, None]:
        """
        Shift and then rotate data.

        This method applies the inverse of the given shift and angle.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-shifted beam

        shift : np.ndarray
            The shift in the spectral dimension needed to "straighten" the spectra
            so a single wavelength is at the same pixel for all slit positions.

        angle : float
            The angle (in radians) between slit hairlines and pixel axes.

        Returns
        -------
        Generator
            2D array(s) containing the data of the rotated and shifted beam
        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            array = array.astype(np.float64)
            array[np.where(array == np.inf)] = np.max(array[np.isfinite(array)])
            array[np.where(array == -np.inf)] = np.min(array[np.isfinite(array)])
            array[np.isnan(array)] = np.nanmedian(array)
            translated = affine_transform_arrays(array, translation=-shift, mode="reflect", order=5)
            yield next(rotate_arrays_about_point(translated, angle=-angle, mode="reflect", order=5))

    @staticmethod
    def corrections_remove_spec_geometry(
        arrays: Iterable[np.ndarray] | np.ndarray, spec_shift: np.ndarray
    ) -> Generator[np.ndarray, None, None]:
        """
        Remove spectral curvature.

        This is a pretty simple function that simply undoes the computed spectral shifts.

        Parameters
        ----------
        arrays
            2D array(s) containing the data for the un-distorted beam

        spec_shift : np.ndarray
            Array with shape (X), where X is the number of pixels in the spatial dimension.
            This dimension gives the spectral shift.

        Returns
        -------
        Generator
            2D array(s) containing the data of the corrected beam

        """
        arrays = [arrays] if isinstance(arrays, np.ndarray) else arrays
        for array in arrays:
            numy = array.shape[1]
            array_output = np.zeros(array.shape)
            for j in range(numy):
                array_output[:, j] = spnd.shift(
                    array[:, j], -spec_shift[j], mode="constant", cval=np.nanmedian(array[:, j])
                )
            yield array_output

    def corrections_mask_hairlines(self, array: np.ndarray) -> np.ndarray:
        """
        Mask hairlines from an array.

        The hairlines will be replaced with data from a median-filtered version of the input array.

        Hairlines are identified by first subtracting a spatially smoothed copy of the array and then looking for pixels
        that have large differences. This works because the hairlines are the only features that are sharp in the
        spatial dimension. The identified hairlines are then slightly smoothed spatially to ensure that their
        higher-flux wings are correctly masked.
        """
        filtered_array = self._median_filter_array_for_hairline_identification(array)
        hairline_locations = self._find_hairline_pixels(
            input_array=array, filtered_array=filtered_array
        )

        # Replace hairline pixels with data from the spatially-filtered array
        array[hairline_locations] = filtered_array[hairline_locations]

        return array

    def _median_filter_array_for_hairline_identification(self, array: np.ndarray) -> np.ndarray:
        """
        Small helper to separate out the median filter step of hairline identification.

        This step has been factored out so that functions that need the filtered array for further processing can avoid
        repeating this expensive computation.
        """
        # The size=(1, X) means we only smooth in the spatial dimension (1st axis)
        filtered_array = spnd.median_filter(
            array, size=(1, self.parameters.hairline_median_spatial_smoothing_width_px)
        )
        return filtered_array

    def _find_hairline_pixels(
        self, input_array: np.ndarray, filtered_array: np.ndarray
    ) -> np.ndarray:
        """
        Find pixels that likely correspond to hairlines.

        This also slightly smooths the identified pixels so that high-flux wings of the hairlines are included.
        """
        diff = (input_array - filtered_array) / filtered_array
        hairline_locations = np.abs(diff) > self.parameters.hairline_fraction

        # Now smooth the hairline mask in the spatial dimension to capture the higher-flux wings
        mask_array = np.zeros_like(input_array)
        mask_array[hairline_locations] = 1.0
        mask_array = spnd.gaussian_filter1d(
            mask_array, self.parameters.hairline_mask_spatial_smoothing_width_px, axis=1
        )

        hairline_locations = np.where(
            mask_array
            > mask_array.max() * self.parameters.hairline_mask_gaussian_peak_cutoff_fraction
        )

        return hairline_locations
