import argparse
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from random import randint

from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_visp.models.tags import VispTag
from dkist_processing_visp.tasks import AssembleVispMovie
from dkist_processing_visp.tasks import MakeVispMovieFrames
from dkist_processing_visp.tasks import ScienceCalibration
from dkist_processing_visp.tasks import VispAssembleQualityData
from dkist_processing_visp.tasks import VispL1QualityMetrics
from dkist_processing_visp.tasks import VispWriteL1Frame
from dkist_processing_visp.tasks.background_light import BackgroundLightCalibration
from dkist_processing_visp.tasks.dark import DarkCalibration
from dkist_processing_visp.tasks.geometric import GeometricCalibration
from dkist_processing_visp.tasks.instrument_polarization import InstrumentPolarizationCalibration
from dkist_processing_visp.tasks.lamp import LampCalibration
from dkist_processing_visp.tasks.solar import SolarCalibration
from dkist_processing_visp.tests.conftest import VispInputDatasetParameterValues
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadCalibratedData
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import LoadSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    ParseCalOnlyL0InputData,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveBackgroundCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveCalibratedData
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveDarkCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveGeometricCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInputParsing
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveInstPolCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveLampCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SaveSolarCal
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SaveSolarGainAsScience,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetAxesTypes
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SetCadenceConstants,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetNumModstates
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetObserveExpTime
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    SetObserveIpStartTime,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import SetPolarimeterMode
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    TagModulatedSolarGainsAsScience,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    TagSingleSolarGainAsScience,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import ValidateL1Output
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    load_solar_gain_as_science_task,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    set_observe_wavelength_task,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import tag_inputs_task
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    transfer_trial_data_locally_task,
)
from dkist_processing_visp.tests.local_trial_workflows.local_trial_helpers import (
    translate_122_to_214l0_task,
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


class DatetimeEncoder(json.JSONEncoder):
    # Copied from quality_report_maker
    """
    A JSON encoder which encodes datetime(s) as iso formatted strings.
    """

    def default(self, obj):
        if isinstance(obj, datetime):
            return {"iso_date": obj.isoformat("T")}
        return super().default(obj)


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
        for pn, pv in asdict(
            VispInputDatasetParameterValues(
                visp_background_on=False,
                visp_geo_upsample_factor=10000,
                visp_polcal_num_spatial_bins=2560,
            )
        ).items():
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
    load_solar_gain_as_science: bool = False,
    load_calibrated_data: bool = False,
    force_intensity_only: bool = False,
    transfer_trial_data: str | None = None,
    use_apm: bool = False,
    dummy_wavelength: float = 630.0,
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
            manual_processing_run.run_task(task=ParseCalOnlyL0InputData)
            manual_processing_run.run_task(
                task=set_observe_wavelength_task(wavelength=dummy_wavelength)
            )
            manual_processing_run.run_task(task=SetObserveIpStartTime)
            manual_processing_run.run_task(task=SetObserveExpTime)
            manual_processing_run.run_task(task=SetPolarimeterMode)
            manual_processing_run.run_task(task=SetNumModstates)
            manual_processing_run.run_task(task=SetCadenceConstants)
            manual_processing_run.run_task(task=SetAxesTypes)
            manual_processing_run.run_task(task=SaveInputParsing)

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

        if load_solar_gain_as_science:
            manual_processing_run.run_task(
                task=load_solar_gain_as_science_task(force_intensity_only=force_intensity_only)
            )
        else:
            if force_intensity_only:
                manual_processing_run.run_task(task=TagSingleSolarGainAsScience)
            else:
                manual_processing_run.run_task(task=TagModulatedSolarGainsAsScience)
            manual_processing_run.run_task(task=SaveSolarGainAsScience)

        if load_calibrated_data:
            manual_processing_run.run_task(task=LoadCalibratedData)
        else:
            manual_processing_run.run_task(task=ScienceCalibration)
            manual_processing_run.run_task(task=SaveCalibratedData)

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
        "-w",
        "--wavelength",
        help="Dummy wavelength to use for loading parameters, etc.",
        type=float,
        default=630.0,
    )
    parser.add_argument(
        "--force-I-only",
        help="Force the dataset to be treated as non-polarimetric",
        action="store_true",
    )
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
    parser.add_argument(
        "-O",
        "--load-solar-gain-as-science",
        help="Don't re-make the polcals-as-science frames",
        action="store_true",
    )
    parser.add_argument(
        "-C", "--load-calibrated-data", help="Load CALIBRATED 'science' frames", action="store_true"
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
            load_solar_gain_as_science=args.load_solar_gain_as_science,
            load_calibrated_data=args.load_calibrated_data,
            force_intensity_only=args.force_I_only,
            transfer_trial_data=args.transfer_trial_data,
            use_apm=args.use_apm,
        )
    )
