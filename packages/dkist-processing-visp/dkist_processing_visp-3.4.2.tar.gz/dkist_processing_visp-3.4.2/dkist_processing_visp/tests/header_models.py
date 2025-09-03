"""
Dataset subclasses for generating data for ViSP unit tests

All of these datasets are designed to produce a *complete* set of frames for the given task/situation. For example, if
you set num_modstates = 8 then the dataset generator will produce 8 frames, each with the correct modstate header
values.

This is very nice, but it's important to understand that the kwargs matter beyond just setting header values; they
actually control the output of the generators themselves.
"""

import uuid
from random import choice
from random import random
from random import randrange
from typing import Literal

import numpy as np
from astropy.wcs import WCS
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common.models.task_name import TaskName


class VispHeaders(Spec122Dataset):
    def __init__(
        self,
        dataset_shape: tuple[int, ...],
        array_shape: tuple[int, ...],
        time_delta: float = 10.0,
        num_modstates_header_value: int = 2,
        instrument: str = "visp",
        polarimeter_mode: str = "observe_polarimetric",
        **kwargs,
    ):
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=time_delta,
            instrument=instrument,
            **kwargs,
        )
        self.add_constant_key("WAVELNTH", 656.30)
        self.add_constant_key("VISP_010", num_modstates_header_value)
        self.add_constant_key("ID___013", "TEST_PROPOSAL_ID")
        self.add_constant_key("VISP_006", polarimeter_mode)
        self.add_constant_key("PAC__005", "0")
        self.add_constant_key("PAC__007", "10")
        self.add_constant_key("FILE_ID", uuid.uuid4().hex)
        self.num_modstates_header_value = num_modstates_header_value

    @key_function("VISP_011")
    def current_modstate(self, key: str):
        return randrange(1, self.num_modstates_header_value + 1)

    @property
    def fits_wcs(self):
        w = WCS(naxis=self.array_ndim)
        w.wcs.crpix = self.array_shape[2] / 2, self.array_shape[1] / 2, 1
        w.wcs.crval = 0, 656.30, 0
        w.wcs.cdelt = 1, 0.2, 1
        w.wcs.cunit = "arcsec", "nm", "arcsec"
        w.wcs.ctype = "HPLT-TAN", "AWAV", "HPLN-TAN"
        w.wcs.pc = np.identity(self.array_ndim)
        return w


class VispHeadersInputDarkFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        exp_time: float = 1.0,
        readout_exp_time: float = 2.0,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        num_frames = num_modstates
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            num_modstates_header_value=num_modstates,
            **kwargs,
        )
        self.add_constant_key("DKIST004", TaskName.dark.value.lower())
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:44:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:45:00")
        self.add_constant_key("VISP_019", 1)  # Num raster steps
        self.add_constant_key("VISP_020", 1)  # Current raster step
        self.add_constant_key("ID___004")
        self.add_constant_key(
            "WAVELNTH", 0.0
        )  # Intentionally bad to make sure it doesn't get parsed
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)  # Num frames per FPA

    @key_function("VISP_011")
    def current_modstate(self, key: str) -> int:
        return self.index + 1


class VispHeadersInputLampGainFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        exp_time: float = 10.0,
        readout_exp_time: float = 20.0,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        num_frames = num_modstates
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            num_modstates_header_value=num_modstates,
            **kwargs,
        )
        self.add_constant_key("DKIST004", TaskName.gain.value.lower())
        self.add_constant_key("PAC__002", "lamp")
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:46:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:47:00")
        self.add_constant_key("VISP_019", 1)
        self.add_constant_key("VISP_020", 1)
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("ID___004")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)

    @key_function("VISP_011")
    def current_modstate(self, key: str) -> int:
        return self.index + 1


class VispHeadersInputSolarGainFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        exp_time: float = 20.0,
        readout_exp_time: float = 40.0,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        num_frames = num_modstates
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            num_modstates_header_value=num_modstates,
            **kwargs,
        )
        self.add_constant_key("DKIST004", TaskName.gain.value.lower())
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:48:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:49:00")
        self.add_constant_key("VISP_019", 1)
        self.add_constant_key("VISP_020", 1)
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)

    @key_function("VISP_011")
    def current_modstate(self, key: str) -> int:
        return self.index + 1


class VispHeadersInputPolcalFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        num_cs_steps: int = 1,
        exp_time: float = 0.01,
        readout_exp_time: float = 0.02,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        num_frames = num_modstates * num_cs_steps
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(
            dataset_shape,
            array_shape,
            time_delta,
            num_modstates_header_value=num_modstates,
            **kwargs,
        )
        self.index_to_modstate = list(range(1, num_modstates + 1)) * num_cs_steps
        self.index_to_cs_step = sum([[c] * num_modstates for c in range(num_cs_steps)], [])
        self.polarizer_choices = ["Sapphire Polarizer", "clear"]
        self.retarder_choices = ["SiO2 OC", "clear"]

        self.add_constant_key("DKIST004", TaskName.polcal.value.lower())
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:50:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:51:00")
        self.add_constant_key("VISP_019", 1)
        self.add_constant_key("VISP_020", 1)
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("PAC__004", "Sapphire Polarizer")
        self.add_constant_key("PAC__005", "60.")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "FieldStop (5arcmin)")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)

    @key_function("PAC__006")
    def retarder_name(self, key: str) -> str:
        if self.index % 2:
            return self.retarder_choices[1]
        return self.retarder_choices[0]

    @property
    def current_cs_step(self) -> int:
        # There is no header value for CS step; this property is used to help data generator fixtures with tagging
        return self.index_to_cs_step[self.index]

    @key_function("VISP_011")
    def current_modstate(self, key: str) -> int:
        return self.index_to_modstate[self.index]

    @key_function("PAC__004")
    def polarizer(self, key: str) -> str:
        return choice(self.polarizer_choices)

    @key_function("PAC__005")
    def pol_angle(self, key: str) -> float:
        return random() * 120.0

    @key_function("PAC__007")
    def ret_angle(self, key: str) -> float:
        return random() * 120.0


class VispHeadersInputPolcalDarkFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        exp_time: float = 0.01,
        readout_exp_time: float = 0.02,
        **kwargs,
    ):
        num_frames = num_modstates
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        self.add_constant_key("DKIST004", TaskName.polcal.value.lower())
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:50:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:51:00")
        self.add_constant_key("VISP_019", 1)
        self.add_constant_key("VISP_020", 1)
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("PAC__004", "clear")
        self.add_constant_key("PAC__005", "60.")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "DarkShutter")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)


class VispHeadersInputPolcalGainFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_modstates: int,
        exp_time: float = 0.01,
        readout_exp_time: float = 0.02,
        **kwargs,
    ):
        num_frames = num_modstates
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)
        self.add_constant_key("DKIST004", TaskName.polcal.value.lower())
        self.add_constant_key("DKIST008", 1)
        self.add_constant_key("DKIST009", 1)
        self.add_constant_key("DKIST011", "2022-11-28T13:50:00")
        self.add_constant_key("DKIST012", "2022-11-28T13:51:00")
        self.add_constant_key("VISP_019", 1)
        self.add_constant_key("VISP_020", 1)
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("ID___004")
        self.add_constant_key("PAC__004", "clear")
        self.add_constant_key("PAC__005", "60.")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "0.0")
        self.add_constant_key("PAC__008", "FieldStop (5arcmin)")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)


class VispHeadersValidObserveFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_maps: int,
        num_raster_steps: int,
        num_modstates: int,
        exp_time: float = 15.0,
        readout_exp_time: float = 30.0,
        abort_last_step: bool = False,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        num_frames = num_maps * num_raster_steps * num_modstates

        if abort_last_step:
            # Because we drop one raster step, which consists of num_modstates frames
            num_dropped_frames = num_modstates * 1
            num_frames -= num_dropped_frames

        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(dataset_shape, array_shape, time_delta, **kwargs)

        self.index_to_map = sum(
            [[map_num + 1] * num_modstates * num_raster_steps for map_num in range(num_maps)], []
        )
        self.index_to_step = (
            sum([[step_num] * num_modstates for step_num in range(num_raster_steps)], []) * num_maps
        )
        self.index_to_modstate = (
            sum([list(range(1, num_modstates + 1)) for _ in range(num_raster_steps)], []) * num_maps
        )

        if abort_last_step:
            self.index_to_step = self.index_to_step[:-num_dropped_frames]
            self.index_to_modstate = self.index_to_modstate[:-num_dropped_frames]

        self._num_raster_steps = num_raster_steps
        self._num_modstates = num_modstates

        self.num_raster_steps = num_raster_steps
        self.add_constant_key("DKIST004", TaskName.observe.value.lower())
        self.add_constant_key("DKIST011", "2022-11-28T13:55:00")  # IP start time
        self.add_constant_key("DKIST012", "2022-11-28T13:56:00")  # IP end time
        self.add_constant_key("ID___004")
        self.add_constant_key("WAVELNTH", 656.28)
        self.add_constant_key("EXPER_ID", "EXPERIMENT ID")
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)  # Num frames in FPA

    @property
    def current_map(self) -> int:
        # There is no header value for map num; this property is used to help data generator fixtures with tagging
        return self.index_to_map[self.index]

    @key_function("VISP_010")
    def num_modstates(self, key: str) -> int:
        # Needed because constant_keys take precedent over key_functions and we need to be able to change this value
        # in a subclass
        return self._num_modstates

    @key_function("VISP_011")
    def current_modstate(self, key: str) -> int:
        return self.index_to_modstate[self.index]

    @key_function("VISP_019")
    def num_raster_steps(self, key: str) -> int:
        # Needed because constant_keys take precedent over key_functions and we need to be able to change this value
        # in a subclass
        return self._num_raster_steps

    @key_function("VISP_020")
    def current_raster_step(self, key: str) -> int:
        return self.index_to_step[self.index]


