import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from random import randint

from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.parsers.visp_l0_fits_access import VispL0FitsAccess
from dkist_processing_visp.tasks.assemble_movie import AssembleVispMovie
from dkist_processing_visp.tasks.background_light import BackgroundLightCalibration
from dkist_processing_visp.tasks.dark import DarkCalibration
from dkist_processing_visp.tasks.geometric import GeometricCalibration
from dkist_processing_visp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_visp.tasks.l1_output_data import VispAssembleQualityData
from dkist_processing_visp.tasks.lamp import LampCalibration
from dkist_processing_visp.tasks.make_movie_frames import MakeVispMovieFrames
from dkist_processing_visp.tasks.parse import ParseL0VispInputData
from dkist_processing_visp.tasks.quality_metrics import VispL0QualityMetrics
from dkist_processing_visp.tasks.quality_metrics import VispL1QualityMetrics
from dkist_processing_visp.tasks.science import ScienceCalibration
from dkist_processing_visp.tasks.solar import SolarCalibration
from dkist_processing_visp.tasks.visp_base import VispTaskBase
from dkist_processing_visp.tasks.write_l1 import VispWriteL1Frame
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import tag_inputs_task
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    transfer_trial_data_locally_task,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    translate_122_to_214l0_task,
)

INV = False
try:
    from dkist_inventory.asdf_generator import dataset_from_fits

    INV = True
except ModuleNotFoundError:
    logger.warning(
        "Could not load dkist-inventory. CreateTrialDatasetInventory and CreateTrialAsdf require dkist-inventory."
    )

QUALITY = False
try:
    import dkist_quality

    QUALITY = True
except ModuleNotFoundError:
    logger.warning("Could not load dkist-quality. CreateTrialQualityReport requires dkist-quality.")

if QUALITY:
    import matplotlib.pyplot as plt

    plt.ioff()


class CreateInputDatasetParameterDocument(WorkflowTaskBase):
    def run(self) -> None:
        relative_path = "input_dataset_parameters.json"
        self.write(
            data=InputDatasetPartDocumentList(
                doc_list=self.input_dataset_document_simple_parameters_part
            ),
            relative_path=relative_path,
            tags=VispTag.input_dataset_parameters(),
            encoder=basemodel_encoder,
        )
        logger.info(f"Wrote input dataset parameter doc to {relative_path}")

    @property
    def input_dataset_document_simple_parameters_part(self):
        parameters_list = []
        value_id = randint(1000, 2000)
        for pn, pv in asdict(VispInputDatasetParameterValues()).items():
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)

        return parameters_list


class ShowPolMode(VispTaskBase):
    def run(self) -> None:
        logger.info(f"{self.constants.correct_for_polarization = }")


class ShowExposureTimes(VispTaskBase):
    def run(self) -> None:
        logger.info(f"{self.constants.dark_exposure_times = }")
        logger.info(f"{self.constants.dark_readout_exp_times = }")
        logger.info(f"{self.constants.lamp_exposure_times = }")
        logger.info(f"{self.constants.lamp_readout_exp_times = }")
        logger.info(f"{self.constants.solar_exposure_times = }")
        logger.info(f"{self.constants.solar_readout_exp_times = }")
        if self.constants.correct_for_polarization:
            logger.info(f"{self.constants.polcal_exposure_times = }")
            logger.info(f"{self.constants.polcal_readout_exp_times = }")
        logger.info(f"{self.constants.observe_exposure_times = }")
        logger.info(f"{self.constants.observe_readout_exp_times = }")


