"""
Tests for the tasks defined in this repo
"""

import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from datetime import datetime
from datetime import timedelta
from itertools import chain
from random import randint
from uuid import uuid4

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator import spec122_validator
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.codecs.json import json_encoder
from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.constants import ConstantsBase
from dkist_processing_common.models.input_dataset import InputDatasetFilePointer
from dkist_processing_common.models.input_dataset import InputDatasetObject
from dkist_processing_common.models.input_dataset import InputDatasetParameter
from dkist_processing_common.models.input_dataset import InputDatasetParameterValue
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client
from dkist_service_configuration.logging import logger

from dkist_processing_test.models.parameters import TestParameters
from dkist_processing_test.tasks import ParseL0TestInputData
from dkist_processing_test.tasks import TestQualityL0Metrics
from dkist_processing_test.tasks.exercise_numba import ExerciseNumba
from dkist_processing_test.tasks.fail import FailTask
from dkist_processing_test.tasks.fake_science import GenerateCalibratedData
from dkist_processing_test.tasks.movie import AssembleTestMovie
from dkist_processing_test.tasks.movie import MakeTestMovieFrames
from dkist_processing_test.tasks.noop import NoOpTask
from dkist_processing_test.tasks.write_l1 import WriteL1Data
from dkist_processing_test.tests.conftest import S122Headers
from dkist_processing_test.tests.conftest import generate_214_l0_fits_frame


@dataclass
class FakeConstantDb:
    NUM_DSPS_REPEATS: int = 2
    OBS_IP_START_TIME: str = "1990-06-12T12:00:00"
    INSTRUMENT: str = "TEST"
    AVERAGE_CADENCE: float = 10.0
    MINIMUM_CADENCE: float = 10.0
    MAXIMUM_CADENCE: float = 10.0
    VARIANCE_CADENCE: float = 0.0
    STOKES_PARAMS: tuple[str] = (
        "I",
        "Q",
        "U",
        "V",
    )  # A tuple because lists aren't allowed on dataclasses
    CONTRIBUTING_PROPOSAL_IDS: tuple[str] = ("abc", "def")
    CONTRIBUTING_EXPERIMENT_IDS: tuple[str] = ("ghi", "jkl")


@pytest.fixture()
def noop_task():
    return NoOpTask(recipe_run_id=1, workflow_name="noop", workflow_version="VX.Y")


def test_noop_task(noop_task):
    """
    Given: A NoOpTask
    When: Calling the task instance
    Then: No errors raised
    """
    noop_task()


@pytest.fixture()
def fail_task():
    return FailTask(recipe_run_id=1, workflow_name="fail", workflow_version="VX.Y")


def test_fail_task(fail_task):
    """
    Given: A FailTask
    When: Calling the task instance
    Then: Runtime Error raised
    """
    with pytest.raises(RuntimeError):
        fail_task()


@pytest.fixture()
def generate_calibrated_data_task(
    tmp_path,
    recipe_run_id,
    assign_input_dataset_doc_to_task,
    link_constants_db,
    array_parameter_file_object_key,
    random_parameter_hdulist,
    early_json_parameter_file_object_key,
    early_file_message_str,
    late_json_parameter_file_object_key,
    late_file_message_str,
    early_or_late,
    late_date,
):
    number_of_frames = 10
    if early_or_late == "early":
        obs_ip_start_time_str = (datetime.fromisoformat(late_date) - timedelta(days=30)).isoformat()
    elif early_or_late == "late":
        obs_ip_start_time_str = (datetime.fromisoformat(late_date) + timedelta(days=30)).isoformat()
    link_constants_db(
        recipe_run_id=recipe_run_id,
        constants_obj=FakeConstantDb(
            NUM_DSPS_REPEATS=number_of_frames, OBS_IP_START_TIME=obs_ip_start_time_str
        ),
    )
    with GenerateCalibratedData(
        recipe_run_id=recipe_run_id, workflow_name="GenerateCalibratedData", workflow_version="VX.Y"
    ) as task:
        # configure input data
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        input_frame_set = Spec122Dataset(
            instrument="vbi",
            dataset_shape=(number_of_frames, 512, 512),
            array_shape=(1, 512, 512),
            time_delta=10,
        )
        # load input data
        for idx, input_frame in enumerate(input_frame_set):
            hdu = input_frame.hdu()
            hdu.data = (
                np.ones(hdu.data.shape, dtype=int) * 10
            )  # Because input data will be ints in test system
            hdu.header["DSPSNUM"] = 1
            hdul = fits.HDUList([hdu])
            file_name = f"input_{idx}.fits"
            task.write(
                data=hdul, tags=Tag.input(), relative_path=file_name, encoder=fits_hdulist_encoder
            )

        # Write parameter files
        hdul, _, _, _ = random_parameter_hdulist
        task.write(
            data=hdul,
            tags=Tag.parameter(array_parameter_file_object_key),
            encoder=fits_hdulist_encoder,
        )
        task.write(
            data=early_file_message_str,
            tags=Tag.parameter(early_json_parameter_file_object_key),
            encoder=json_encoder,
        )
        task.write(
            data=late_file_message_str,
            tags=Tag.parameter(late_json_parameter_file_object_key),
            encoder=json_encoder,
        )

        # This needs to be after we've written and tagged the parameter files
        assign_input_dataset_doc_to_task(task, obs_ip_start_time=task.constants.obs_ip_start_time)

        # result
        yield task, number_of_frames
        # teardown
        task._purge()
    # disconnect


