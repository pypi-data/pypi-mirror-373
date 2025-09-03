"""Helper to manage extract a given beam from input data."""

import numpy as np


class BeamAccessMixin:
    """
    Mixin for extracting a single beam from a raw, dual-beam array.

    This is exclusively used for input frames; all intermediate frames are saved on a per-beam basis.
    """

    def beam_access_get_beam(self, array: np.ndarray, beam: int) -> np.ndarray:
        """
        Extract a single beam array from a dual-beam array.

        Parameters
        ----------
        array
            The input dual-beam array

        beam
            The desired beam to extract

        Returns
        -------
        An ndarray containing the extracted beam
        """
        if beam == 1:
            return np.copy(array[: self.parameters.beam_border, ...])
        else:
            return np.copy(array[self.parameters.beam_border :, ...][::-1, :])
