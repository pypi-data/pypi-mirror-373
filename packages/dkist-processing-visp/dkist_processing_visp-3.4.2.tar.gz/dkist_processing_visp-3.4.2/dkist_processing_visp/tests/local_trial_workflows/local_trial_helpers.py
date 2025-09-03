import os
import shutil
from datetime import datetime
from pathlib import Path

import asdf
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.parsers.cs_step import CSStepFlower
from dkist_processing_common.parsers.cs_step import NumCSStepBud
from dkist_processing_common.parsers.retarder import RetarderNameBud
from dkist_processing_common.parsers.task import PolcalTaskFlower
from dkist_processing_common.parsers.task import TaskTypeFlower
from dkist_processing_common.parsers.task import parse_header_ip_task_with_gains
from dkist_processing_common.parsers.time import ExposureTimeFlower
from dkist_processing_common.parsers.time import ReadoutExpTimeFlower
from dkist_processing_common.parsers.time import TaskExposureTimesBud
from dkist_processing_common.parsers.time import TaskReadoutExpTimesBud
from dkist_processing_common.tasks import ParseL0InputDataBase
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_processing_common.tasks.trial_output_data import TransferTrialData
from dkist_processing_math.statistics import average_numpy_arrays
from loguru import logger

from dkist_processing_visp.models.constants import VispBudName
from dkist_processing_visp.models.constants import VispConstants
from dkist_processing_visp.models.parameters import VispParsingParameters
from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.models.task_name import VispTaskName
from dkist_processing_visp.parsers.modulator_states import ModulatorStateFlower
from dkist_processing_visp.parsers.time import DarkReadoutExpTimePickyBud
from dkist_processing_visp.parsers.time import NonDarkNonPolcalTaskReadoutExpTimesBud
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.visp_base import VispTaskBase


class SaveInputParsing(WorkflowTaskBase):
    """Dump redis db to file"""

    @property
    def relative_save_file(self) -> str:
        return "input_parsing_cal.asdf"

    def run(self):
        file_tag_dict = self.get_input_tags()
        constant_dict = self.get_constants()

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict, "constants_dict": constant_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved input tags to {full_save_file}")

    def get_input_tags(self) -> dict[str, list[str]]:
        file_tag_dict = dict()
        path_list = self.read(tags=[VispTag.input()])
        for p in path_list:
            tags = self.tags(p)
            file_tag_dict[str(p)] = tags

        return file_tag_dict

    def get_constants(self) -> dict[str, str | float | list]:
        constants_dict = dict()
        for c in self.constants._db_dict.keys():
            constants_dict[c] = self.constants._db_dict[c]

        return constants_dict


class LoadInputParsing(WorkflowTaskBase):
    """Load redis db (tags and constants) from a file."""

    @property
    def relative_save_file(self) -> str:
        return "input_parsing_cal.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            file_tag_dict = af.tree["file_tag_dict"]
            self.tag_input_files(file_tag_dict)

            constants_dict = af.tree["constants_dict"]
            self.populate_constants(constants_dict)

        logger.info(f"Loaded input tags and constants from")

    def tag_input_files(self, file_tag_dict: dict[str, list[str]]):
        """Do."""
        for f, t in file_tag_dict.items():
            if not os.path.exists(f):
                raise FileNotFoundError(f"Expected to find {f}, but it doesn't exist.")
            self.tag(path=f, tags=t)

    def populate_constants(self, constants_dict: dict[str, str | int | float]) -> None:
        """Do."""
        for c, v in constants_dict.items():
            logger.info(f"Setting value of {c} to {v}")
            self.constants._update({c: v})


