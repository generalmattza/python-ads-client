#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-09-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""Test fixtures for the ADS client class."""
# ---------------------------------------------------------------------------

import logging
from logging.config import dictConfig
import time
import pytest
import pyads

from ads_client import ADSConnection
from config_loader import load_configs

try:
    import pyads.testserver
except FileNotFoundError as e:
    logging.error(
        f"{e}. Check that TwinCAT software is installed and configured properly"
    )
    raise e

logger = logging.getLogger(__name__)

# Configure logging using the specified logging configuration
dictConfig(load_configs("config/logging.yaml"))

# Test server configuration
PYADS_TESTSERVER_ADS_ADDRESS = "127.0.0.1.1.1"
PYADS_TESTSERVER_ADS_PORT = 48898
PYADS_TESTSERVER_TIMEOUT_MS = 1000

# Test server variables definition
VALUE_DIMENSION = 10
TESTSERVER_VARNAMES = {
    "integers": [f"int{n}" for n in range(VALUE_DIMENSION)],
    "reals": [f"real{n}" for n in range(VALUE_DIMENSION)],
}

TESTSERVER_VALUES = {
    "integers": [n for n in range(VALUE_DIMENSION)],  # Integer values, e.g., ints
    "reals": [
        round(n * 1.1, 2) for n in range(VALUE_DIMENSION)
    ],  # Real values, e.g., floats
}
TESTSERVER_VARIABLES = {
    key: {
        name: value
        for name, value in zip(
            TESTSERVER_VARNAMES[key], TESTSERVER_VALUES[key]
        )
    }
    for key in TESTSERVER_VARNAMES
}

TESTSERVER_ARRAY_VARNAMES = {
    "integers": [f"integer_array{n}" for n in range(VALUE_DIMENSION)],
    "reals": [f"real_array{n}" for n in range(VALUE_DIMENSION)],
}
TESTSERVER_ARRAY_VALUES = {
    "integers": [
        [n * i for n in range(VALUE_DIMENSION)] for i in range(VALUE_DIMENSION)
    ],
    "reals": [
        [round(n * i * 1.1, 2) for n in range(VALUE_DIMENSION)]
        for i in range(VALUE_DIMENSION)
    ],
}
TESTSERVER_ARRAY_VARIABLES = {
    key: {
        name: value
        for name, value in zip(
            TESTSERVER_ARRAY_VARNAMES[key],
            TESTSERVER_ARRAY_VALUES[key],
        )
    }
    for key in TESTSERVER_ARRAY_VARNAMES
}
def get_total_length(nested_dict: dict) -> int:
    """
    Get the total number of key-value pairs in a nested dictionary.
    
    Args:
    - nested_dict (dict): A dictionary where values are themselves dictionaries.

    Returns:
    - int: The total number of key-value pairs across all nested dictionaries.
    """
    return sum(len(sub_dict) for sub_dict in nested_dict.values())
# Total number of variables in the test server for verification
TESTSERVER_TOTAL_VARIABLES = get_total_length(TESTSERVER_VARIABLES) + get_total_length(TESTSERVER_ARRAY_VARIABLES)

# Test fixtures
@pytest.fixture
def testserver_target():
    """Fixture to create an instance of the ADS client class."""
    target = ADSConnection(
        ams_net_id=PYADS_TESTSERVER_ADS_ADDRESS, ams_net_port=PYADS_TESTSERVER_ADS_PORT
    )
    target.set_timeout(PYADS_TESTSERVER_TIMEOUT_MS)

    with target:
        yield target


@pytest.fixture(scope="session")
def testserver_advanced():

    try:
        pyads.add_route("127.0.0.1.1.1", "127.0.0.1")
    except (pyads.ADSError, RuntimeError) as e:
        logger.warning(f"Unable to create route {e}. Continuing without route.")
        pass

    handler = pyads.testserver.AdvancedHandler()

    def get_variable_kwargs(variable_type: str, initial_value: bytes = bytes(8)):
        """Function to get the keyword arguments for creating a PLCVariable."""
        if variable_type == "integers":
            return dict(value=initial_value, ads_type=pyads.constants.ADST_INT16, symbol_type="LINT")
        elif variable_type == "reals":
            return dict(value=initial_value, ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL")
        else:
            raise ValueError(f"Unknown variable type: {variable_type}")
        
    for var_type, variables in TESTSERVER_VARIABLES.items():
        for var_name in variables:
            handler.add_variable(
                pyads.testserver.PLCVariable(
                    var_name,
                    **get_variable_kwargs(var_type)
                )
            )

    for var_type, variables in TESTSERVER_ARRAY_VARIABLES.items():
        for var_name in variables:
            kwargs = get_variable_kwargs(var_type)
            handler.add_variable(
                pyads.testserver.PLCVariable(
                    var_name,
                    value=kwargs["value"],
                    ads_type=kwargs["ads_type"] * VALUE_DIMENSION,
                    symbol_type=kwargs["symbol_type"],
                )
            )

    pyads_testserver = pyads.testserver.AdsTestServer(handler)
    # Wait a bit to ensure the server has time to start
    time.sleep(0.5)

    # Yield control to the tests, then cleanup after tests
    with pyads_testserver:
        yield pyads_testserver
