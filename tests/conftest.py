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
PYADS_TESTSERVER_IP_ADDRESS = "127.0.0.1"
PYADS_TESTSERVER_ADS_PORT = 48898
PYADS_TESTSERVER_TIMEOUT_MS = 1000


def generate_dataset(dimension1, dimension2=None):
    """
    Generate a dataset with integers and real values.

    If dimension2 is None, it generates single values.
    If dimension2 is provided, it generates arrays with the second dimension size.
    """

    # Generate names
    names = {
        "integers": [
            f"integer{'_array' if dimension2 else ''}{n}" for n in range(dimension1)
        ],
        "reals": [
            f"real{'_array' if dimension2 else ''}{n}" for n in range(dimension1)
        ],
        "bools": [
            f"bool{'_array' if dimension2 else ''}{n}" for n in range(dimension1)
        ],
    }

    # Generate values based on whether it's a regular or array dataset
    if dimension2:
        values = {
            "integers": [[n * i for n in range(dimension1)] for i in range(dimension2)],
            "reals": [
                [round(n * i * 1.1, 2) for n in range(dimension1)]
                for i in range(dimension2)
            ],
            "bools": [
                [n % 2 == 0 for n in range(dimension1)] for i in range(dimension2)
            ],
        }
    else:
        values = {
            "integers": [n for n in range(dimension1)],
            "reals": [round(n * 1.1, 2) for n in range(dimension1)],
            "bools": [n % 2 == 0 for n in range(dimension1)],
        }

    # Combine names and values
    return {
        key: {name: value for name, value in zip(names[key], values[key])}
        for key in names
    }


def get_variable_kwargs(variable_type: str, initial_value: bytes = bytes(8)):
    """Function to get the keyword arguments for creating a PLCVariable."""
    if variable_type == "integers":
        return dict(
            value=initial_value,
            ads_type=pyads.constants.ADST_INT16,
            symbol_type="LINT",
        )
    elif variable_type == "reals":
        return dict(
            value=initial_value,
            ads_type=pyads.constants.ADST_REAL64,
            symbol_type="LREAL",
        )
    elif variable_type == "bools":
        return dict(
            value=initial_value,
            ads_type=pyads.constants.ADST_INT8,
            symbol_type="BOOL",
        )
    else:
        raise ValueError(f"Unknown variable type: {variable_type}")


def get_total_length(variables):
    """Function to get the total length of all variables in a dataset."""
    if isinstance(variables, list):
        return sum(get_total_length(variable) for variable in variables)
    return sum(len(variables[key]) for key in variables)


TESTSERVER_VARIABLES_SMALL = generate_dataset(10)
TESTSERVER_ARRAY_VARIABLES_SMALL = generate_dataset(1, 10)

TESTSERVER_VARIABLES_LARGE = generate_dataset(100)
TESTSERVER_ARRAY_VARIABLES_LARGE = generate_dataset(100, 100)

# TESTSERVER_VARNAMES = {
#     "integers": [f"int{n}" for n in range(VALUE_DIMENSION)],
#     "reals": [f"real{n}" for n in range(VALUE_DIMENSION)],
# }

# TESTSERVER_VALUES = {
#     "integers": [n for n in range(VALUE_DIMENSION)],  # Integer values, e.g., ints
#     "reals": [
#         round(n * 1.1, 2) for n in range(VALUE_DIMENSION)
#     ],  # Real values, e.g., floats
# }
# TESTSERVER_VARIABLES = {
#     key: {
#         name: value
#         for name, value in zip(TESTSERVER_VARNAMES[key], TESTSERVER_VALUES[key])
#     }
#     for key in TESTSERVER_VARNAMES
# }

# TESTSERVER_ARRAY_VARNAMES = {
#     "integers": [f"integer_array{n}" for n in range(VALUE_DIMENSION)],
#     "reals": [f"real_array{n}" for n in range(VALUE_DIMENSION)],
# }
# TESTSERVER_ARRAY_VALUES = {
#     "integers": [
#         [n * i for n in range(VALUE_DIMENSION)] for i in range(VALUE_DIMENSION)
#     ],
#     "reals": [
#         [round(n * i * 1.1, 2) for n in range(VALUE_DIMENSION)]
#         for i in range(VALUE_DIMENSION)
#     ],
# }
# TESTSERVER_ARRAY_VARIABLES = {
#     key: {
#         name: value
#         for name, value in zip(
#             TESTSERVER_ARRAY_VARNAMES[key],
#             TESTSERVER_ARRAY_VALUES[key],
#         )
#     }
#     for key in TESTSERVER_ARRAY_VARNAMES
# }


# Total number of variables in the test server for verification
# TESTSERVER_TOTAL_VARIABLES = get_total_length(TESTSERVER_VARIABLES) + get_total_length(
#     TESTSERVER_ARRAY_VARIABLES
# )


def add_route(ams_net_id="127.0.0.1.1.1", ip_address="127.0.0.1"):
    try:
        pyads.add_route(ams_net_id, ip_address)
    except (pyads.ADSError, RuntimeError) as e:
        logger.warning(f"Unable to create route {e}. Continuing without route.")
        pass


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


def add_variables(handler, variables):
    for var_type, variables in variables.items():
        for var_name in variables:
            try:
                len(variables[var_name])
            except TypeError:
                # Create a single variable
                handler.add_variable(
                    pyads.testserver.PLCVariable(
                        var_name, **get_variable_kwargs(var_type)
                    )
                )
                continue
            else:
                # Create an array variable
                kwargs = get_variable_kwargs(var_type)
                handler.add_variable(
                    pyads.testserver.PLCVariable(
                        var_name,
                        value=kwargs["value"],
                        ads_type=kwargs["ads_type"] * len(variables[var_name]),
                        symbol_type=kwargs["symbol_type"],
                    )
                )


def init_testserver_advanced(variables):
    handler = pyads.testserver.AdvancedHandler()
    add_variables(handler, variables)
    testserver = pyads.testserver.AdsTestServer(handler)
    time.sleep(1)
    add_route(
        ams_net_id=PYADS_TESTSERVER_ADS_ADDRESS,
        ip_address=PYADS_TESTSERVER_IP_ADDRESS,
    )
    return testserver


@pytest.fixture(scope="session")
def testserver_advanced_small():
    with init_testserver_advanced(TESTSERVER_VARIABLES_SMALL) as testserver:
        yield testserver
