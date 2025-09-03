import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path
from random import randint

import asdf
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_processing_common.tasks.mixin.globus import GlobusTransferItem
from dkist_service_configuration.logging import logger

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.models.task_name import CryonirspTaskName
from dkist_processing_cryonirsp.tasks.cryonirsp_base import CryonirspTaskBase
from dkist_processing_cryonirsp.tests.conftest import FileParameter
from dkist_processing_cryonirsp.tests.conftest import cryonirsp_testing_parameters_factory

# These are the workflow versions of the polyfit coefficient parameters
WORKFLOW_LINEARIZATION_POLYFIT_COEFFS_CI = [
    1.10505215e00,
    -7.50178863e-06,
    1.43050375e-10,
    -1.62898848e-15,
]

WORKFLOW_LINEARIZATION_POLYFIT_COEFFS_SP = [
    1.14636662,
    -1.05173302e-05,
    2.18059789e-10,
    -3.00894653e-15,
]


def save_parsing_task(
    tag_list: [str], save_file: str, save_file_tags: bool = True, save_constants: bool = True
):
    class SaveParsing(WorkflowTaskBase):
        """Save the result of parsing (constants and tags) to an asdf file."""

        @property
        def relative_save_file(self) -> str:
            return save_file

        def run(self):
            if save_file_tags:
                file_tag_dict = self.get_input_tags()
            else:
                logger.info("Skipping saving of file tags")
                file_tag_dict = dict()
            if save_constants:
                constant_dict = self.get_constants()
            else:
                logger.info("Skipping saving of constants")
                constant_dict = dict()

            full_save_file = self.scratch.workflow_base_path / self.relative_save_file
            tree = {"file_tag_dict": file_tag_dict, "constants_dict": constant_dict}
            af = asdf.AsdfFile(tree)
            af.write_to(full_save_file)
            logger.info(f"Saved input tags to {full_save_file}")

        def get_input_tags(self) -> dict[str, list[str]]:
            file_tag_dict = dict()
            path_list = self.read(tags=tag_list)
            for p in path_list:
                tags = self.tags(p)
                file_tag_dict[str(p)] = tags

            return file_tag_dict

        def get_constants(self) -> dict[str, str | float | list]:
            constants_dict = dict()
            for c in self.constants._db_dict.keys():
                constants_dict[c] = self.constants._db_dict[c]

            return constants_dict

    return SaveParsing


def load_parsing_task(save_file: str):
    class LoadParsing(WorkflowTaskBase):
        """Load tags and constants into the database."""

        @property
        def relative_save_file(self) -> str:
            return save_file

        def run(self):
            full_save_file = self.scratch.workflow_base_path / self.relative_save_file
            with asdf.open(full_save_file) as af:
                file_tag_dict = af.tree["file_tag_dict"]
                self.tag_input_files(file_tag_dict)

                constants_dict = af.tree["constants_dict"]
                self.populate_constants(constants_dict)

            logger.info(f"Loaded tags and constants from {full_save_file}")

        def tag_input_files(self, file_tag_dict: dict[str, list[str]]):
            for f, t in file_tag_dict.items():
                if not os.path.exists(f):
                    raise FileNotFoundError(f"Expected to find {f}, but it doesn't exist.")
                self.tag(path=f, tags=t)

        def populate_constants(self, constants_dict: dict[str, str | int | float]) -> None:
            # First we purge all constants because a previous load might have polluted the DB
            self.constants._purge()
            for c, v in constants_dict.items():
                logger.info(f"Setting value of {c} to {v}")
                self.constants._update({c: v})

    return LoadParsing


class SaveLinearizedFiles(WorkflowTaskBase):
    """Save linearized files and their tags to a directory and asdf file."""

    @property
    def relative_save_file(self) -> str:
        return "linearized.asdf"

    def run(self):
        file_tag_dict = dict()
        path_list = self.read(tags=[CryonirspTag.linearized()])
        save_dir = self.scratch.workflow_base_path / Path(self.relative_save_file).stem
        save_dir.mkdir(exist_ok=True)
        for p in path_list:
            copied_path = shutil.move(str(p), save_dir)
            tags = self.tags(p)
            file_tag_dict[copied_path] = tags

        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        tree = {"file_tag_dict": file_tag_dict}
        af = asdf.AsdfFile(tree)
        af.write_to(full_save_file)
        logger.info(f"Saved linearized tags to {full_save_file}")


