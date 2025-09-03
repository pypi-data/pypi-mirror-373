"""Visp make movie frames task."""

import numpy as np
from astropy.io import fits
from astropy.visualization import ZScaleInterval
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l1_fits_access import VispL1FitsAccess
from dkist_processing_visp.tasks.visp_base import VispTaskBase

__all__ = ["MakeVispMovieFrames"]


class MakeVispMovieFrames(VispTaskBase):
    """
    Make ViSP movie frames and tag with VispTag.movie_frame().

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs


    """

    def run(self):
        """
        For each stokes state.

            For each map scan:
              - Integrate each step in the scan over wavelength into a single column of pixels
              - Build a movie frame by lining the columns up side by side
              - Write full wavelength integrated frame as a "MOVIE_FRAME"

        Returns
        -------
        None
        """
        is_polarized = False
        stokes_states = ["I", "Q", "U", "V"]
        # Loop over the number of raster scans
        for map_scan in range(1, self.constants.num_map_scans + 1):
            with self.apm_processing_step(f"Making movie frame for {map_scan = }"):
                instrument_set = set()
                wavelength_set = set()
                time_obs = []
                # Loop over the stokes states to add them to the frame array
                for stokes_state in stokes_states:
                    stokes_paths = list(
                        self.read(
                            tags=[
                                VispTag.frame(),
                                VispTag.calibrated(),
                                VispTag.stokes(stokes_state),
                            ]
                        )
                    )
                    if len(stokes_paths) > 0:
                        # Loop over the raster steps in a single scan
                        for raster_step in range(0, self.constants.num_raster_steps):
                            calibrated_frame: VispL1FitsAccess = next(
                                self.read(
                                    tags=[
                                        VispTag.frame(),
                                        VispTag.calibrated(),
                                        VispTag.stokes(stokes_state),
                                        VispTag.map_scan(map_scan),
                                        VispTag.raster_step(raster_step),
                                    ],
                                    decoder=fits_access_decoder,
                                    fits_access_class=VispL1FitsAccess,
                                )
                            )
                            data = calibrated_frame.data
                            if self.constants.num_raster_steps == 1:
                                logger.info(
                                    "Only a single raster step found. Making a spectral movie."
                                )
                                stokes_frame_data = data
                            else:
                                wavelength_integrated_data = np.sum(np.abs(data), axis=0)
                                if raster_step == 0:
                                    stokes_frame_data = wavelength_integrated_data[:, None]
                                else:
                                    stokes_frame_data = np.concatenate(
                                        (stokes_frame_data, wavelength_integrated_data[:, None]),
                                        axis=1,
                                    )
                            # Grab the relevant header info from the frame
                            instrument_set.add(calibrated_frame.instrument)
                            wavelength_set.add(calibrated_frame.wavelength)
                            time_obs.append(calibrated_frame.time_obs)

                        # Encode the data as a specific stokes state
                        if stokes_state == "I":
                            stokes_i_data = stokes_frame_data
                        if stokes_state == "Q":
                            is_polarized = True
                            stokes_q_data = stokes_frame_data
                        if stokes_state == "U":
                            is_polarized = True
                            stokes_u_data = stokes_frame_data
                        if stokes_state == "V":
                            is_polarized = True
                            stokes_v_data = stokes_frame_data

                # Use the most recently read header as the base header because we need to be able to read it
                # with VispL1FitsAccess. We'll update the values we actually care about below.
                header = fits.Header(calibrated_frame.header)

                # Make sure only one instrument value was found
                if len(instrument_set) != 1:
                    raise ValueError(
                        f"There should only be one instrument value in the headers. "
                        f"Found {len(instrument_set)}: {instrument_set=}"
                    )
                header["INSTRUME"] = instrument_set.pop()
                # The timestamp of a movie frame will be the time of raster scan start
                header["DATE-BEG"] = time_obs[0]
                # Make sure only one wavelength value was found
                if len(wavelength_set) != 1:
                    raise ValueError(
                        f"There should only be one wavelength value in the headers. "
                        f"Found {len(wavelength_set)}: {wavelength_set=}"
                    )
                header["LINEWAV"] = wavelength_set.pop()
                # Write the movie frame file to disk and tag it, normalizing across stokes intensities
                if is_polarized:
                    i_norm = ZScaleInterval()(stokes_i_data)
                    q_norm = ZScaleInterval()(stokes_q_data)
                    u_norm = ZScaleInterval()(stokes_u_data)
                    v_norm = ZScaleInterval()(stokes_v_data)
                    movie_frame_data = np.concatenate(
                        (
                            np.concatenate((i_norm, q_norm), axis=1),
                            np.concatenate((u_norm, v_norm), axis=1),
                        ),
                        axis=0,
                    )
                else:
                    movie_frame_data = stokes_i_data

            with self.apm_writing_step(f"Writing movie frame for {map_scan = }"):
                self.write(
                    data=np.asarray(movie_frame_data),
                    tags=[
                        VispTag.map_scan(map_scan),
                        VispTag.movie_frame(),
                    ],
                    encoder=fits_array_encoder,
                    header=header,
                )