class VispHeadersValidCalibratedFrames(VispHeaders):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        time_delta: float,
        num_maps: int,
        num_raster_steps: int,
        polarimeter_mode: Literal[
            "observe_polarimetric", "observe_intensity"
        ] = "observe_polarimetric",
        exp_time: float = 15.0,
        readout_exp_time: float = 30.0,
        wcs_axis_names: tuple[str, str] | None = None,
        **kwargs,
    ):
        ################################################
        # See module docstring and README for usage info
        ################################################
        if polarimeter_mode == "observe_polarimetric":
            num_stokes = 4
        else:
            num_stokes = 1

        num_frames = num_maps * num_raster_steps * num_stokes
        dataset_shape = (num_frames, *array_shape[-2:])
        super().__init__(
            dataset_shape, array_shape, time_delta, polarimeter_mode=polarimeter_mode, **kwargs
        )

        stokes_list = ["I", "Q", "U", "V"][:num_stokes]
        self.index_to_map = sum(
            [[map_num + 1] * num_stokes * num_raster_steps for map_num in range(num_maps)], []
        )
        self.index_to_step = (
            sum([[step_num] * num_stokes for step_num in range(num_raster_steps)], []) * num_maps
        )
        self.index_to_stokes = sum([stokes_list for _ in range(num_raster_steps)], []) * num_maps

        self.num_raster_steps = num_raster_steps
        self.add_constant_key("DKIST004", TaskName.observe.value.lower())
        self.add_constant_key("DKIST011", "2022-11-28T13:55:00")  # IP start time
        self.add_constant_key("DKIST012", "2022-11-28T13:56:00")  # IP end time
        self.add_constant_key("ID___004")
        self.add_constant_key("WAVELNTH", 656.28)
        self.add_constant_key("EXPER_ID", "EXPERIMENT ID")
        self.add_constant_key("VISP_019", num_raster_steps)
        self.add_constant_key("CAM__004", exp_time)
        self.add_constant_key("CAM__005", readout_exp_time)
        self.add_constant_key("CAM__014", 10)  # Num frames in FPA

        if wcs_axis_names:
            self.add_constant_key("CTYPE1", wcs_axis_names[0])
            self.add_constant_key("CTYPE2", wcs_axis_names[1])

        # These keys are added by the Science task
        self.add_constant_key("VSPNMAPS", num_maps)
        self.add_constant_key("DATE-END", "2022-11-28T14:00:00")
        if polarimeter_mode == "observe_polarimetric":
            self.add_constant_key("POL_NOIS", 0.4)
            self.add_constant_key("POL_SENS", 1.4)

    @property
    def current_map(self) -> int:
        # This property is used to help data generator fixtures with tagging
        return self.index_to_map[self.index]

    @key_function("VSPMAP")
    def map_key(self, key: str) -> int:
        return self.current_map

    @property
    def current_stokes(self) -> str:
        # There is no header value for Stokes value; this property is used to help data generator fixtures with tagging
        return self.index_to_stokes[self.index]

    @key_function("VISP_020")
    def current_raster_step(self, key: str) -> int:
        return self.index_to_step[self.index]
