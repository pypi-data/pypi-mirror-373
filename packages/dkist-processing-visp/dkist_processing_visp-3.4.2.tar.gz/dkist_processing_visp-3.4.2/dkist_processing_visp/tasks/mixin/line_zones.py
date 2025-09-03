"""Helper functions for line zone determination."""

import numpy as np
import peakutils
import scipy.signal as sps
from dkist_service_configuration.logging import logger


class LineZonesMixin:
    """Helper functions for line zone determination."""

    def compute_line_zones(
        self,
        spec_2d: np.ndarray,
        prominence: float = 0.2,
        width: float = 2,
        bg_order: int = 22,
        normalization_percentile: int = 99,
        rel_height=0.97,
    ) -> list[tuple[int, int]]:
        """
        Identify spectral regions around strong spectra features.

        Parameters
        ----------
        spec_2d : np.ndarray
            Data

        prominence : float
            Zone prominence threshold used to identify strong spectral features

        width : float
            Zone width

        bg_order : int
            Order of polynomial fit used to remove continuum when identifying strong spectral features

        normalization_percentile : int
            Compute this percentile of the data along a specified axis



        Returns
        -------
        List
            List of regions to remove

        """
        logger.info(
            f"Finding zones using {prominence=}, {width=}, {bg_order=}, {normalization_percentile=}, and {rel_height=}"
        )
        # Compute average along slit to improve signal. Line smearing isn't important here
        avg_1d = np.mean(spec_2d, axis=1)

        # Convert to an emission spectrum and remove baseline continuum so peakutils has an easier time
        em_spec = -1 * avg_1d + avg_1d.max()
        em_spec /= np.nanpercentile(em_spec, normalization_percentile)
        baseline = peakutils.baseline(em_spec, bg_order)
        em_spec -= baseline

        # Find indices of peaks
        peak_idxs = sps.find_peaks(em_spec, prominence=prominence, width=width)[0]

        # Find the rough width based only on the height of the peak
        #  rips and lips are the right and left borders of the region around the peak
        _, _, rips, lips = sps.peak_widths(em_spec, peak_idxs, rel_height=rel_height)

        # Convert to ints so they can be used as indices
        rips = np.floor(rips).astype(int)
        lips = np.ceil(lips).astype(int)

        # Remove any regions that are contained within another region
        ranges_to_remove = self.identify_overlapping_zones(rips, lips)
        rips = np.delete(rips, ranges_to_remove)
        lips = np.delete(lips, ranges_to_remove)

        return list(zip(rips, lips))

    @staticmethod
    def identify_overlapping_zones(rips: np.ndarray, lips: np.ndarray) -> list[int]:
        """
        Identify line zones that overlap with other zones. Any overlap greater than 1 pixel is flagged.

        Parameters
        ----------
        rips : np.ndarray
            Right borders of the region around the peak

        lips : np.ndarray
            Left borders of the region around the peak

        Returns
        -------
        List
            List of ranges to be removed
        """
        all_ranges = [np.arange(zmin, zmax) for zmin, zmax in zip(rips, lips)]
        ranges_to_remove = []
        for i in range(len(all_ranges)):
            target_range = all_ranges[i]
            for j in range(i + 1, len(all_ranges)):
                if (
                    np.intersect1d(target_range, all_ranges[j]).size > 1
                ):  # Allow for a single overlap just to be nice
                    if target_range.size > all_ranges[j].size:
                        ranges_to_remove.append(j)
                        logger.info(
                            f"Zone ({all_ranges[j][0]}, {all_ranges[j][-1]}) inside zone ({target_range[0]}, {target_range[-1]})"
                        )
                    else:
                        ranges_to_remove.append(i)
                        logger.info(
                            f"Zone ({target_range[0]}, {target_range[-1]}) inside zone ({all_ranges[j][0]}, {all_ranges[j][-1]})"
                        )

        return ranges_to_remove
