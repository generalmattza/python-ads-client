import pytest
import pyads
from conftest import (
    TEST_DATASET,
    # TESTSERVER_TOTAL_VARIABLES,
)
import logging
from utils import (
    _testfunc_read_by_name,
    _testfunc_write_by_name,
    _testfunc_write_list_by_name,
    _testfunc_get_all_symbols,
    _testfunc_get_all_symbol_values,
    _testfunc_read_array_by_name,
    _testfunc_write_array_by_name,
    _testfunc_write_list_array_by_name,
    _testfunc_read_device_info,
    _testfunc_false_read_by_name,
    _testfunc_false_write_by_name,
)


# Read/Write Operations Testing
# ################################################################################################


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
@pytest.mark.parametrize("dataset", {"single_small"})
def test_read_by_name(
    testserver_advanced,
    testserver_target,
    variable_type,
    dataset,
):
    """Test single reading by name using the ADS client class."""
    variables = TEST_DATASET[dataset][variable_type]
    assert _testfunc_read_by_name(target=testserver_target, variables=variables)


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
@pytest.mark.parametrize("dataset", {"single_small"})
def test_write_by_name(
    testserver_advanced,
    testserver_target,
    variable_type,
    dataset,
):
    """Test single writing by name using the ADS client class."""
    variables = TEST_DATASET[dataset][variable_type]
    assert _testfunc_write_by_name(target=testserver_target, variables=variables)


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
@pytest.mark.parametrize("dataset", {"single_small"})
def test_read_write_list_by_name(
    testserver_advanced, testserver_target, variable_type, dataset
):
    """Test batch writing by name using the ADS client class. Perform a manual verification."""
    variables = TEST_DATASET[dataset][variable_type]
    assert _testfunc_write_list_by_name(target=testserver_target, variables=variables)


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
@pytest.mark.parametrize("dataset", {"single_small"})
def test_write_list_by_name(
    testserver_advanced, testserver_target, variable_type, dataset
):
    """Test batch writing by name with verification using the ADS client class."""
    variables = TEST_DATASET[dataset][variable_type]
    assert _testfunc_write_list_by_name(testserver_target, variables)


# @pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
# @pytest.mark.parametrize("dataset", {"array_small"})
# def test_write_array_by_name(
#     testserver_advanced, testserver_target, variable_type, dataset
# ):
#     """Test writing an array by name using the ADS client class."""
#     variables = TEST_DATASET[dataset][variable_type]
#     assert _testfunc_write_array_by_name(testserver_target, variables)


# @pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
# @pytest.mark.parametrize("dataset", {"array_small"})
# def test_read_array_by_name(
#     testserver_advanced, testserver_target, variable_type, dataset
# ):
#     """Test reading an array by name using the ADS client class."""
#     variables = TEST_DATASET[dataset][variable_type]
#     # array_size = length of the first array in the dataset
#     # array_size = len(variables[list(variables.keys())[0]])
#     assert _testfunc_read_array_by_name(testserver_target, variables)


def test_false_read_by_name(testserver_advanced, testserver_target):
    """Test reading by name using the ADS client class."""
    assert _testfunc_false_read_by_name(testserver_target)


def test_false_write_by_name(testserver_advanced, testserver_target):
    """Test writing by name using the ADS client class."""
    assert _testfunc_false_write_by_name(testserver_target)


# Utility function testing
# ################################################################################################
def test_read_device_info(testserver_advanced, testserver_target):
    """Test reading device info using the ADS client class."""
    assert _testfunc_read_device_info(testserver_target)


def test_get_all_symbols(testserver_advanced, testserver_target):
    """Test getting all symbols using the ADS client class."""
    assert _testfunc_get_all_symbols(testserver_target)


def test_get_all_symbol_values(testserver_advanced, testserver_target):
    """Test getting all symbol values using the ADS client class."""
    assert _testfunc_get_all_symbol_values(testserver_target)


def test_verify_ams_net_id():
    """Tests function to verify AMS NetID format"""
    from ads_client.ads_connection import verify_ams_net_id, AMSNetIDFormatError

    # Valid id
    verify_ams_net_id("127.123.12.34.1.1")

    # Invalid ids
    with pytest.raises(AMSNetIDFormatError):
        verify_ams_net_id("123.4.56.787.66.1")
        verify_ams_net_id("123.4.56.87.66.1.1")


# Performance testing
# ################################################################################################


@pytest.mark.parametrize("variable_type", {"integers", "reals", "bools"})
@pytest.mark.parametrize("dataset", {"single_small", "single_large"})
def test_write_performance(
    benchmark, testserver_advanced, testserver_target, variable_type, dataset
):
    """Test the performance of writing by name using the ADS client class."""

    variables = TEST_DATASET[dataset][variable_type]

    def write_operation():
        testserver_target.write_list_by_name(variables, verify=False)

    # Use pytest-benchmark for timing
    # write_operation()
    benchmark(write_operation)

    # Optionally, you can assert something, like a maximum duration:
    # benchmark.extra_info['variable_count'] = len(variables)
