import argparse
import sys
from pathlib import Path

from dkist_processing_common.manual import ManualProcessing

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.linearity_correction import LinearityCorrection
from dkist_processing_cryonirsp.tasks.parse import ParseL0CryonirspRampData
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    SaveLinearizedFiles,
)
from dkist_processing_cryonirsp.tests.local_trial_workflows.local_trial_helpers import (
    create_input_dataset_parameter_document,
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


def main(
    scratch_path: str,
    suffix: str = "dat",
    recipe_run_id: int = 2,
    skip_translation: bool = False,
    param_path: Path = None,
):
    with ManualProcessing(
        workflow_path=Path(scratch_path),
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name="cryonirsp-l0-pipeline",  # need sperate workflows for CI and SP?
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(task=translate_122_to_214_task(suffix))

        manual_processing_run.run_task(
            task=create_input_dataset_parameter_document(param_path=param_path)
        )
        manual_processing_run.run_task(task=tag_inputs_task(suffix))
        manual_processing_run.run_task(task=ParseL0CryonirspRampData)
        manual_processing_run.run_task(
            task=save_parsing_task(
                tag_list=[CryonirspTag.input(), CryonirspTag.frame()],
                save_file="input_parsing.asdf",
                save_file_tags=False,
            )
        )
        manual_processing_run.run_task(task=LinearityCorrection)
        manual_processing_run.run_task(task=SaveLinearizedFiles)


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
        "-p",
        "--param-path",
        help="Path to parameter directory",
        type=str,
        default=None,
    )

    args = parser.parse_args()
    sys.exit(
        main(
            scratch_path=args.scratch_path,
            suffix=args.suffix,
            recipe_run_id=args.run_id,
            skip_translation=args.skip_translation,
            param_path=Path(args.param_path),
        )
    )