class LoadLinearizedFiles(WorkflowTaskBase):
    """Load linearized tags that point to previously saved files."""

    @property
    def relative_save_file(self) -> str:
        return "linearized.asdf"

    def run(self):
        full_save_file = self.scratch.workflow_base_path / self.relative_save_file
        with asdf.open(full_save_file) as af:
            for f, t in af.tree["file_tag_dict"].items():
                # This is so any of the old (un-moved) files still tagged in the db are removed from the db
                current_files = self.read(tags=t)
                for current_file in current_files:
                    self.remove_tags(current_file, t)

                self.tag(path=f, tags=t)
        logger.info(f"Loaded linearized files entries from {full_save_file}")


class SaveTaskTags(WorkflowTaskBase):
    @property
    def task_str(self) -> str:
        return "TASK"

    @property
    def relative_save_file(self) -> str:
        return "default_sav.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]] | list[str]:
        return [[CryonirspTag.task(self.task_str), CryonirspTag.intermediate()]]

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
        path_list = list(
            self.read(tags=[CryonirspTag.task_geometric_angle(), CryonirspTag.intermediate()])
        )
        path_list += list(
            self.read(tags=[CryonirspTag.task_geometric_offset(), CryonirspTag.intermediate()])
        )
        path_list += list(
            self.read(
                tags=[CryonirspTag.task_geometric_spectral_shifts(), CryonirspTag.intermediate()]
            )
        )
        path_list += list(
            self.read(
                tags=[
                    CryonirspTag.quality("TASK_TYPES"),
                    CryonirspTag.workflow_task("SPGeometricCalibration"),
                ]
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


class SaveBadPixelMap(SaveTaskTags):
    @property
    def task_str(self):
        return CryonirspTaskName.bad_pixel_map.value

    @property
    def relative_save_file(self) -> str:
        return "bad_pixel_map.asdf"


class LoadBadPixelMap(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "bad_pixel_map.asdf"


class SaveBeamBoundaryCal(SaveTaskTags):
    @property
    def task_str(self):
        return CryonirspTaskName.beam_boundaries.value

    @property
    def relative_save_file(self) -> str:
        return "beam_boundary_cal.asdf"


class LoadBeamBoundaryCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "beam_boundary_cal.asdf"


class SaveDarkCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.dark.value

    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [CryonirspTag.quality("TASK_TYPES"), CryonirspTag.workflow_task("DarkCalibration")]
        ]


class LoadDarkCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "dark_cal.asdf"


class SaveLampCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.lamp_gain.value

    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [CryonirspTag.quality("TASK_TYPES"), CryonirspTag.workflow_task("LampGainCalibration")],
        ]


class LoadLampCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "lamp_cal.asdf"


class SaveSolarCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.solar_gain.value

    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                CryonirspTag.quality("TASK_TYPES"),
                CryonirspTag.workflow_task("CISolarGainCalibration"),
            ],
            [
                CryonirspTag.quality("TASK_TYPES"),
                CryonirspTag.workflow_task("SPSolarGainCalibration"),
            ],
            [
                CryonirspTag.intermediate(),
                CryonirspTag.task_characteristic_spectra(),
            ],
        ]


class SaveWavelengthCorrection(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return CryonirspTaskName.spectral_fit.value

    @property
    def relative_save_file(self) -> str:
        return "sp_wavelength_correction.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                CryonirspTag.quality("TASK_TYPES"),
                CryonirspTag.workflow_task("SPDispersionAxisCorrection"),
            ],
        ]


class LoadSolarCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "solar_cal.asdf"


