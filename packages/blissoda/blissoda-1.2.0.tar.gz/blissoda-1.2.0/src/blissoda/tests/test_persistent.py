import numpy
import pytest

try:
    from ..persistent.ordereddict import PersistentOrderedDict
except TypeError:
    # bliss not installed
    PersistentOrderedDict = None
from ..persistent.ndarray import PersistentNdArray
from ..persistent.parameters import ParameterInfo
from ..persistent.parameters import WithPersistentParameters


def test_persistent_parameters(mock_persistent):
    class MyParameters(WithPersistentParameters, parameters=["a", "b"]):
        def __init__(self, **defaults) -> None:
            defaults.setdefault("a", 1)
            super().__init__(**defaults)

    parameters = MyParameters()

    expected = {"a": 1}
    assert mock_persistent == expected
    assert parameters.a == 1
    assert parameters.b is None

    parameters.a = 2
    expected["a"] = 2
    assert mock_persistent == expected
    assert parameters.a == 2

    parameters = MyParameters()
    assert parameters.a == 2

    parameters.a = None
    expected["a"] = None
    assert mock_persistent == {}
    assert parameters.a is None
    assert parameters.b is None


def test_persistent_parameters_dict(mock_persistent):
    class MyParameters(WithPersistentParameters, parameters=["python_dict"]):
        def __init__(self, **defaults) -> None:
            defaults.setdefault("python_dict", dict())
            super().__init__(**defaults)

    parameters = MyParameters()
    expected = {}

    assert mock_persistent == {"python_dict": expected}
    assert parameters.python_dict == expected

    parameters.python_dict["a"] = 2
    parameters.python_dict["fix"] = -1
    expected["python_dict"] = {"a": 2, "fix": -1}
    assert mock_persistent == expected
    assert parameters.python_dict == expected["python_dict"]

    parameters.python_dict["a"] = {"x": 1, "fix": -2}
    expected["python_dict"]["a"] = {"x": 1, "fix": -2}
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"] == 1

    parameters.python_dict["a"]["x"] = {"y": 2, "fix": -3}
    expected["python_dict"]["a"]["x"] = {"y": 2, "fix": -3}
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"]["y"] == 2

    parameters.python_dict["a"]["x"]["y"] = 3
    expected["python_dict"]["a"]["x"]["y"] = 3
    assert mock_persistent == expected
    assert parameters.python_dict["a"]["x"]["y"] == 3


def test_persistent_ndarray(mock_bliss):
    python_arr = list()
    persistent_arr = PersistentNdArray("test")
    with pytest.raises(IndexError):
        persistent_arr[0]
    with pytest.raises(IndexError):
        persistent_arr[-1]
    numpy.testing.assert_array_equal(python_arr, persistent_arr[()])

    add = numpy.random.uniform(low=0, high=1, size=10)
    python_arr.append(add)
    persistent_arr.append(add)
    python_arr_copy = numpy.array(python_arr)
    numpy.testing.assert_array_equal(python_arr_copy[0], persistent_arr[0])
    numpy.testing.assert_array_equal(python_arr_copy[-1], persistent_arr[-1])
    numpy.testing.assert_array_equal(python_arr_copy, persistent_arr[()])

    add = numpy.random.uniform(low=0, high=1, size=(2, 10))
    python_arr.extend(add)
    persistent_arr.extend(add)
    python_arr_copy = numpy.array(python_arr)
    numpy.testing.assert_array_equal(python_arr_copy[0], persistent_arr[0])
    numpy.testing.assert_array_equal(python_arr_copy[-1], persistent_arr[-1])
    numpy.testing.assert_array_equal(python_arr_copy, persistent_arr[()])

    numpy.testing.assert_array_equal(python_arr_copy[2, 5:6], persistent_arr[2, 5:6])


def test_extend_persistent_ndarray_1d(mock_bliss):
    values = numpy.arange(10)
    persistent_arr = PersistentNdArray("test")
    persistent_arr.extend(values)

    numpy.testing.assert_array_equal(values[0], persistent_arr[0])
    numpy.testing.assert_array_equal(values[-1], persistent_arr[-1])
    numpy.testing.assert_array_equal(values, persistent_arr[()])
    numpy.testing.assert_array_equal(values[2:5], persistent_arr[2:5])


