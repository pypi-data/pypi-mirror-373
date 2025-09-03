"""Helper mixin for downsampling data."""

import numpy as np


class DownsampleMixin:
    """Mixin for downsampling data (i.e., reduce dimension lengths through some sort of binning)."""

    @staticmethod
    def downsample_spatial_dimension_local_median(
        data: np.ndarray, num_spatial_bins: int
    ) -> np.ndarray:
        """Resample a stack of spectra along the spatial dimension.

        This is a separate function because calling `skimage.measure.block_reduce` on the entire (large) array all at once
        creates a huge memory strain that is not needed since we're only reducing over one of the dimensions. Instead,
        this function does some very cool tricks with reshaping and base numpy to keep the memory footprint lower.
        """
        # Taken from the amazing answer in
        #  https://stackoverflow.com/questions/44527579/whats-the-best-way-to-downsample-a-numpy-array
        num_wave, num_spat_pos = data.shape

        if (num_spat_pos / num_spatial_bins) % 1 != 0:
            raise ValueError(
                f"The number of spatial bins must evenly divide the spatial dimension. {num_spatial_bins} bins do not evenly divide {num_spat_pos}."
            )

        reshaped = data.reshape((num_wave, num_spatial_bins, num_spat_pos // num_spatial_bins))
        return np.median(reshaped, axis=2)