class LoadWavelengthCorrection(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "sp_wavelength_correction.asdf"


class SaveInstPolCal(SaveTaskTags):
    @property
    def task_str(self) -> str:
        return TaskName.demodulation_matrices.value

    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"

    @property
    def tag_lists_to_save(self) -> list[list[str]]:
        return super().tag_lists_to_save + [
            [
                CryonirspTag.quality("TASK_TYPES"),
                CryonirspTag.workflow_task("CIInstrumentPolarizationCalibration"),
            ],
            [
                CryonirspTag.quality("TASK_TYPES"),
                CryonirspTag.workflow_task("SPInstrumentPolarizationCalibration"),
            ],
            [CryonirspTag.quality("POLCAL_CONSTANT_PAR_VALS")],
            [CryonirspTag.quality("POLCAL_GLOBAL_PAR_VALS")],
            [CryonirspTag.quality("POLCAL_LOCAL_PAR_VALS")],
            [CryonirspTag.quality("POLCAL_FIT_RESIDUALS")],
            [CryonirspTag.quality("POLCAL_EFFICIENCY")],
        ]


class LoadInstPolCal(LoadTaskTags):
    @property
    def relative_save_file(self) -> str:
        return "inst_pol_cal.asdf"


def translate_122_to_214_task(suffix: str):
    class Translate122To214L0(WorkflowTaskBase):
        def run(self) -> None:
            raw_dir = Path(self.scratch.scratch_base_path) / f"CRYONIRSP{self.recipe_run_id:03n}"
            if not os.path.exists(self.scratch.workflow_base_path):
                os.makedirs(self.scratch.workflow_base_path)

            if not raw_dir.exists():
                raise FileNotFoundError(
                    f"Expected to find a raw CRYONIRSP{self.recipe_run_id:03n} folder in {self.scratch.scratch_base_path}"
                )

            for file in raw_dir.glob(f"*.{suffix}"):
                translated_file_name = Path(self.scratch.workflow_base_path) / os.path.basename(
                    file
                )
                logger.info(f"Translating {file} -> {translated_file_name}")
                hdl = fits.open(file)
                # Handle both compressed and uncompressed files...
                if len(hdl) > 1:
                    hdl_header = hdl[1].header
                    hdl_data = hdl[1].data
                else:
                    hdl_header = hdl[0].header
                    hdl_data = hdl[0].data
                header = spec122_validator.validate_and_translate_to_214_l0(
                    hdl_header, return_type=fits.HDUList
                )[0].header

                comp_hdu = fits.CompImageHDU(header=header, data=hdl_data)
                comp_hdl = fits.HDUList([fits.PrimaryHDU(), comp_hdu])
                comp_hdl.writeto(translated_file_name, overwrite=True)

                hdl.close()
                del hdl
                comp_hdl.close()
                del comp_hdl

    return Translate122To214L0


def create_input_dataset_parameter_document(param_path: Path):
    class CreateInputDatasetParameterDocument(WorkflowTaskBase):
        def run(self) -> None:
            relative_path = "input_dataset_parameters.json"
            self.write(
                data=InputDatasetPartDocumentList(
                    doc_list=self.input_dataset_document_simple_parameters_part
                ),
                relative_path=relative_path,
                tags=CryonirspTag.input_dataset_parameters(),
                encoder=basemodel_encoder,
                overwrite=True,
            )
            logger.info(f"Wrote input dataset parameter doc to {relative_path}")
            self.copy_and_tag_parameter_files(param_path=param_path)
            logger.info(f"Copied input dataset parameter files from {param_path}")

        @property
        def parameter_dict(self):
            param_class = cryonirsp_testing_parameters_factory(task=self, create_files=False)
            params = asdict(
                param_class(
                    cryonirsp_linearization_polyfit_coeffs_ci=WORKFLOW_LINEARIZATION_POLYFIT_COEFFS_CI,
                    cryonirsp_linearization_polyfit_coeffs_sp=WORKFLOW_LINEARIZATION_POLYFIT_COEFFS_SP,
                )
            )
            return params

        @property
        def input_dataset_document_simple_parameters_part(self):
            parameters_list = []
            value_id = randint(1000, 2000)
            params = self.parameter_dict
            for pn, pv in params.items():
                if isinstance(pv, FileParameter):
                    pv = pv.model_dump()
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

        def copy_and_tag_parameter_files(self, param_path=param_path):
            # Copy parameter files from param_path to a place where they can be tagged
            params = self.parameter_dict
            destination_dir = Path(self.scratch.workflow_base_path) / "parameters"
            destination_dir.mkdir(parents=True, exist_ok=True)
            for pn, pv in params.items():
                if isinstance(pv, FileParameter):
                    file_path = next(param_path.rglob(pv.file_pointer.object_key))
                    if file_path.parent != destination_dir:
                        shutil.copy(file_path, destination_dir)
                        logger.info(
                            f"Copied parameter file for '{pn}' to {destination_dir / file_path}"
                        )
                        file_path = next(destination_dir.rglob(pv.file_pointer.object_key))
                    self.tag(path=file_path, tags=pv.file_pointer.tag)

    return CreateInputDatasetParameterDocument


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
                self.tag(path=file, tags=[CryonirspTag.input(), CryonirspTag.frame()])

    return TagInputs


class DBAccess(CryonirspTaskBase):
    """
    No-Op task that allows use to access the redis database.

    I.e.:

    task = DBAccess(recipe_run_id)
    value = task.constants.whatever
    """

    def __init__(self, recipe_run_id: int):
        workflow_name = "redis_db_access_task"
        workflow_version = "vfoo.bar"

        super().__init__(
            recipe_run_id=recipe_run_id,
            workflow_name=workflow_name,
            workflow_version=workflow_version,
        )

    def run(self) -> None:
        pass

    def __call__(self, *args, **kwargs):
        raise RuntimeError(f"{self.__class__.__name__} not intended to be called.")


def transfer_trial_data_locally_task(
    trial_dir: str | Path,
    debug_switch: bool = True,
    intermediate_switch: bool = True,
    output_swtich: bool = True,
    tag_lists: list | None = None,
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