class SaveTaskTags(WorkflowTaskBase):
    @property
    def task_str(self) -> str:
        return "TASK"

    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]] | list[str]:
        return [[VispTag.task(self.task_str), VispTag.intermediate()]]

    def run(self):
        file_tag_dict = dict()

        tag_list_list = self.tag_lists_to_save
        if isinstance(tag_list_list[0], str):
            tag_list_list = [tag_list_list]

        for tags_to_save in tag_list_list:
            path_list = self.read(tags=tags_to_save)
            save_dir = self.scratch.workflow_base_path / Path(self.relative_save_file).stem
            save_dir.mkdir(exist_ok=True)
            for p in path_list:
                copied_path = shutil.copy(str(p), save_dir)
                tags = self.tags(p)
                file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved {self.task_str} to {full_save_file}")


class LoadTaskTags(WorkflowTaskBase):
    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            for f, t in af.tree["file_tag_dict"].items():
                self.tag(path=f, tags=t)
        logger.info(f"Loaded database entries from {full_save_file}")


class SaveGeometricCal(WorkflowTaskBase):
    def run(self) -> None:
        relative_save_file = "geometric_cal.asdf"
        file_tag_dict = dict()
        path_list = list(self.read(tags=[VispTag.task_geometric_angle(), VispTag.intermediate()]))
        path_list += list(self.read(tags=[VispTag.task_geometric_offset(), VispTag.intermediate()]))
        path_list += list(
            self.read(tags=[VispTag.task_geometric_spectral_shifts(), VispTag.intermediate()])
        )
        path_list += list(
            self.read(
                tags=[VispTag.quality("TASK_TYPES"), VispTag.workflow_task("GeometricCalibration")]
            )
        )
        save_dir = self.scratch.workflow_base_path / Path(relative_save_file).stem
        save_dir.mkdir(exist_ok=True)
        for p in path_list:
            copied_path = shutil.copy(str(p), save_dir)
            tags = self.tags(p)
            file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved Geometric Calibration to {full_save_file}")


class LoadGeometricCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "geometric_cal.asdf"


class SaveDarkCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.dark.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [VispTag.quality("TASK_TYPES"), VispTag.workflow_task("DarkCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class LoadDarkCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class SaveBackgroundCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return VispTaskName.background.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [VispTag.quality("TASK_TYPES"), VispTag.workflow_task("BackgroundLightCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "background_cal.asdf"


class LoadBackgroundCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "background_cal.asdf"


class SaveLampCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.lamp_gain.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [VispTag.quality("TASK_TYPES"), VispTag.workflow_task("LampCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class LoadLampCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class SaveSolarCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.solar_gain.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [VispTag.quality("TASK_TYPES"), VispTag.workflow_task("SolarCalibration")]
        ]

    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class LoadSolarCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class SaveInstPolCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.demodulation_matrices.value

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                VispTag.quality("TASK_TYPES"),
                VispTag.workflow_task("InstrumentPolarizationCalibration"),
            ],
            [VispTag.quality("POLCAL_CONSTANT_PAR_VALS")],
            [VispTag.quality("POLCAL_GLOBAL_PAR_VALS")],
            [VispTag.quality("POLCAL_LOCAL_PAR_VALS")],
            [VispTag.quality("POLCAL_FIT_RESIDUALS")],
            [VispTag.quality("POLCAL_EFFICIENCY")],
        ]

    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


class LoadInstPolCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


class SaveCalibratedData(SaveTaskTags):
    @property
    def tag_lists_to_save(self) -> list[str]:
        return [VispTag.frame(), VispTag.calibrated()]

    @property
    def relative_save_file(self) -> str:
        return "calibrated_science.asdf"


class LoadCalibratedData(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "calibrated_science.asdf"


def set_observe_wavelength_task(wavelength: float = 630.0):
    class SetObserveWavelength(WorkflowTaskBase):
        def run(self):
            self.constants._update({VispBudName.wavelength.value: wavelength})

    return SetObserveWavelength


class SetObserveIpStartTime(WorkflowTaskBase):
    def run(self):
        self.constants._update({VispBudName.obs_ip_start_time.value: datetime.now().isoformat()})


class SetObserveExpTime(VispTaskBase):
    def run(self):
        self.constants._update(
            {VispBudName.observe_exposure_times.value: self.constants.solar_exposure_times}
        )
        self.constants._update(
            {VispBudName.observe_readout_exp_times.value: self.constants.solar_readout_exp_times}
        )


class SetCadenceConstants(WorkflowTaskBase):
    def run(self):
        self.constants._update(
            {
                BudName.average_cadence.value: 1.0,
                BudName.minimum_cadence.value: 0.0,
                BudName.maximum_cadence.value: 3.0,
                BudName.variance_cadence.value: 1,
            }
        )


class SetAxesTypes(WorkflowTaskBase):
    def run(self):
        self.constants._update(
            {
                VispBudName.axis_1_type.value: "HPLT-TAN",
                VispBudName.axis_2_type.value: "AWAV",
                VispBudName.axis_3_type.value: "HPLN-TAN",
            }
        )


class SetPolarimeterMode(VispTaskBase):
    def run(self):
        self.constants._update({VispBudName.polarimeter_mode.value: "observe_polarimetric"})


class SetNumModstates(VispTaskBase):
    def run(self):
        self.constants._update({BudName.num_modstates.value: 10})


class ParseCalOnlyL0InputData(ParseL0InputDataBase):
    """
    Parse input ViSP data. Subclassed from the ParseL0InputDataBase task in dkist_processing_common to add ViSP specific parameters.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    def __init__(
        self,
        recipe_run_id: int,
        workflow_name: str,
        workflow_version: str,
    ):
        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )
        self.parameters = VispParsingParameters(scratch=self.scratch)

    @property
    def fits_parsing_class(self):
        """FITS access class to use in this task."""
        return VispL0FitsAccess

    @property
    def constant_buds(self):
        """Add ViSP specific constants to common constants."""
        return super().constant_buds + [
            NumCSStepBud(self.parameters.max_cs_step_time_sec),
            NonDarkNonPolcalTaskReadoutExpTimesBud(),
            DarkReadoutExpTimePickyBud(),
            RetarderNameBud(),
            TaskExposureTimesBud(
                stem_name=VispBudName.lamp_exposure_times.value,
                ip_task_types=TaskName.lamp_gain.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
            TaskExposureTimesBud(
                stem_name=VispBudName.solar_exposure_times.value,
                ip_task_types=TaskName.solar_gain.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
            TaskExposureTimesBud(
                stem_name=VispBudName.polcal_exposure_times.value,
                ip_task_types=TaskName.polcal.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
            TaskReadoutExpTimesBud(
                stem_name=VispBudName.lamp_readout_exp_times.value,
                ip_task_types=TaskName.lamp_gain.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
            TaskReadoutExpTimesBud(
                stem_name=VispBudName.solar_readout_exp_times.value,
                ip_task_types=TaskName.solar_gain.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
            TaskReadoutExpTimesBud(
                stem_name=VispBudName.polcal_readout_exp_times.value,
                ip_task_types=TaskName.polcal.value,
                header_task_parsing_func=parse_header_ip_task_with_gains,
            ),
        ]

    @property
    def tag_flowers(self):
        """Add ViSP specific tags to common tags."""
        return super().tag_flowers + [
            CSStepFlower(max_cs_step_time_sec=self.parameters.max_cs_step_time_sec),
            TaskTypeFlower(header_task_parsing_func=parse_header_ip_task_with_gains),
            PolcalTaskFlower(),
            ModulatorStateFlower(),
            ExposureTimeFlower(),
            ReadoutExpTimeFlower(),
        ]


class ValidateL1Output(VispTaskBase):
    def run(self) -> None:
        files = self.read(tags=[VispTag.output(), VispTag.frame()])
        for f in files:
            logger.info(f"Validating {f}")
            spec214_validator.validate(f, extra=False)


def transfer_trial_data_locally_task(
    trial_dir: str | Path,
):
    class LocalTrialData(TransferTrialData):
        @property
        def destination_folder(self) -> Path:
            return Path(trial_dir)

        def remove_folder_objects(self):
            logger.info("Would have removed folder objects here")

        def globus_transfer_scratch_to_object_store(
            self,
            transfer_items: list[GlobusTransferItem],
            label: str = None,
            sync_level: str = None,
            verify_checksum: bool = True,
        ) -> None:
            if label:
                logger.info(f"Transferring files with {label = }")

            for frame in transfer_items:
                if not frame.destination_path.parent.exists():
                    frame.destination_path.parent.mkdir(parents=True)
                os.system(f"cp {frame.source_path} {frame.destination_path}")

    return LocalTrialData


def translate_122_to_214l0_task(suffix: str):
    class Translate122To214L0(WorkflowTaskBase):
        def run(self) -> None:
            raw_dir = Path(self.scratch.scratch_base_path) / f"VISP{self.recipe_run_id:03n}"
            if not os.path.exists(self.scratch.workflow_base_path):
                os.makedirs(self.scratch.workflow_base_path)

            if not raw_dir.exists():
                raise FileNotFoundError(
                    f"Expected to find a raw VISP{{run_id:03n}} folder in {self.scratch.scratch_base_path}"
                )

            for file in raw_dir.glob(f"*{suffix}"):
                translated_file_name = Path(self.scratch.workflow_base_path) / os.path.basename(
                    file
                )
                logger.info(f"Translating {file} -> {translated_file_name}")
                hdl = fits.open(file)
                i = 0
                if hdl[i].data is None:
                    i = 1

                header = spec122_validator.validate_and_translate_to_214_l0(
                    hdl[i].header, return_type=fits.HDUList
                )[0].header

                comp_hdu = fits.CompImageHDU(header=header, data=hdl[i].data)
                comp_hdl = fits.HDUList([fits.PrimaryHDU(), comp_hdu])
                comp_hdl.writeto(translated_file_name, overwrite=True)

                hdl.close()
                del hdl
                comp_hdl.close()
                del comp_hdl

    return Translate122To214L0


def tag_inputs_task(suffix: str):
    class TagInputs(WorkflowTaskBase):
        def run(self) -> None:
            logger.info(f"Looking in {os.path.abspath(self.scratch.workflow_base_path)}")
            input_file_list = list(self.scratch.workflow_base_path.glob(f"*.{suffix}"))
            if len(input_file_list) == 0:
                raise FileNotFoundError(
                    f"Did not find any files matching '*.{suffix}' in {self.scratch.workflow_base_path}"
                )
            for file in input_file_list:
                logger.info(f"Found {file}")
                self.tag(path=file, tags=[VispTag.input(), VispTag.frame()])

    return TagInputs


class TagSingleSolarGainAsScience(VispTaskBase):
    """Do."""

    def run(self) -> None:
        """Do."""
        tags = [
            VispTag.input(),
            VispTag.frame(),
            VispTag.task_solar_gain(),
        ]
        file_list = list(self.read(tags=tags))
        first_hdul = fits.open(file_list[0])
        idx = 1 if first_hdul[0].data is None else 0
        first_header = first_hdul[idx].header
        logger.info(f"Averaging {len(file_list)} files")
        arrays = self.read(tags=tags, decoder=fits_array_decoder)
        avg_array = average_numpy_arrays(arrays=arrays)

        hdul = fits.HDUList([fits.PrimaryHDU(data=avg_array, header=first_header)])
        hdul[0].header["VSPSTP"] = 0
        hdul[0].header["VSPNSTP"] = 1
        hdul[0].header["VSPSTNUM"] = 1
        hdul[0].header["VSPPOLMD"] = "observe_intensity"
        # hdul[0].header["POL_NOIS"] = 0.666
        # hdul[0].header["POL_SENS"] = 0.666

        new_tags = [
            VispTag.task_observe(),
            VispTag.input(),
            VispTag.frame(),
            VispTag.map_scan(1),
            VispTag.raster_step(0),
            VispTag.modstate(1),
            VispTag.readout_exp_time(self.constants.solar_readout_exp_times[0]),
        ]
        file_name = self.write(data=hdul, tags=new_tags, encoder=fits_hdulist_encoder)
        final_tags = self.tags(self.scratch.workflow_base_path / file_name)
        logger.info(f"after re-tagging tags for {str(file_name) = } are {final_tags}")

        del self.constants._db_dict[VispBudName.polarimeter_mode.value]
        self.constants._update(
            {
                VispBudName.num_map_scans.value: 1,
                VispBudName.num_raster_steps.value: 1,
                VispBudName.polarimeter_mode.value: "observe_intensity",
            }
        )


class TagModulatedSolarGainsAsScience(VispTaskBase):
    """Do."""

    def run(self) -> None:
        """Do."""
        for modstate in range(1, self.constants.num_modstates + 1):
            tags = [
                VispTag.task_solar_gain(),
                VispTag.input(),
                VispTag.frame(),
                VispTag.modstate(modstate),
            ]
            file_list = list(self.read(tags=tags))
            first_hdul = fits.open(file_list[0])
            idx = 1 if first_hdul[0].data is None else 0
            first_header = first_hdul[idx].header
            logger.info(f"Averaging {len(file_list)} files")
            arrays = self.read(tags=tags, decoder=fits_array_decoder)
            avg_array = average_numpy_arrays(arrays=arrays)

            hdul = fits.HDUList([fits.PrimaryHDU(data=avg_array, header=first_header)])
            hdul[0].header["VSPSTP"] = 0
            hdul[0].header["VSPNSTP"] = 1
            hdul[0].header["VSPSTNUM"] = modstate
            hdul[0].header["VSPPOLMD"] = "observe_polarimetric"

            new_tags = [
                VispTag.task_observe(),
                VispTag.input(),
                VispTag.frame(),
                VispTag.map_scan(1),
                VispTag.raster_step(0),
                VispTag.modstate(modstate),
                VispTag.readout_exp_time(self.constants.solar_readout_exp_times[0]),
            ]
            file_name = self.write(data=hdul, tags=new_tags, encoder=fits_hdulist_encoder)
            final_tags = self.tags(self.scratch.workflow_base_path / file_name)
            logger.info(f"after re-tagging tags for {str(file_name) = } are {final_tags}")

        del self.constants._db_dict[VispBudName.polarimeter_mode.value]
        self.constants._update(
            {
                VispBudName.num_map_scans.value: 1,
                VispBudName.num_raster_steps.value: 1,
                VispBudName.polarimeter_mode.value: "observe_polarimetric",
            }
        )
        logger.info(f"{self.constants.correct_for_polarization = }")


class SaveSolarGainAsScience(SaveTaskTags):
    @property
    def tag_lists_to_save(self) -> list[str]:
        return [VispTag.task_observe(), VispTag.input(), VispTag.frame()]

    @property
    def relative_save_file(self) -> str:
        return "solar_gain_as_science.asdf"


def load_solar_gain_as_science_task(force_intensity_only: bool):
    class LoadSolarGainAsScience(LoadTaskTags):
        constants: VispConstants

        @property
        def constants_model_class(self):
            """Get ViSP pipeline constants."""
            return VispConstants

        @property
        def relative_save_file(self) -> str:
            return "solar_gain_as_science.asdf"

        def run(self):
            super().run()
            del self.constants._db_dict[VispBudName.polarimeter_mode.value]
            self.constants._update(
                {
                    VispBudName.num_map_scans.value: 1,
                    VispBudName.num_raster_steps.value: 1,
                    VispBudName.polarimeter_mode.value: "observe_intensity" if force_intensity_only else "observe_polarimetric",  # fmt: skip
                }
            )
            logger.info(f"{self.constants.correct_for_polarization = }")

    return LoadSolarGainAsScience
