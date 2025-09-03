from datetime import datetime
from pathlib import Path

import numpy as np
import pytest
from astropy.io import fits
from astropy.time import Time
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.json import json_encoder

from dkist_processing_cryonirsp.models.tags import CryonirspTag
from dkist_processing_cryonirsp.tasks.write_l1 import CIWriteL1Frame
from dkist_processing_cryonirsp.tasks.write_l1 import CryonirspWriteL1Frame
from dkist_processing_cryonirsp.tasks.write_l1 import SPWriteL1Frame
from dkist_processing_cryonirsp.tests.conftest import CryonirspConstantsDb


@pytest.fixture(scope="function")
def write_l1_task(
    recipe_run_id,
    calibrated_ci_cryonirsp_headers,
    calibrated_cryonirsp_headers,
    init_cryonirsp_constants_db,
    num_stokes_params,
    num_map_scans,
    num_meas,
    arm_id,
):
    if num_stokes_params == 1:
        num_modstates = 1
    else:
        num_modstates = 2
    num_scan_steps = 2
    if arm_id == "CI":
        axis_1_type = "HPLN-TAN"
        axis_2_type = "HPLT-TAN"
        axis_3_type = "AWAV"
        write_l1_task = CIWriteL1Frame
        calibrated_headers = calibrated_ci_cryonirsp_headers
    else:
        axis_1_type = "AWAV"
        axis_2_type = "HPLT-TAN"
        axis_3_type = "HPLN-TAN"
        write_l1_task = SPWriteL1Frame
        calibrated_headers = calibrated_cryonirsp_headers

    constants_db = CryonirspConstantsDb(
        AVERAGE_CADENCE=10,
        MINIMUM_CADENCE=10,
        MAXIMUM_CADENCE=10,
        VARIANCE_CADENCE=0,
        NUM_MAP_SCANS=num_map_scans,
        NUM_SCAN_STEPS=num_scan_steps,
        # Needed so self.correct_for_polarization is set to the right value
        NUM_MODSTATES=num_modstates,
        ARM_ID=arm_id,
        AXIS_1_TYPE=axis_1_type,
        AXIS_2_TYPE=axis_2_type,
        AXIS_3_TYPE=axis_3_type,
        NUM_MEAS=num_meas,
    )

    init_cryonirsp_constants_db(recipe_run_id, constants_db)
    with write_l1_task(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        try:  # This try... block is here to make sure the dbs get cleaned up if there's a failure in the fixture
            if num_stokes_params == 1:
                stokes_params = ["I"]
            else:
                stokes_params = ["I", "Q", "U", "V"]
            # Random data needed so skew and kurtosis don't barf
            header = calibrated_headers
            hdu = fits.PrimaryHDU(
                data=np.random.random((header["NAXIS3"], header["NAXIS2"], header["NAXIS1"]))
                * 100.0,
                header=calibrated_headers,
            )
            hdul = fits.HDUList([hdu])
            hdul[0].header["CTYPE1"] = axis_1_type
            hdul[0].header["CTYPE2"] = axis_2_type
            hdul[0].header["CTYPE3"] = axis_3_type
            hdul[0].header["CNNMAPS"] = num_map_scans

            # Set CNMODNST and CNSPINMD so the correct schema is loaded for validation
            hdul[0].header["CNMODNST"] = num_modstates
            if num_stokes_params > 1:
                hdul[0].header["CNSPINMD"] = "Continuous"

                # These headers are added to polarimetric frames in the science task
                hdul[0].header["POL_NOIS"] = 0.1
                hdul[0].header["POL_SENS"] = 0.2

            else:
                hdul[0].header["CNSPINMD"] = "None"

            if arm_id == "SP":
                write_dummy_sp_dispersion_intermediate(task)

            for map_scan in range(1, num_map_scans + 1):
                for scan_step in range(1, num_scan_steps + 1):
                    for meas_num in range(1, num_meas + 1):
                        # all stokes files have the same date-beg
                        hdul[0].header["DATE-BEG"] = datetime.now().isoformat("T")
                        for stokes_param in stokes_params:
                            hdul[0].header["CNCMEAS"] = meas_num
                            hdul[0].header["CNMAP"] = map_scan
                            task.write(
                                data=hdul,
                                tags=[
                                    CryonirspTag.calibrated(),
                                    CryonirspTag.frame(),
                                    CryonirspTag.stokes(stokes_param),
                                    CryonirspTag.meas_num(meas_num),
                                    CryonirspTag.map_scan(map_scan),
                                    CryonirspTag.scan_step(scan_step),
                                ],
                                encoder=fits_hdulist_encoder,
                            )
            yield task, stokes_params, hdul[0].header
        finally:
            task._purge()


def write_dummy_sp_dispersion_intermediate(task: SPWriteL1Frame) -> None:
    dummy_fit_solution = {
        "CTYPE1": "AWAV-GRA",
        "CUNIT1": "nm",
        "CRPIX1": 5,  # This needs to be 5 for `axis_flip_tests`
        "CRVAL1": 9999.0,
        "CDELT1": 4.56,
        "PV1_0": 78.9,
        "PV1_1": 51,
        "PV1_2": 11121,
    }

    dummy_fit_solution = dummy_fit_solution | {f"{k}A": v for k, v in dummy_fit_solution.items()}

    task.write(
        data=dummy_fit_solution,
        tags=[CryonirspTag.intermediate(), CryonirspTag.task_spectral_fit()],
        encoder=json_encoder,
    )


@pytest.mark.parametrize(
    "num_stokes_params",
    [pytest.param(1, id="Stokes I"), pytest.param(4, id="Stokes IQUV")],
)
@pytest.mark.parametrize(
    "num_meas",
    [pytest.param(1, id="single meas"), pytest.param(2, id="multiple meas")],
)
@pytest.mark.parametrize(
    "num_map_scans",
    [pytest.param(1, id="single map"), pytest.param(2, id="multiple maps")],
)
@pytest.mark.parametrize(
    "arm_id",
    [pytest.param("CI", id="CI"), pytest.param("SP", id="SP")],
)
def test_write_l1_frame(
    write_l1_task, mocker, fake_gql_client, arm_id, num_stokes_params, num_map_scans, num_meas
):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: the correct header keys are written
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, stokes_params, original_headers = write_l1_task
    task()

    for stokes_param in stokes_params:
        common_tags = [
            CryonirspTag.frame(),
            CryonirspTag.stokes(stokes_param),
        ]
        output_files = list(task.read(tags=common_tags + [CryonirspTag.output()]))
        calibrated_files = list(task.read(tags=common_tags + [CryonirspTag.calibrated()]))
        assert (
            len(output_files)
            == task.constants.num_map_scans
            * task.constants.num_scan_steps
            * task.constants.num_meas
        )
        preserve_date_tests(output_files, calibrated_files)
        for output_file in output_files:
            assert output_file.exists
            assert output_file.name.startswith(f"CRYO-NIRSP_{arm_id}_")
            assert spec214_validator.validate(output_file, extra=False)
            hdu_list = fits.open(output_file)
            header = hdu_list[1].header
            assert len(hdu_list) == 2  # Primary, CompImage
            assert type(hdu_list[0]) is fits.PrimaryHDU
            assert type(hdu_list[1]) is fits.CompImageHDU
            axis_num = 1
            if arm_id == "CI":
                longitude_axis_tests(axis_num, header)
                ci_spatial_axis_correction_tests(axis_num, original_headers, header)
            else:
                spectral_axis_tests(axis_num, header)
                sp_spatial_axis_correction_tests(axis_num, original_headers, header)
                sp_spectral_axis_correction_tests(original_headers, header)
            axis_num += 1
            latitude_axis_tests(axis_num, arm_id, header)
            axis_num += 1
            if task.constants.num_meas > 1:
                measurement_axis_tests(axis_num, header, task)
                axis_num += 1
            scan_step_axis_tests(axis_num, arm_id, header, task)
            if task.constants.num_map_scans > 1:
                axis_num += 1
                map_scan_tests(axis_num, header, task)
            if task.constants.correct_for_polarization:
                axis_num += 1
                stokes_axis_tests(axis_num, header)

            # Timing header keys
            if task.constants.correct_for_polarization:
                assert header["CADENCE"] == 20 * num_meas
                assert header["XPOSURE"] == 30
            else:
                assert header["CADENCE"] == 10 * num_meas
                assert header["XPOSURE"] == 15

            # Other general tests
            general_header_tests(axis_num, header, task, arm_id)

            axis_flip_tests(original_headers, header, arm_id)


def sp_spatial_axis_correction_tests(
    axis_num: int, original_header: fits.Header, header: fits.Header
):
    # test that headers were actually updated
    if axis_num == 1:
        assert header[f"PC{axis_num}_1"] == 1.0
        assert header[f"PC{axis_num}_1A"] == 1.0
        assert header[f"PC{axis_num}_2"] == 0.0
        assert header[f"PC{axis_num}_2A"] == 0.0
        assert header[f"PC{axis_num}_3"] == 0.0
        assert header[f"PC{axis_num}_3A"] == 0.0
    elif axis_num == 2 or 3:
        assert header[f"PC{axis_num}_1"] == 0.0
        assert header[f"PC{axis_num}_1A"] == 0.0
        assert header[f"PC{axis_num}_2"] != original_header[f"PC{axis_num}_2"]
        assert header[f"PC{axis_num}_2A"] != original_header[f"PC{axis_num}_2A"]
        assert header[f"PC{axis_num}_3"] != original_header[f"PC{axis_num}_3"]
        assert header[f"PC{axis_num}_3A"] != original_header[f"PC{axis_num}_3A"]
        assert header[f"CRPIX{axis_num}"] != original_header[f"CRPIX{axis_num}"]
        assert header[f"CRPIX{axis_num}A"] != original_header[f"CRPIX{axis_num}A"]
        assert header[f"CDELT{axis_num}"] != original_header[f"CDELT{axis_num}"]
        assert header[f"CDELT{axis_num}A"] != original_header[f"CDELT{axis_num}A"]

    assert header["SLITORI"]


def ci_spatial_axis_correction_tests(
    axis_num: int, original_header: fits.Header, header: fits.Header
):
    if axis_num == 1 or 2:
        assert header[f"PC{axis_num}_1"] != original_header[f"PC{axis_num}_1"]
        assert header[f"PC{axis_num}_1A"] != original_header[f"PC{axis_num}_1A"]
        assert header[f"PC{axis_num}_2"] != original_header[f"PC{axis_num}_2"]
        assert header[f"PC{axis_num}_2A"] != original_header[f"PC{axis_num}_2A"]
        assert header[f"PC{axis_num}_3"] == 0
        assert header[f"PC{axis_num}_3A"] == 0
        assert header[f"CRPIX{axis_num}"] != original_header[f"CRPIX{axis_num}"]
        assert header[f"CRPIX{axis_num}A"] != original_header[f"CRPIX{axis_num}A"]
        assert header[f"CDELT{axis_num}"] != original_header[f"CDELT{axis_num}"]
        assert header[f"CDELT{axis_num}A"] != original_header[f"CDELT{axis_num}A"]

    if axis_num == 3:
        assert header[f"PC{axis_num}_1"] == 0
        assert header[f"PC{axis_num}_2"] == 0
        assert header[f"PC{axis_num}_3"] == 1
        assert header[f"PC{axis_num}_1A"] == 0
        assert header[f"PC{axis_num}_2A"] == 0
        assert header[f"PC{axis_num}_3A"] == 1

    assert header["SLITORI"]
    assert header["CNM1BOFF"] == 8.0
    assert header["CNM1OFF"] == -2.75


def sp_spectral_axis_correction_tests(original_headers: fits.Header, header: fits.Header):
    # CRPIX gets tested in `axis_flip_tests`
    assert header["CRVAL1"] != original_headers["CRVAL1"]
    assert header["CRVAL1A"] != original_headers["CRVAL1A"]
    assert header["CDELT1"] != original_headers["CDELT1"]
    assert header["CDELT1A"] != original_headers["CDELT1A"]
    assert header["CTYPE1"] == "AWAV-GRA"
    assert header["CUNIT1"] == "nm"
    assert header["CTYPE1A"] == "AWAV-GRA"
    assert header["CUNIT1A"] == "nm"
    assert "PV1_0" in header
    assert "PV1_2" in header
    assert "PV1_1" in header


def longitude_axis_tests(axis_num: int, header: fits.Header):
    assert header[f"DNAXIS{axis_num}"] == header[f"NAXIS{axis_num}"]
    assert header[f"DTYPE{axis_num}"] == "SPATIAL"
    assert header[f"DWNAME{axis_num}"] == "helioprojective longitude"
    assert header[f"DUNIT{axis_num}"] == header[f"CUNIT{axis_num}"]
    assert header[f"DPNAME{axis_num}"] == "detector y axis"


def spectral_axis_tests(axis_num: int, header: fits.Header):
    assert header[f"DNAXIS{axis_num}"] == header[f"NAXIS{axis_num}"]
    assert header[f"DTYPE{axis_num}"] == "SPECTRAL"
    assert header[f"DPNAME{axis_num}"] == "dispersion axis"
    assert header[f"DWNAME{axis_num}"] == "wavelength"
    assert header[f"DUNIT{axis_num}"] == header[f"CUNIT{axis_num}"]


def latitude_axis_tests(axis_num: int, arm_id: str, header: fits.Header):
    if arm_id == "CI":
        latitude_dp_name = "detector x axis"
    else:
        latitude_dp_name = "spatial along slit"
    assert header[f"DNAXIS{axis_num}"] == header[f"NAXIS{axis_num}"]
    assert header[f"DTYPE{axis_num}"] == "SPATIAL"
    assert header[f"DPNAME{axis_num}"] == latitude_dp_name
    assert header[f"DWNAME{axis_num}"] == "helioprojective latitude"
    assert header[f"DUNIT{axis_num}"] == header[f"CUNIT{axis_num}"]


def measurement_axis_tests(axis_num: int, header: fits.Header, task: CryonirspWriteL1Frame):
    assert header[f"DNAXIS{axis_num}"] == task.constants.num_meas
    assert header[f"DTYPE{axis_num}"] == "TEMPORAL"
    assert header[f"DPNAME{axis_num}"] == "measurement number"
    assert header[f"DWNAME{axis_num}"] == "time"
    assert header[f"DUNIT{axis_num}"] == "s"
    assert header[f"DINDEX{axis_num}"] == header["CNCMEAS"]


def scan_step_axis_tests(
    axis_num: int, arm_id: str, header: fits.Header, task: CryonirspWriteL1Frame
):
    if arm_id == "CI":
        scan_step_value = "TEMPORAL"
        scan_step_dwname = "time"
        scan_step_dunit = "s"
    else:
        scan_step_value = "SPATIAL"
        scan_step_dwname = "helioprojective longitude"
        scan_step_dunit = header[f"CUNIT3"]

    assert header[f"DNAXIS{axis_num}"] == task.constants.num_scan_steps
    assert header[f"DTYPE{axis_num}"] == scan_step_value
    assert header[f"DPNAME{axis_num}"] == "scan step number"
    assert header[f"DWNAME{axis_num}"] == scan_step_dwname
    assert header[f"DUNIT{axis_num}"] == scan_step_dunit


def map_scan_tests(axis_num: int, header: fits.Header, task: CryonirspWriteL1Frame):
    assert header["CNNMAPS"] == task.constants.num_map_scans
    assert header[f"DNAXIS{axis_num}"] == task.constants.num_map_scans
    assert header[f"DTYPE{axis_num}"] == "TEMPORAL"
    assert header[f"DPNAME{axis_num}"] == "map scan number"
    assert header[f"DWNAME{axis_num}"] == "time"
    assert header[f"DUNIT{axis_num}"] == "s"
    assert header[f"DINDEX{axis_num}"] == header["CNMAP"]


def stokes_axis_tests(axis_num: int, header: fits.Header):
    assert header[f"DNAXIS{axis_num}"] == 4
    assert header[f"DTYPE{axis_num}"] == "STOKES"
    assert header[f"DPNAME{axis_num}"] == "polarization state"
    assert header[f"DWNAME{axis_num}"] == "polarization state"
    assert header[f"DUNIT{axis_num}"] == ""
    assert header[f"DINDEX{axis_num}"] in range(1, 5)


def axis_flip_tests(original_header: fits.Header, header: fits.Header, arm_id: str):
    if arm_id == "SP":
        axis_length = original_header["NAXIS1"]
        ref_pix = original_header["CRPIX1"]
        assert header["CDELT1"] > 0
        assert header["CRPIX1"] == axis_length - ref_pix
    if arm_id == "CI":
        pass


def preserve_date_tests(output_files: list[Path], calibrated_files: list[Path]) -> None:
    # Make sure we didn't overwrite pre-computed DATE-BEG and DATE-END keys
    cal_headers = [fits.getheader(f) for f in calibrated_files]
    output_headers = [fits.getheader(f, ext=1) for f in output_files]

    assert sorted([h["DATE-BEG"] for h in cal_headers]) == sorted(
        [h["DATE-BEG"] for h in output_headers]
    )
    assert sorted([h["DATE-END"] for h in cal_headers]) == sorted(
        [h["DATE-END"] for h in output_headers]
    )


def general_header_tests(
    axis_num: int,
    header: fits.Header,
    task: CryonirspWriteL1Frame,
    arm_id: str,
):
    # Other general tests
    assert header["DAAXES"] == 2
    assert header["DNAXIS"] == axis_num
    assert header["DEAXES"] == axis_num - 2
    assert f"DNAXIS{axis_num + 1}" not in header

    assert header["INFO_URL"] == task.docs_base_url
    assert header["HEADVERS"] == spec_version
    assert header["HEAD_URL"] == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
    calvers = task.version_from_module_name()
    assert header["CALVERS"] == calvers
    assert (
        header["CAL_URL"]
        == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
    )
    date_avg = (
        (Time(header["DATE-END"], precision=6) - Time(header["DATE-BEG"], precision=6)) / 2
        + Time(header["DATE-BEG"], precision=6)
    ).isot
    assert header["DATE-AVG"] == date_avg
    assert isinstance(header["HLSVERS"], str)
    assert header["BUNIT"] == ""
    assert header.comments["BUNIT"] == "Values are relative to disk center. See calibration docs."