class ShowMapMapping(VispTaskBase):
    def run(self) -> None:
        logger.info(f"Found {self.constants.num_map_scans} map scans")
        step = 0
        logger.info(f"Step {step} is organized thusly:")
        for map in range(1, self.constants.num_map_scans + 1):
            logger.info(f"Map #{map}:")
            for mod in range(1, self.constants.num_modstates + 1):
                fits_obj = list(
                    self.read(
                        tags=[
                            VispTag.input(),
                            VispTag.frame(),
                            VispTag.map_scan(map),
                            VispTag.modstate(mod),
                            VispTag.raster_step(step),
                        ],
                        decoder=fits_access_decoder,
                        fits_access_class=VispL0FitsAccess,
                    )
                )
                logger.info(
                    f"\tModstate {mod} has {len(fits_obj)} files. Date is {fits_obj[0].time_obs}"
                )


class ValidateL1Output(VispTaskBase):
    def run(self) -> None:
        files = self.read(tags=[VispTag.output(), VispTag.frame()])
        for f in files:
            logger.info(f"Validating {f}")
            spec214_validator.validate(f, extra=False)


def setup_APM_config() -> None:
    mesh_config = {
        "system-monitoring-log-apm": {
            "mesh_address": "system-monitoring-log-apm.service.sim.consul",
            "mesh_port": 8200,
        },
        "automated-processing-scratch-inventory": {"mesh_address": "localhost", "mesh_port": 6379},
        "internal-api-gateway": {"mesh_address": "localhost", "mesh_port": 80},
    }
    apm_options = {"TRANSACTION_MAX_SPANS": 10000}
    os.environ["MESH_CONFIG"] = json.dumps(mesh_config)
    os.environ["ELASTIC_APM_ENABLED"] = "true"
    os.environ["ELASTIC_APM_OTHER_OPTIONS"] = json.dumps(apm_options)