@pytest.fixture(scope="session")
def array_file_parameter(
    random_parameter_hdulist, array_parameter_file_object_key
) -> tuple[list[InputDatasetParameterValue], float, float, float]:
    hdul, mu, std, const = random_parameter_hdulist

    parameter_array_file_values = [
        InputDatasetParameterValue(
            parameterValueId=randint(1000, 2000),
            parameterValue=InputDatasetFilePointer(
                file_pointer=InputDatasetObject(
                    objectKey=array_parameter_file_object_key,
                    bucket="not_used",
                    tag=Tag.parameter(array_parameter_file_object_key),
                )
            ).model_dump_json(),
            parameterValueStartDate=datetime(1946, 11, 20),
        )
    ]
    return parameter_array_file_values, mu, std, const


@pytest.fixture(scope="session")
def wavelength_parameter() -> list[InputDatasetParameterValue]:
    value = {"wavelength": (1.0, 2.0, 3.0), "values": ("one", "two", "three")}

    parameter_value = [
        InputDatasetParameterValue(
            parameter_value_id=randint(1000, 2000),
            parameter_value=json.dumps(value),
            parameter_value_start_date=datetime(1946, 11, 20),
        )
    ]
    return parameter_value


@pytest.fixture(scope="session")
def message_parameters(
    early_value_message_str, late_value_message_str, early_date, late_date
) -> list[InputDatasetParameterValue]:
    parameter_values = [
        InputDatasetParameterValue(
            parameterValueId=randint(1000, 2000),
            parameterValue=json.dumps(early_value_message_str),
            parameterValueStartDate=early_date,
        ),
        InputDatasetParameterValue(
            parameterValueId=randint(1000, 2000),
            parameterValue=json.dumps(late_value_message_str),
            parameterValueStartDate=late_date,
        ),
    ]
    return parameter_values


@pytest.fixture(scope="session")
def message_file_parameters(
    early_json_parameter_file_object_key, late_json_parameter_file_object_key, early_date, late_date
) -> list[InputDatasetParameterValue]:
    parameter_values = [
        InputDatasetParameterValue(
            parameterValueId=randint(1000, 2000),
            parameterValue=InputDatasetFilePointer(
                file_pointer=InputDatasetObject(
                    objectKey=early_json_parameter_file_object_key,
                    bucket="not_used",
                    tag=Tag.parameter(early_json_parameter_file_object_key),
                )
            ).model_dump_json(),
            parameterValueStartDate=early_date,
        ),
        InputDatasetParameterValue(
            parameterValueId=randint(1000, 2000),
            parameterValue=InputDatasetFilePointer(
                file_pointer=InputDatasetObject(
                    objectKey=late_json_parameter_file_object_key,
                    bucket="not_used",
                    tag=Tag.parameter(late_json_parameter_file_object_key),
                )
            ).model_dump_json(),
            parameterValueStartDate=late_date,
        ),
    ]
    return parameter_values


