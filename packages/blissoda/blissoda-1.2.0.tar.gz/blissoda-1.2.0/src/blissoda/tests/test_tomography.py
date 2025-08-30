import pydantic
import pytest

from ..tomo.tomo_model import TomoProcessorModel


@pytest.fixture
def valid_model():
    model = TomoProcessorModel()
    return model


def test_valid_model_initialization(valid_model):
    assert valid_model.workflow == "tomo_processor.json"
    assert valid_model.queue is None
    assert valid_model.nabu_config_file is None
    assert valid_model.slice_index == "middle"
    assert valid_model.rotation_axis_position == "sliding-window"
    assert valid_model.phase_retrieval_method == "None"
    assert valid_model.delta_beta == "100"


def test_valid_model_assignment(valid_model):
    valid_model.queue = "my_queue"
    assert valid_model.queue == "my_queue"

    valid_model.slice_index = "first"
    assert valid_model.slice_index == "first"

    valid_model.slice_index = 2
    assert valid_model.slice_index == "2"

    valid_model.rotation_axis_position = 3.14
    assert valid_model.rotation_axis_position == 3.14

    valid_model.phase_retrieval_method = "CTF"
    assert valid_model.phase_retrieval_method == "CTF"

    valid_model.delta_beta = 100
    assert valid_model.delta_beta == "100"


def test_invalid_workflow_assignment(valid_model):
    with pytest.raises(ValueError):
        valid_model.workflow = "invalid.txt"

    with pytest.raises(ValueError):
        valid_model.workflow = 123

    with pytest.raises(FileNotFoundError):
        valid_model.workflow = "nonexistent.json"


def test_invalid_queue_assignment(valid_model):
    with pytest.raises(ValueError):
        valid_model.queue = 123

    with pytest.raises(ValueError):
        valid_model.queue = [1, 2, 3]


def test_invalid_nabu_config_file_assignment(tmp_path, valid_model):
    # Point to a file that doesn't exist
    missing_file = tmp_path / "missing.yml"
    with pytest.raises(FileNotFoundError):
        valid_model.nabu_config_file = str(missing_file)

    with pytest.raises(ValueError):
        valid_model.nabu_config_file = 123


def test_invalid_slice_index_assignment(valid_model):
    with pytest.raises(ValueError):
        valid_model.slice_index = "wrong"

    with pytest.raises(ValueError):
        valid_model.slice_index = 4.5


def test_invalid_rotation_axis_position_assignment(valid_model):
    with pytest.raises(ValueError):
        valid_model.rotation_axis_position = "invalid-method"

    with pytest.raises(ValueError):
        valid_model.rotation_axis_position = [1, 2, 3]


def test_invalid_phase_retrieval_method_assignment(valid_model):
    with pytest.raises(ValueError):
        valid_model.phase_retrieval_method = "wrong"

    with pytest.raises(ValueError):
        valid_model.phase_retrieval_method = 123


def test_invalid_delta_beta_assignment(valid_model):
    with pytest.raises(ValueError, match="delta_beta must be positive"):
        valid_model.delta_beta = -5

    with pytest.raises(ValueError):
        valid_model.delta_beta = "0"

    with pytest.raises(ValueError):
        valid_model.delta_beta = "invalid"


def test_show_last_slice(valid_model):
    assert valid_model.show_last_slice is False
    valid_model.show_last_slice = True
    assert valid_model.show_last_slice is True

    with pytest.raises(pydantic.ValidationError):
        valid_model.show_last_slice = 123

    with pytest.raises(pydantic.ValidationError):
        valid_model.show_last_slice = "wrong_type"