def main(
    scratch_path: str,
    suffix: str = "FITS",
    recipe_run_id: int = 2,
    skip_translation: bool = False,
    only_translate: bool = False,
    load_input_parsing: bool = False,
    load_dark: bool = False,
    load_background: bool = False,
    load_lamp: bool = False,
    load_geometric: bool = False,
    load_solar: bool = False,
    load_inst_pol: bool = False,
    use_apm: bool = False,
    transfer_trial_data: str | None = None,
):
    if use_apm:
        setup_APM_config()
    with ManualProcessing(
        workflow_path=scratch_path,
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name="visp-l0-pipeline",
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=translate_122_to_214l0_task(suffix=suffix))
        if only_translate:
            return
        manual_processing_run.run_task(task=CreateInputDatasetParameterDocument)

        if load_input_parsing:
            manual_processing_run.run_task(task=LoadInputParsing)
        else:
            manual_processing_run.run_task(task=tag_inputs_task(suffix))
            manual_processing_run.run_task(task=ParseL0VispInputData)
            manual_processing_run.run_task(task=SaveInputParsing)

        manual_processing_run.run_task(task=ShowMapMapping)
        manual_processing_run.run_task(task=VispL0QualityMetrics)
        manual_processing_run.run_task(task=ShowPolMode)
        manual_processing_run.run_task(task=ShowExposureTimes)

        if load_dark:
            manual_processing_run.run_task(task=LoadDarkCal)
        else:
            manual_processing_run.run_task(task=DarkCalibration)
            manual_processing_run.run_task(task=SaveDarkCal)

        if load_background:
            manual_processing_run.run_task(task=LoadBackgroundCal)
        else:
            manual_processing_run.run_task(task=BackgroundLightCalibration)
            manual_processing_run.run_task(task=SaveBackgroundCal)

        if load_lamp:
            manual_processing_run.run_task(task=LoadLampCal)
        else:
            manual_processing_run.run_task(task=LampCalibration)
            manual_processing_run.run_task(task=SaveLampCal)

        if load_geometric:
            manual_processing_run.run_task(task=LoadGeometricCal)
        else:
            manual_processing_run.run_task(task=GeometricCalibration)
            manual_processing_run.run_task(task=SaveGeometricCal)

        if load_solar:
            manual_processing_run.run_task(task=LoadSolarCal)
        else:
            manual_processing_run.run_task(task=SolarCalibration)
            manual_processing_run.run_task(task=SaveSolarCal)

        if load_inst_pol:
            manual_processing_run.run_task(task=LoadInstPolCal)
        else:
            manual_processing_run.run_task(task=InstrumentPolarizationCalibration)
            manual_processing_run.run_task(task=SaveInstPolCal)

        manual_processing_run.run_task(task=ScienceCalibration)
        manual_processing_run.run_task(task=VispWriteL1Frame)
        manual_processing_run.run_task(task=QualityL1Metrics)
        manual_processing_run.run_task(task=VispL1QualityMetrics)
        manual_processing_run.run_task(task=VispAssembleQualityData)
        manual_processing_run.run_task(task=ValidateL1Output)
        manual_processing_run.run_task(task=MakeVispMovieFrames)
        manual_processing_run.run_task(task=AssembleVispMovie)

        if transfer_trial_data:
            if transfer_trial_data == "default":
                trial_output_dir = (
                    Path(manual_processing_run.workflow_path) / str(recipe_run_id) / "trial_output"
                )
            else:
                trial_output_dir = Path(transfer_trial_data).absolute()

            logger.info(f"Writing trial output to {trial_output_dir}")
            transfer_local_task = transfer_trial_data_locally_task(trial_dir=trial_output_dir)
            manual_processing_run.run_task(transfer_local_task)

        # Test some downstream services
        if QUALITY:
            manual_processing_run.run_task(task=CreateTrialQualityReport)
        else:
            logger.warning("Did NOT make quality report pdf because dkist-quality is not installed")

        if INV:
            manual_processing_run.run_task(task=CreateTrialAsdf)
        else:
            logger.warning(
                "Did NOT make dataset asdf file because the asdf generator is not installed"
            )

        if any([load_dark, load_lamp, load_geometric, load_solar, load_inst_pol]):
            logger.info("NOT counting provenance records because some tasks were skipped")
        else:
            manual_processing_run.count_provenance()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an end-to-end test of the ViSP DC Science pipeline"
    )
    parser.add_argument("scratch_path", help="Location to use as the DC 'scratch' disk")
    parser.add_argument(
        "-i",
        "--run-id",
        help="Which subdir to use. This will become the recipe run id",
        type=int,
        default=4,
    )
    parser.add_argument("--suffix", help="File suffix to treat as INPUT frames", default="FITS")
    parser.add_argument(
        "-T",
        "--skip-translation",
        help="Skip the translation of raw 122 l0 frames to 214 l0",
        action="store_true",
    )
    parser.add_argument(
        "-t", "--only-translate", help="Do ONLY the translation step", action="store_true"
    )
    parser.add_argument(
        "-X",
        "--transfer-trial-data",
        help="Transfer trial data to a different location.",
        nargs="?",
        const="default",
        default=None,
    )
    parser.add_argument(
        "-I", "--load-input-parsing", help="Load tags on input files", action="store_true"
    )
    parser.add_argument(
        "-D",
        "--load-dark",
        help="Load dark calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-B",
        "--load-background",
        help="Load background light calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-L",
        "--load-lamp",
        help="Load lamp calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-G",
        "--load-geometric",
        help="Load geometric calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-S",
        "--load-solar",
        help="Load solar calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-P",
        "--load-inst-pol",
        help="Load instrument polarization calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument("-A", "--use-apm", help="Send APM spans to SIM", action="store_true")
    args = parser.parse_args()
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            suffix=args.suffix,
            recipe_run_id=args.run_id,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            load_input_parsing=args.load_input_parsing,
            load_dark=args.load_dark,
            load_background=args.load_background,
            load_lamp=args.load_lamp,
            load_geometric=args.load_geometric,
            load_solar=args.load_solar,
            load_inst_pol=args.load_inst_pol,
            use_apm=args.use_apm,
            transfer_trial_data=args.transfer_trial_data,
        )
    )
