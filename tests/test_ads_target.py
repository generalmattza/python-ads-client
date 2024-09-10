import pytest
import pyads
from conftest import (
    TESTSERVER_VARIABLES_SMALL,
    TESTSERVER_ARRAY_VARIABLES_SMALL,
    TESTSERVER_VARIABLES_LARGE,
    TESTSERVER_ARRAY_VARIABLES_LARGE,
    # TESTSERVER_TOTAL_VARIABLES,
)
import logging


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
def test_read_by_name(testserver_advanced_small, testserver_target, variable_type):
    """Test single reading by name using the ADS client class."""
    variables = TESTSERVER_VARIABLES_SMALL[variable_type]
    [testserver_target.read_by_name(var_name) for var_name in variables]


def test_write_by_name(testserver_advanced, testserver_target):
    """Test single writing by name using the ADS client class."""
    for variable_type in TESTSERVER_VARIABLES:
        for variable in TESTSERVER_VARIABLES[variable_type].items():
            testserver_target.write_by_name(*variable, verify=True)


def test_read_write_list_by_name(testserver_advanced, testserver_target):
    """Test batch writing by name using the ADS client class."""
    for variable_type in TESTSERVER_VARIABLES:
        variables = TESTSERVER_VARIABLES[variable_type]
        # First write the variables so they can be read
        testserver_target.write_list_by_name(variables, verify=False)
        variables_read = testserver_target.read_list_by_name(variables)
        assert variables_read == variables


def test_write_list_by_name_verify(testserver_advanced, testserver_target):
    """Test batch writing by name with verification using the ADS client class."""
    for variable_type in TESTSERVER_VARIABLES:
        variables = TESTSERVER_VARIABLES[variable_type]
        testserver_target.write_list_by_name(variables, verify=True)


def test_write_by_name_verify(testserver_advanced, testserver_target):
    """Test writing by name with verification using the ADS client class."""
    for variable_type in TESTSERVER_VARIABLES:
        for variable in TESTSERVER_VARIABLES[variable_type].items():
            testserver_target.write_by_name(*variable, verify=True)


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
    assert len(all_symbols) == TESTSERVER_TOTAL_VARIABLES


def test_verify_ams_net_id():
    """Tests function to verify AMS NetID format"""
    from ads_client.ads_connection import verify_ams_net_id, AMSNetIDFormatError

    # Valid id
    verify_ams_net_id("127.123.12.34.1.1")

    # Invalid ids
    with pytest.raises(AMSNetIDFormatError):
        verify_ams_net_id("123.4.56.787.66.1")
        verify_ams_net_id("123.4.56.87.66.1.1")


def test_write_array_by_name(testserver_advanced, testserver_target):
    """Test writing an array by name using the ADS client class."""
    for variable_type in TESTSERVER_ARRAY_VARIABLES:
        for variable in TESTSERVER_ARRAY_VARIABLES[variable_type].items():
            testserver_target.write_array_by_name(*variable, verify=False)


def test_write_list_array_by_name(testserver_advanced, testserver_target):
    """Test writing multiple arrays by name using the ADS client class."""
    for variable_type in TESTSERVER_ARRAY_VARIABLES:
        variables = TESTSERVER_ARRAY_VARIABLES[variable_type]
        testserver_target.write_list_array_by_name(variables, verify=False)


def test_write_list_array_by_name_verify(testserver_advanced, testserver_target):
    """Test writing multiple arrays by name with verification using the ADS client class."""
    for variable_type in TESTSERVER_ARRAY_VARIABLES:
        variables = TESTSERVER_ARRAY_VARIABLES[variable_type]
        testserver_target.write_list_array_by_name(variables, verify=True)


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
def test_write_performance(
    benchmark, testserver_advanced, testserver_target, variable_type
):
    """Test the performance of writing by name using the ADS client class."""

    variables = TESTSERVER_VARIABLES[variable_type]

    def write_operation():
        for variable in variables.items():
            testserver_target.write_by_name(*variable, verify=False)

    # Use pytest-benchmark for timing
    # write_operation()
    benchmark(write_operation)

    # Optionally, you can assert something, like a maximum duration:
    # benchmark.extra_info['variable_count'] = len(variables)