@pytest.fixture(scope="session")
def input_dataset_document_parameters_part_basemodel(
    array_file_parameter,
    wavelength_parameter,
    message_parameters,
    message_file_parameters,
):
    parameter_array_file_values, _, _, _ = array_file_parameter

    parameter_wavelength_values = wavelength_parameter

    parameter_message_values = message_parameters

    parameter_file_values = message_file_parameters

    parameters_obj = InputDatasetPartDocumentList(
        doc_list=[
            InputDatasetParameter(
                parameter_name="test_random_data", parameter_values=parameter_array_file_values
            ),
            InputDatasetParameter(
                parameter_name="test_wavelength_category",
                parameter_values=parameter_wavelength_values,
            ),
            InputDatasetParameter(
                parameter_name="test_message", parameter_values=parameter_message_values
            ),
            InputDatasetParameter(
                parameter_name="test_message_file", parameter_values=parameter_file_values
            ),
        ]
    )

    return parameters_obj


@pytest.fixture(scope="session")
def assign_input_dataset_doc_to_task(
    input_dataset_document_parameters_part_basemodel,
):
    def update_task(task, obs_ip_start_time=None):
        task.write(
            data=input_dataset_document_parameters_part_basemodel,
            tags=Tag.input_dataset_parameters(),
            encoder=basemodel_encoder,
        )
        task.parameters = TestParameters(
            scratch=task.scratch, wavelength=2.0, obs_ip_start_time=obs_ip_start_time
        )

    return update_task


@pytest.mark.parametrize("early_or_late", [pytest.param("early")])
def test_generate_calibrated_data_parameters(
    generate_calibrated_data_task,
    array_file_parameter,
    early_file_message_str,
    early_value_message_str,
    early_or_late,
):
    """
    Given: A GenerateCalibratedData task
    When: Accessing the task's parameters
    Then: The correct values are returned
    """
    task, _ = generate_calibrated_data_task
    _, mu, std, const = array_file_parameter

    assert type(task.parameters.randomness) is tuple
    np.testing.assert_allclose(np.array(task.parameters.randomness), np.array([mu, std]), rtol=1)

    assert task.parameters.constant == const
    assert task.parameters.wavelength_category == "two"
    assert task.parameters.value_message == early_value_message_str
    assert task.parameters.file_message == early_file_message_str


@pytest.fixture
def link_constants_db():
    return constants_linker


def constants_linker(recipe_run_id: int, constants_obj):
    """Take a dataclass (or dict) containing a constants DB and link it to a specific recipe run id."""
    if is_dataclass(constants_obj):
        constants_obj = asdict(constants_obj)
    constants = ConstantsBase(recipe_run_id=recipe_run_id, task_name="test")
    constants._purge()
    constants._update(constants_obj)
    return


