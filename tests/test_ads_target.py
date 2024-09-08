import pytest
import pyads
from conftest import PYADS_TESTSERVER_VARIABLE_NAMES

TEST_VAR_NAMES = PYADS_TESTSERVER_VARIABLE_NAMES
TEST_VARIABLES = [(var_name, n) for var_name, n in zip(TEST_VAR_NAMES, range(12))]


def test_read_by_name(testserver_advanced, testserver_target):
    """Test single reading by name using the ADS client class."""

    [testserver_target.read_by_name(var_name) for var_name in TEST_VAR_NAMES]


def test_write_by_name(testserver_advanced, testserver_target):
    """Test single writing by name using the ADS client class."""

    [testserver_target.write_by_name(var_name, 0) for var_name in TEST_VAR_NAMES]


def test_batch_write_by_name(testserver_advanced, testserver_target):
    """Test batch writing by name using the ADS client class."""

    testserver_target.batch_write_by_name(TEST_VARIABLES)


def test_batch_read_by_name(testserver_advanced, testserver_target):
    """Test batch reading by name using the ADS client class."""

    testserver_target.batch_read_by_name(TEST_VAR_NAMES)


def test_write_by_name_verify(testserver_advanced, testserver_target):
    """Test writing by name with verification using the ADS client class."""

    [
        testserver_target.write_by_name(var_name, 1, verify=True)
        for var_name in TEST_VAR_NAMES
    ]


def test_batch_write_by_name_verify(testserver_advanced, testserver_target):
    """Test batch writing by name with verification using the ADS client class."""

    testserver_target.batch_write_by_name(TEST_VARIABLES, verify=True)


def test_read_device_info(testserver_advanced, testserver_target):
    """Test reading device info using the ADS client class."""

    testserver_target.read_device_info()


def test_false_read_by_name(testserver_advanced, testserver_target):
    """Test reading by name using the ADS client class."""
    with pytest.raises(pyads.ADSError):
        testserver_target.read_by_name("FalseVarName")


def test_false_write_by_name(testserver_advanced, testserver_target):
    """Test writing by name using the ADS client class."""
    with pytest.raises(pyads.ADSError):
        testserver_target.write_by_name("FalseVarName", 0)


def test_get_all_symbols(testserver_advanced, testserver_target):
    """Test getting all symbols using the ADS client class."""
    all_symbols = testserver_target.get_all_symbols()
    assert len(all_symbols) == len(TEST_VAR_NAMES)
