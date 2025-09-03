import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from astropy.io import fits
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.constants import CryonirspBudName
from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks import CIBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks import SPWavelengthCalibration
from dkist_processing_cryonirsp.tasks.bad_pixel_map import BadPixelMapCalibration
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase
from dkist_processing_cryonirsp.tasks.dark import DarkCalibration
from dkist_processing_cryonirsp.tasks.gain import CISolarGainCalibration
from dkist_processing_cryonirsp.tasks.gain import LampGainCalibration
from dkist_processing_cryonirsp.tasks.instrument_polarization import (
    CIInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tasks.instrument_polarization import (
    SPInstrumentPolarizationCalibration,
)
from dkist_processing_cryonirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspCILinearizedData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspSPLinearizedData
from dkist_processing_cryonirsp.tasks.sp_beam_boundaries import SPBeamBoundariesCalibration
from dkist_processing_cryonirsp.tasks.sp_geometric import SPGeometricCalibration
from dkist_processing_cryonirsp.tasks.sp_solar_gain import SPSolarGainCalibration
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import DBAccess
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadBadPixelMap,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadBeamBoundaryCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import LoadDarkCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadGeometricCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadInstPolCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import LoadLampCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadLinearizedFiles,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import LoadSolarCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    LoadWavelengthCorrection,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveBadPixelMap,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveBeamBoundaryCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import SaveDarkCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveGeometricCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveInstPolCal,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import SaveLampCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveLinearizedFiles,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import SaveSolarCal
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveWavelengthCorrection,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    create_input_dataset_parameter_document,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    load_parsing_task,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    save_parsing_task,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    tag_inputs_task,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    translate_122_to_214_task,
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


def tag_linearized_inputs_task(suffix: str):
    class TagLinearizedInputs(WorkflowTaskBase):
        def run(self) -> None:
            logger.info(f"Looking in {os.path.abspath(self.scratch.workflow_base_path)}")
            input_file_list = list(self.scratch.workflow_base_path.glob(f"*.{suffix}"))
            if len(input_file_list) == 0:
                raise FileNotFoundError(
                    f"Did not find any files matching '*.{suffix}' in {self.scratch.workflow_base_path}"
                )
            for file in input_file_list:
                logger.info(f"Found {file}")
                self.tag(path=file, tags=CryonirspTag.linearized_frame())
            # Update the arm_id constant, as it is derived in linearity processing
            with fits.open(file) as hdul:
                if len(hdul) == 1:
                    hdu = hdul[0]
                else:
                    hdu = hdul[1]
                arm_id = hdu.header["CNARMID"]
            self.constants._update({CryonirspBudName.arm_id.value: arm_id})

    return TagLinearizedInputs


def spoof_obs_ramp_parsed_constants(wavelength: float = 1083.0):
    class SetObsWavelength(WorkflowTaskBase):
        def run(self) -> None:
            self.constants._update({CryonirspBudName.wavelength.value: wavelength})
            self.constants._update({BudName.obs_ip_start_time.value: datetime.now().isoformat()})

    return SetObsWavelength


def spoof_obs_lin_parsed_constants(
    polarimetric: bool = True,
):
    class SetCalOnlyConstants(CryonirspTaskBase):
        def run(self) -> None:
            self.constants._update(
                {
                    CryonirspBudName.observe_exposure_conditions_list.value: self.constants.solar_gain_exposure_conditions_list
                }
            )

            if polarimetric:
                self.constants._update({CryonirspBudName.num_modstates.value: 8})
                self.constants._update({CryonirspBudName.modulator_spin_mode.value: "Continuous"})
            else:
                self.constants._update({CryonirspBudName.num_modstates.value: 1})
                self.constants._update({CryonirspBudName.modulator_spin_mode.value: "None"})

    return SetCalOnlyConstants


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


def CI_workflow(
    manual_processing_run: ManualProcessing,
    load_beam_boundaries: bool = False,
    load_dark: bool = False,
    load_solar: bool = False,
    load_inst_pol: bool = False,
) -> None:
    if load_beam_boundaries:
        manual_processing_run.run_task(task=LoadBeamBoundaryCal)
    else:
        manual_processing_run.run_task(task=CIBeamBoundariesCalibration)
        manual_processing_run.run_task(task=SaveBeamBoundaryCal)

    if load_dark:
        manual_processing_run.run_task(task=LoadDarkCal)
    else:
        manual_processing_run.run_task(task=DarkCalibration)
        manual_processing_run.run_task(task=SaveDarkCal)

    if load_solar:
        manual_processing_run.run_task(task=LoadSolarCal)
    else:
        manual_processing_run.run_task(task=CISolarGainCalibration)
        manual_processing_run.run_task(task=SaveSolarCal)

    if load_inst_pol:
        manual_processing_run.run_task(task=LoadInstPolCal)
    else:
        manual_processing_run.run_task(task=CIInstrumentPolarizationCalibration)
        manual_processing_run.run_task(task=SaveInstPolCal)


def SP_workflow(
    manual_processing_run: ManualProcessing,
    load_beam_boundaries: bool = False,
    load_dark: bool = False,
    load_lamp: bool = False,
    load_geometric: bool = False,
    load_solar: bool = False,
    load_wavelength_correction: bool = False,
    load_inst_pol: bool = False,
) -> None:
    if load_beam_boundaries:
        manual_processing_run.run_task(task=LoadBeamBoundaryCal)
    else:
        manual_processing_run.run_task(task=SPBeamBoundariesCalibration)
        manual_processing_run.run_task(task=SaveBeamBoundaryCal)

    if load_dark:
        manual_processing_run.run_task(task=LoadDarkCal)
    else:
        manual_processing_run.run_task(task=DarkCalibration)
        manual_processing_run.run_task(task=SaveDarkCal)

    if load_lamp:
        manual_processing_run.run_task(task=LoadLampCal)
    else:
        manual_processing_run.run_task(task=LampGainCalibration)
        manual_processing_run.run_task(task=SaveLampCal)

    if load_geometric:
        manual_processing_run.run_task(task=LoadGeometricCal)
    else:
        manual_processing_run.run_task(task=SPGeometricCalibration)
        manual_processing_run.run_task(task=SaveGeometricCal)

    if load_solar:
        manual_processing_run.run_task(task=LoadSolarCal)
    else:
        manual_processing_run.run_task(task=SPSolarGainCalibration)
        manual_processing_run.run_task(task=SaveSolarCal)

    if load_wavelength_correction:
        manual_processing_run.run_task(task=LoadWavelengthCorrection)
    else:
        manual_processing_run.run_task(task=SPWavelengthCalibration)
        manual_processing_run.run_task(task=SaveWavelengthCorrection)

    if load_inst_pol:
        manual_processing_run.run_task(task=LoadInstPolCal)
    else:
        manual_processing_run.run_task(task=SPInstrumentPolarizationCalibration)
        manual_processing_run.run_task(task=SaveInstPolCal)


def main(
    scratch_path: str,
    suffix: str = "FITS",
    recipe_run_id: int = 2,
    skip_translation: bool = False,
    only_translate: bool = False,
    skip_saving_parse: bool = False,
    load_input_parsing: bool = False,
    load_linearized: bool = False,
    only_linearize: bool = False,
    load_linearized_parsing: bool = False,
    load_bad_pixel_map: bool = False,
    load_beam_boundaries: bool = False,
    load_dark: bool = False,
    load_lamp: bool = False,
    load_geometric: bool = False,
    load_solar: bool = False,
    load_wavelength_correction: bool = False,
    load_inst_pol: bool = False,
    use_apm: bool = False,
    param_path: Path = None,
    dummy_wavelength: float = 1083.0,
    polarimetric: bool = True,
):
    if use_apm:
        setup_APM_config()
    with ManualProcessing(
        workflow_path=Path(scratch_path),
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name="sp_l0_to_l1_cryonirsp",
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=translate_122_to_214_task(suffix))
        if only_translate:
            return
        manual_processing_run.run_task(
            task=create_input_dataset_parameter_document(param_path=param_path)
        )

        if not load_linearized:
            manual_processing_run.run_task(task=tag_inputs_task(suffix))

        if load_input_parsing or load_linearized:
            manual_processing_run.run_task(task=load_parsing_task(save_file="input_parsing.asdf"))
        else:
            manual_processing_run.run_task(task=ParseL0CryonirspRampData)
            manual_processing_run.run_task(task=spoof_obs_ramp_parsed_constants(dummy_wavelength))
            manual_processing_run.run_task(
                task=save_parsing_task(
                    tag_list=[CryonirspTag.input(), CryonirspTag.frame()],
                    save_file="input_parsing.asdf",
                    save_file_tags=False,
                )
            )

        if load_linearized:
            manual_processing_run.run_task(task=LoadLinearizedFiles)
        else:
            manual_processing_run.run_task(task=LinearityCorrection)
            manual_processing_run.run_task(task=SaveLinearizedFiles)
            manual_processing_run.run_task(task=LoadLinearizedFiles)

        if only_linearize:
            logger.info("Linearization complete. All done.")
            return

        db_access = DBAccess(recipe_run_id=recipe_run_id)
        arm_id = db_access.constants.arm_id

        if load_linearized_parsing:
            manual_processing_run.run_task(
                task=load_parsing_task(save_file="linearized_parsing.asdf")
            )
        else:
            if arm_id == "SP":
                manual_processing_run.run_task(task=ParseL0CryonirspSPLinearizedData)
            elif arm_id == "CI":
                manual_processing_run.run_task(task=ParseL0CryonirspCILinearizedData)
            else:
                raise ValueError(f"Did not recognize {arm_id = }")
            manual_processing_run.run_task(
                task=spoof_obs_lin_parsed_constants(polarimetric=polarimetric)
            )
            if not skip_saving_parse:
                manual_processing_run.run_task(
                    task=save_parsing_task(
                        tag_list=CryonirspTag.linearized_frame(),
                        save_file="linearized_parsing.asdf",
                    )
                )

        if load_bad_pixel_map:
            manual_processing_run.run_task(task=LoadBadPixelMap)
        else:
            manual_processing_run.run_task(task=BadPixelMapCalibration)
            manual_processing_run.run_task(task=SaveBadPixelMap)

        if arm_id == "SP":
            logger.info("Running SP pipeline")
            SP_workflow(
                manual_processing_run,
                load_beam_boundaries=load_beam_boundaries,
                load_dark=load_dark,
                load_lamp=load_lamp,
                load_geometric=load_geometric,
                load_solar=load_solar,
                load_wavelength_correction=load_wavelength_correction,
                load_inst_pol=load_inst_pol,
            )
        elif arm_id == "CI":
            logger.info("Running CI pipeline")
            CI_workflow(
                manual_processing_run,
                load_beam_boundaries=load_beam_boundaries,
                load_dark=load_dark,
                load_solar=load_solar,
                load_inst_pol=load_inst_pol,
            )
        else:
            raise ValueError(f"Did not recognize {arm_id = }")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an end-to-end test of the Cryonirsp DC Science pipeline"
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
        "--skip-saving-parse",
        help="DON'T save the results of either parsing. Useful for really large "
        "datasets that you know will only be run once.",
        action="store_true",
    )
    parser.add_argument(
        "-I",
        "--load-input-parsing",
        help="Load constants on input files",
        action="store_true",
    )
    parser.add_argument(
        "-Z",
        "--load-linearized",
        help="Load linearized tags from a previous run",
        action="store_true",
    )
    parser.add_argument(
        "-z", "--only-linearize", help="Don't continue after linearization", action="store_true"
    )
    parser.add_argument(
        "-R",
        "--load-linearized-parsing",
        help="Load tags and constants from linearized files",
        action="store_true",
    )
    parser.add_argument(
        "-M",
        "--load-bad-pixel-map",
        help="Load bad pixel map from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-B",
        "--load-beam-boundaries",
        help="Load beam boundaries from a previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-D",
        "--load-dark",
        help="Load dark calibration from previously saved run",
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
        "-W",
        "--load-wavelength-correction",
        help="Load wavelength correction solution from previously saved run",
        action="store_true",
    )
    parser.add_argument(
        "-P",
        "--load-inst-pol",
        help="Load instrument polarization calibration from previously saved run",
        action="store_true",
    )
    parser.add_argument("-A", "--use-apm", help="Send APM spans to SIM", action="store_true")
    parser.add_argument(
        "-p",
        "--param-path",
        help="Path to parameter directory",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--intensity-only",
        help="Contrive constants so pipeline thinks data are non-polarimetric",
        action="store_true",
    )

    args = parser.parse_args()
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            suffix=args.suffix,
            recipe_run_id=args.run_id,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            skip_saving_parse=args.skip_saving_parse,
            load_input_parsing=args.load_input_parsing,
            load_linearized=args.load_linearized,
            only_linearize=args.only_linearize,
            load_linearized_parsing=args.load_linearized_parsing,
            load_bad_pixel_map=args.load_bad_pixel_map,
            load_beam_boundaries=args.load_beam_boundaries,
            load_dark=args.load_dark,
            load_lamp=args.load_lamp,
            load_geometric=args.load_geometric,
            load_solar=args.load_solar,
            load_wavelength_correction=args.load_wavelength_correction,
            load_inst_pol=args.load_inst_pol,
            use_apm=args.use_apm,
            param_path=Path(args.param_path),
            polarimetric=not args.intensity_only,
        )
    )