@pytest.mark.parametrize("early_or_late", [pytest.param("early"), pytest.param("late")])
def test_generate_calibrated_data(
    generate_calibrated_data_task,
    early_file_message_str,
    late_file_message_str,
    early_value_message_str,
    late_value_message_str,
    early_or_late,
    mocker,
    fake_gql_client,
):
    """
    Given: A GenerateCalibratedData task
    When: Calling the task instance
    Then: Output files are generated for each input file with appropriate tags
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, number_of_frames = generate_calibrated_data_task
    task()
    # Then
    calibrated_frame_hdus = list(
        task.read(tags=[Tag.calibrated(), Tag.frame()], decoder=fits_hdu_decoder)
    )

    if early_or_late == "early":
        expected_file_message = early_file_message_str
        expected_value_message = early_value_message_str
    elif early_or_late == "late":
        expected_file_message = late_file_message_str
        expected_value_message = late_value_message_str

    # Verify frames
    assert len(calibrated_frame_hdus) == number_of_frames
    for hdu in calibrated_frame_hdus:
        assert "VBINMOSC" in hdu.header
        assert "VBICMOSC" in hdu.header

        # Verify correct date params were used
        assert hdu.header["CAM_ID"] == expected_file_message
        assert hdu.header["CAMERA"] == expected_value_message

    # Verify debug frame was written
    debug_frame_paths = list(task.read(tags=[Tag.debug(), Tag.frame()]))
    assert len(debug_frame_paths) == 1
    assert debug_frame_paths[0].exists()


class CommonDataset(Spec122Dataset):
    # NOTE: We use ViSP data for unit tests because ViSP can be polarimetric
    # **BUT** in actual integration tests `*-procesing-test` processes VBI data
    def __init__(
        self,
        task_type: str = "observe",
        num_dsps_repeats: int = 1,
        num_files: int = 2,
        start_datetime: datetime = datetime(2020, 1, 1, 0, 0, 0),
    ):
        array_shape = (1, 10, 10)
        dataset_shape = (num_files,) + array_shape[1:]
        super().__init__(
            array_shape=array_shape,
            time_delta=1,
            dataset_shape=dataset_shape,
            instrument="visp",
            start_time=start_datetime,
        )

        self.add_constant_key("TELEVATN", 6.28)
        self.add_constant_key("TAZIMUTH", 3.14)
        self.add_constant_key("TTBLANGL", 1.23)
        self.add_constant_key("VISP_012", "bar")
        self.add_constant_key("DKIST004", task_type)
        self.add_constant_key("ID___005", "ip id")
        self.add_constant_key("PAC__004", "Sapphire Polarizer")
        self.add_constant_key("PAC__005", "31.2")
        self.add_constant_key("PAC__006", "clear")
        self.add_constant_key("PAC__007", "6.66")
        self.add_constant_key("PAC__008", "DarkShutter")
        self.add_constant_key("INSTRUME", "VISP")
        self.add_constant_key("WAVELNTH", 1080.0)
        self.add_constant_key("DATE-OBS", "2020-01-02T00:00:00.000")
        self.add_constant_key("DATE-END", "2020-01-03T00:00:00.000")
        self.add_constant_key("ID___012", "EXPERIMENT_ID1")
        self.add_constant_key("ID___013", "PROPOSAL_ID1")
        self.add_constant_key("PAC__002", "clear")
        self.add_constant_key("PAC__003", "on")
        self.add_constant_key("TELSCAN", "Raster")
        self.add_constant_key("DKIST008", num_dsps_repeats)
        self.add_constant_key("BZERO", 0)
        self.add_constant_key("BSCALE", 1)

        # Because these test data are from "ViSP" we need to add these keys,
        # which would normally be added by the `*-processing-visp` science task (although they are not
        # added by the `*-processing-test` science task because Test calibrates VBI data in integration tests
        self.add_constant_key("VSPMAP", 1)
        self.add_constant_key("VSPNMAPS", 2)

    @key_function("DKIST009")
    def current_dsps_repeat(self, key: str) -> int:
        """Current DSPS repeat number."""
        return self.index


@pytest.fixture()
def complete_common_header():
    """
    A header with some common by-frame keywords
    """
    # Taken from dkist-processing-common
    ds = CommonDataset()
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    return header_list[0]


@pytest.fixture(scope="function")
def parse_inputs_task_no_data(tmp_path, recipe_run_id):
    with ParseL0TestInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="test_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:

        yield task
        task._purge()


def test_parse_task(parse_inputs_task_no_data, tmp_path, recipe_run_id):
    """
    Given: A `ParseL0TestInputData` task with observe and non-observe INPUT data frames
    When: Parsing the input data
    Then: The correct constants and tags are applied
    """
    num_dsps_repeats = 3
    start_datetime = datetime(1988, 7, 2)
    num_non_obs_files = 2
    task = parse_inputs_task_no_data

    task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
    obs_ds = CommonDataset(
        task_type="observe",
        num_dsps_repeats=num_dsps_repeats,
        num_files=num_dsps_repeats,
        start_datetime=start_datetime,
    )
    non_obs_ds = CommonDataset(task_type="not_observe", num_files=num_non_obs_files)
    ds = chain(obs_ds, non_obs_ds)
    header_generator = (d.header() for d in ds)
    for header in header_generator:
        hdul = generate_214_l0_fits_frame(s122_header=header)
        task.write(data=hdul, tags=[Tag.input(), Tag.frame()], encoder=fits_hdulist_encoder)

    task()

    assert task.constants._db_dict[BudName.instrument.value] == "VISP"
    assert task.constants._db_dict[BudName.num_dsps_repeats.value] == num_dsps_repeats
    assert task.constants._db_dict[BudName.obs_ip_start_time] == start_datetime.isoformat()

    assert (
        task.count(tags=[Tag.input(), Tag.frame(), Tag.task(TaskName.observe.value)])
        == num_dsps_repeats
    )
    assert task.count(tags=[Tag.input(), Tag.frame(), Tag.task("not_observe")]) == num_non_obs_files
    for dsps in range(num_dsps_repeats):
        assert (
            task.count(
                tags=[
                    Tag.input(),
                    Tag.frame(),
                    Tag.task(TaskName.observe.value),
                    Tag.dsps_repeat(dsps),
                ]
            )
            == 1
        )
        assert (
            task.count(
                tags=[Tag.input(), Tag.frame(), Tag.task("not_observe"), Tag.dsps_repeat(dsps)]
            )
            == 0
        )


def test_parse_picky_bud(parse_inputs_task_no_data, tmp_path, recipe_run_id):
    """
    Given: A `ParseL0TestInputData` task with data that will trigger an error in the `PickyBud` assigned to that task
    When: Parsing the input data
    Then: The correct error is raised
    """
    task = parse_inputs_task_no_data
    task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
    ds = CommonDataset(task_type="bad value")
    header_generator = (d.header() for d in ds)
    for header in header_generator:
        hdul = generate_214_l0_fits_frame(s122_header=header)
        task.write(data=hdul, tags=[Tag.input(), Tag.frame()], encoder=fits_hdulist_encoder)

    with pytest.raises(ValueError, match="This task type is bad!"):
        task()


@pytest.fixture(scope="function", params=[1, 4])
def write_l1_task(complete_common_header, request):
    with WriteL1Data(
        recipe_run_id=randint(0, 99999),
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        num_of_stokes_params = request.param
        stokes_params = ["I", "Q", "U", "V"]

        # Make sure polarimetric header validation happens correctly
        if num_of_stokes_params == 4:
            complete_common_header["VSPPOLMD"] = "observe_polarimetric"
            complete_common_header["POL_NOIS"] = 0.1
            complete_common_header["POL_SENS"] = 0.2
        else:
            complete_common_header["VSPPOLMD"] = "observe_intensity"

        hdu = fits.PrimaryHDU(
            data=np.random.random(size=(1, 128, 128)) * 10, header=complete_common_header
        )
        logger.info(f"{num_of_stokes_params=}")
        hdul = fits.HDUList([hdu])
        for i in range(num_of_stokes_params):
            task.write(
                data=hdul,
                tags=[Tag.calibrated(), Tag.frame(), Tag.stokes(stokes_params[i])],
                encoder=fits_hdulist_encoder,
            )
        task.constants._update(
            asdict(
                FakeConstantDb(
                    AVERAGE_CADENCE=10,
                    MINIMUM_CADENCE=10,
                    MAXIMUM_CADENCE=10,
                    VARIANCE_CADENCE=0,
                    INSTRUMENT="TEST",
                )
            )
        )
        yield task, num_of_stokes_params
        task._purge()


def test_write_l1_task(write_l1_task, mocker, fake_gql_client):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_of_stokes_params = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    logger.info(f"{files=}")
    assert len(files) == num_of_stokes_params
    for file in files:
        logger.info(f"Checking file {file}")
        assert file.exists


class BaseSpec214l0Dataset(Spec122Dataset):
    def __init__(self, num_tasks: int, instrument: str = "vbi"):
        super().__init__(
            dataset_shape=(num_tasks, 4, 4),
            array_shape=(1, 4, 4),
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )

    @property
    def data(self):
        return np.ones(shape=self.array_shape)


@pytest.fixture()
def test_l0_quality_metrics_task_class(quality_l0_task_types):
    # Just to override `quality_task_types` to make testing more precise
    class TestingL0QualityMetrics(TestQualityL0Metrics):
        @property
        def quality_task_types(self) -> list[str]:
            return quality_l0_task_types

    return TestingL0QualityMetrics


@pytest.fixture(params=[pytest.param(1, id="no_modstates"), pytest.param(4, id="with_modstates")])
def num_modstates(request):
    return request.param


@pytest.fixture()
def quality_l0_task_types() -> list[str]:
    # The tasks types we want to build l0 metrics for
    return [TaskName.lamp_gain.value, TaskName.dark.value]


@pytest.fixture()
def dataset_task_types(quality_l0_task_types) -> list[str]:
    # The task types that exist in the dataset. I.e., a larger set than we want to build metrics for.
    return quality_l0_task_types + [TaskName.solar_gain.value, TaskName.observe.value]


@pytest.fixture()
def quality_l0_task(
    test_l0_quality_metrics_task_class,
    tmp_path,
    num_modstates,
    dataset_task_types,
    link_constants_db,
    recipe_run_id,
):
    link_constants_db(
        recipe_run_id=recipe_run_id, constants_obj={BudName.num_modstates.value: num_modstates}
    )
    with test_l0_quality_metrics_task_class(
        recipe_run_id=recipe_run_id, workflow_name="TestTasks", workflow_version="vX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        ds = BaseSpec214l0Dataset(num_tasks=len(dataset_task_types) * num_modstates)
        for modstate in range(1, num_modstates + 1):
            for frame, task_type in zip(ds, dataset_task_types):
                hdu = frame.hdu()
                hdul = fits.HDUList([hdu])
                task.write(
                    data=hdul,
                    tags=[Tag.input(), Tag.task(task_type), Tag.modstate(modstate)],
                    encoder=fits_hdulist_encoder,
                )

        yield task
        task._purge()


def test_quality_l0_metrics(quality_l0_task, quality_l0_task_types, num_modstates):
    """
    Given: A sublcassed `QualityL0Metrics` task and some data frames
    When: Running the task
    Then: The correct metrics are produced
    """
    task = quality_l0_task
    task()

    task_metric_names = ["FRAME_RMS", "FRAME_AVERAGE"]

    for modstate in range(1, num_modstates + 1):
        for metric_name in task_metric_names:
            for task_type in quality_l0_task_types:
                tags = [Tag.quality(metric_name), Tag.quality_task(task_type)]
                if num_modstates > 1:
                    tags.append(Tag.modstate(modstate))
                files = list(task.read(tags=tags))
                assert files  # there are some
                for file in files:
                    with file.open() as f:
                        data = json.load(f)
                        assert isinstance(data, dict)
                        assert data["x_values"]
                        assert data["y_values"]
                        assert all(isinstance(item, str) for item in data["x_values"])
                        assert all(isinstance(item, float) for item in data["y_values"])
                        assert len(data["x_values"]) == len(data["y_values"])

    global_metric_names = ["DATASET_AVERAGE", "DATASET_RMS"]
    for metric_name in global_metric_names:
        files = list(task.read(tags=[Tag.quality(metric_name)]))
        assert files
        for file in files:
            with file.open() as f:
                data = json.load(f)
                assert isinstance(data, dict)


def test_quality_l0_metrics_task_integration_run(recipe_run_id):
    """
    Given: A base `TestQualityL0Metrics` task with no constants or data
    When: Running the task
    Then: No error is raised
    """
    # I.e., this tests that the fixturization needed to get good testing on the quality L0 task aren't hiding
    # an inability to run in integration tests where the setup is much more minimal
    task = TestQualityL0Metrics(
        recipe_run_id=recipe_run_id, workflow_name="integration-style", workflow_version="vX.Y"
    )
    task()


@pytest.fixture()
def make_movie_frames_task(tmp_path, recipe_run_id):
    with MakeTestMovieFrames(
        recipe_run_id=recipe_run_id, workflow_name="MakeMovieFrames", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.testing_num_dsps_repeats = 10
        task.num_steps = 1
        task.num_exp_per_step = 1
        task.constants._update(
            asdict(FakeConstantDb(NUM_DSPS_REPEATS=task.testing_num_dsps_repeats))
        )
        ds = S122Headers(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for d, header in enumerate(header_generator):
            data = np.ones((1, 10, 10))
            data[:, : d * 10, :] = 0.0
            hdl = generate_214_l0_fits_frame(data=data, s122_header=header)
            task.write(
                data=hdl,
                tags=[
                    Tag.calibrated(),
                    Tag.dsps_repeat(d + 1),
                ],
                encoder=fits_hdulist_encoder,
            )
        yield task
        task._purge()


def test_make_movie_frames_task(make_movie_frames_task, mocker, fake_gql_client):
    """
    :Given: a make_movie_frames_task task
    :When: running the task
    :Then: no errors are raised and a movie file is created
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = make_movie_frames_task
    task()
    movie_frames = list(task.read(tags=[Tag.movie_frame()]))
    logger.info(f"{movie_frames=}")
    assert len(movie_frames) == task.testing_num_dsps_repeats
    for frame in movie_frames:
        assert frame.exists()
        hdul = fits.open(frame)
        assert len(hdul[0].data.shape) == 2