def test_persistent_ordered_dict(mock_bliss):
    python_dict = dict()
    persistent_dict = PersistentOrderedDict("test")
    python_dict["string"] = "abc"
    persistent_dict["string"] = "abc"
    python_dict["number"] = 123
    persistent_dict["number"] = 123
    python_dict["list"] = [123, 456]
    persistent_dict["list"] = [123, 456]
    python_dict["dict"] = {"key": "value"}
    persistent_dict["dict"] = {"key": "value"}
    assert python_dict == persistent_dict.get_all()


def test_persistent_parameter_deprecation(mock_persistent):
    class MyParameters(WithPersistentParameters, parameters=["a1", "b1"]):
        pass

    parameters = MyParameters()
    parameters.a1 = 10

    class MyParametersNew(
        WithPersistentParameters,
        parameters=[
            ParameterInfo("a2", deprecated_names=["a1"]),
            ParameterInfo("b2", deprecated_names=["b1"]),
        ],
    ):
        def __init__(self, **defaults) -> None:
            defaults.setdefault("a2", 20)
            super().__init__(**defaults)

    parameters = MyParametersNew()

    assert mock_persistent == {"a2": 10}
    assert parameters.a1 == 10
    assert parameters.b1 is None
    assert parameters.a2 == 10
    assert parameters.b2 is None

    parameters.b1 = 30
    assert mock_persistent == {"a2": 10, "b2": 30}
    assert parameters.a1 == 10
    assert parameters.b1 == 30
    assert parameters.a2 == 10
    assert parameters.b2 == 30

    parameters.a1 = None
    assert mock_persistent == {"b2": 30}
    assert parameters.a1 is None
    assert parameters.b1 == 30
    assert parameters.a2 is None
    assert parameters.b2 == 30

    parameters.a2 = 40
    assert mock_persistent == {"a2": 40, "b2": 30}
    assert parameters.a1 == 40
    assert parameters.b1 == 30
    assert parameters.a2 == 40
    assert parameters.b2 == 30


def test_persistent_class_attribute_deprecation(mock_persistent, caplog):
    caplog.set_level("WARNING")
    log_message = "'OLD' is deprecated and will be removed in a future version. Use 'NEW' instead."

    class MyParametersNew(
        WithPersistentParameters, deprecated_class_attributes={"OLD": "NEW"}
    ):
        NEW = "default_value"

    assert MyParametersNew.NEW == "default_value"
    assert MyParametersNew.OLD == "default_value"
    _check_warning(caplog, log_message)

    MyParametersNew.NEW = "value1"
    assert MyParametersNew.NEW == "value1"
    assert MyParametersNew.OLD == "value1"
    _check_warning(caplog, log_message)

    MyParametersNew.OLD = "value2"
    _check_warning(caplog, log_message)
    assert MyParametersNew.NEW == "value2"
    assert MyParametersNew.OLD == "value2"
    _check_warning(caplog, log_message)

    instance = MyParametersNew()
    assert instance.NEW == "value2"
    assert instance.OLD == "value2"
    _check_warning(caplog, log_message)

    instance.NEW = "value3"
    assert instance.NEW == "value3"
    assert instance.OLD == "value3"
    _check_warning(caplog, log_message)

    instance.OLD = "value4"
    _check_warning(caplog, log_message)
    assert instance.NEW == "value4"
    assert instance.OLD == "value4"
    _check_warning(caplog, log_message)

    assert MyParametersNew.NEW == "value2"
    assert MyParametersNew.OLD == "value2"
    _check_warning(caplog, log_message)

    with pytest.raises(
        AttributeError, match="'MyParametersNew' object has no attribute 'NO_ATTRIBUTE'"
    ):
        _ = instance.NO_ATTRIBUTE

    with pytest.raises(
        AttributeError, match="'MyParametersNew' object has no attribute 'NO_ATTRIBUTE'"
    ):
        MyParametersNew.NO_ATTRIBUTE

    class MyParametersNew2(MyParametersNew):
        NEW = "default_value"

    assert MyParametersNew2.NEW == "default_value"
    assert MyParametersNew2.OLD == "default_value"
    _check_warning(caplog, log_message)

    instance = MyParametersNew2()
    assert instance.NEW == "default_value"
    assert instance.OLD == "default_value"
    _check_warning(caplog, log_message)

    assert len(caplog.records) == 0


def _check_warning(caplog, expected_message):
    """Verify a single expected warning in caplog and ensure no other warnings exist."""
    assert len(caplog.records) == 1, "Unexpected number of warnings"
    record = caplog.records[0]
    assert record.levelname == "WARNING", f"Expected a WARNING, got {record.levelname}"
    assert expected_message in record.message, f"Unexpected warning: {record.message}"
    caplog.clear()