@pytest.fixture()
def assemble_test_movie_task(tmp_path, recipe_run_id):
    with AssembleTestMovie(
        recipe_run_id=recipe_run_id, workflow_name="AssembleTestMovie", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path)
        task.testing_num_dsps_repeats = 10
        task.num_steps = 1
        task.num_exp_per_step = 1
        task.constants._update(
            asdict(FakeConstantDb(NUM_DSPS_REPEATS=task.testing_num_dsps_repeats))
        )
        ds = S122Headers(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for d, header in enumerate(header_generator):
            data = np.ones((10, 10))
            data[: d * 10, :] = 0.0
            hdl = generate_214_l0_fits_frame(data=data, s122_header=header)
            task.write(
                data=hdl,
                tags=[
                    Tag.movie_frame(),
                    Tag.dsps_repeat(d + 1),
                ],
                encoder=fits_hdulist_encoder,
            )
        yield task
        task._purge()


def test_assemble_test_movie_task(assemble_test_movie_task, mocker, fake_gql_client):
    """
    :Given: an assemble_test_movie task
    :When: running the task
    :Then: no errors are raised and a movie file is created
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = assemble_test_movie_task
    task()
    movie_file = list(task.read(tags=[Tag.movie()]))
    logger.info(f"{movie_file=}")
    assert len(movie_file) == 1
    assert movie_file[0].exists()


@pytest.fixture
def trial_output_task(recipe_run_id, tmp_path, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient",
        new=fake_gql_client,
    )
    proposal_id = "test_proposal_id"
    with TransferTrialData(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(
            recipe_run_id=recipe_run_id,
            scratch_base_path=tmp_path,
        )
        task.constants._update({"PROPOSAL_ID": proposal_id})

        file_count = 0
        # Write a debug frame
        debug_file_obj = uuid4().hex.encode("utf8")
        task.write(debug_file_obj, tags=[Tag.debug(), Tag.frame()])
        file_count += 1

        # Write an intermediate frame
        intermediate_file_obj = uuid4().hex.encode("utf8")
        task.write(
            intermediate_file_obj,
            tags=[Tag.intermediate(), Tag.frame(), Tag.task("DUMMY")],
        )
        file_count += 1

        # An output frame
        output_file_obj = uuid4().hex.encode("utf8")
        task.write(output_file_obj, tags=[Tag.output(), Tag.frame()])
        file_count += 1

        # Output dataset inventory
        dsi_file_obj = uuid4().hex.encode("utf8")
        task.write(dsi_file_obj, tags=[Tag.output(), Tag.dataset_inventory()])
        file_count += 1

        # Output asdf
        asdf_file_obj = uuid4().hex.encode("utf8")
        task.write(asdf_file_obj, tags=[Tag.output(), Tag.asdf()])
        file_count += 1

        # Output movie
        movie_file_obj = uuid4().hex.encode("utf8")
        task.write(movie_file_obj, tags=[Tag.output(), Tag.movie()])
        file_count += 1

        # Output quality data
        quality_data_file_obj = uuid4().hex.encode("utf8")
        task.write(quality_data_file_obj, tags=Tag.quality_data())
        file_count += 1

        # Output quality report
        quality_report_file_obj = uuid4().hex.encode("utf8")
        task.write(quality_report_file_obj, tags=[Tag.output(), Tag.quality_report()])
        file_count += 1

        # This one won't get transferred
        task.write(uuid4().hex.encode("utf8"), tags=[Tag.frame(), "FOO"])

        yield task, file_count
        task._purge()


def test_transfer_test_trial_data(trial_output_task, mocker):
    """
    Given: A TransferTrialData task with associated frames
    When: Running the task and building the transfer list
    Then: No errors occur and the transfer list has the correct number of items
    """
    task, expected_num_items = trial_output_task

    mocker.patch(
        "dkist_processing_common.tasks.mixin.globus.GlobusMixin.globus_transfer_scratch_to_object_store"
    )
    mocker.patch(
        "dkist_processing_common.tasks.trial_output_data.TransferTrialData.remove_folder_objects"
    )

    # Just make sure the thing runs with no errors
    task()

    transfer_list = task.build_transfer_list()
    assert len(transfer_list) == expected_num_items


@pytest.fixture()
def exercise_numba_task(recipe_run_id):
    with ExerciseNumba(
        recipe_run_id=recipe_run_id, workflow_name="ExerciseNumba", workflow_version="VX.Y"
    ) as task:
        yield task


def test_exercise_numba_task(exercise_numba_task):
    """
    :Given: an exercise_numba task
    :When: running the task
    :Then: the numba module can be loaded and simple method using numba is executed
    """
    original = np.linspace(0.0, 10.0, 1001)
    task = exercise_numba_task
    task()
    assert task.speedup > 1.0
    assert np.all(np.equal(original, task.sorted_array))
