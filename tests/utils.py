import logging
import pyads
import pytest

from ads_client.ads_connection import ADSConnection

logger = logging.getLogger("testing")


def add_route(ams_net_id="127.0.0.1.1.1", ip_address="127.0.0.1"):
    try:
        pyads.add_route(ams_net_id, ip_address)
    except (pyads.ADSError, RuntimeError) as e:
        logger.warning(f"Unable to create route {e}. Continuing without route.")
        pass


def _testfunc_read_by_name(target: ADSConnection, variables: dict):
    """Function for testing single reading by name using the ADS client class."""
    # First write the variables to the PLC
    target.write_list_by_name(variables)
    # Then read the variables back
    read_variables = target.read_list_by_name(variables)
    # Assert that the read variables are equal to the written variables
    return variables == read_variables


def _testfunc_write_by_name(target: ADSConnection, variables: dict):
    """Function for testing single writing by name using the ADS client class."""
    for var_name, value in variables.items():
        target.write_by_name(var_name, value, verify=False)
    read_variables = target.read_list_by_name(variables)
    return variables == read_variables


def _testfunc_write_list_by_name(target: ADSConnection, variables: dict):
    """Function for testing multiple writing by name using the ADS client class."""
    target.write_list_by_name(variables, verify=False)
    return variables == target.read_list_by_name(variables)


def _testfunc_write_array_by_name(target: ADSConnection, variables: dict):
    """Function for testing writing an array by name using the ADS client class."""
    for var_name, value in variables.items():
        target.write_array_by_name(var_name, value, verify=False)
    read_variables = target.read_list_array_by_name(variables)
    return variables == read_variables


def _testfunc_write_list_array_by_name(target: ADSConnection, variables: dict):
    """Function for testing writing multiple arrays by name using the ADS client class."""
    target.write_list_array_by_name(variables, verify=False)
    read_variables = target.read_list_array_by_name(variables)
    return variables == read_variables


def _testfunc_read_array_by_name(target: ADSConnection, variables: dict):
    """Function for testing reading an array by name using the ADS client class."""
    # First write the variables to the PLC
    for var_name, value in variables.items():
        target.write_array_by_name(var_name, value)
    # Then read the variables back
    read_variables = {
        var_name: target.read_array_by_name(var_name) for var_name in variables
    }
    # Assert that the read variables are equal to the written variables
    return variables == read_variables


def _testfunc_get_all_symbols(target: ADSConnection):
    """Test function for getting all symbols using the ADS client class."""
    try:
        all_symbols = target.get_all_symbols()
    except pyads.ADSError:
        return False
    symbol_dict = {symbol.name: symbol for symbol in all_symbols}

    logger.debug("get_all_symbols:")
    for name, symbol in symbol_dict.items():
        logger.debug(f"{name}: {symbol}")
    return True


def _testfunc_get_all_symbol_values(target: ADSConnection):
    """Test function for getting all symbol values using the ADS client class."""
    try:
        all_symbols = target.get_all_symbols()
    except pyads.ADSError:
        return False
    symbol_values = {
        symbol.name: target.read_by_name(symbol.name) for symbol in all_symbols
    }
    for name, symbol in symbol_values.items():
        logger.debug(f"get_all_symbol_values: {name}: {symbol}")
    return True


def _testfunc_read_device_info(target: ADSConnection):
    """Test function for reading device info using the ADS client class."""
    try:
        device_info = target.read_device_info()
    except pyads.ADSError:
        return False
    logger.debug(f"read_device_info: {device_info}")
    return True


def _testfunc_false_read_by_name(
    target: ADSConnection, false_var_name: str = "FalseVarName"
):
    """Test function for reading by name using the ADS client class."""
    try:
        target.read_by_name(false_var_name)
        return False
    except pyads.ADSError:
        return True


def _testfunc_false_write_by_name(
    target: ADSConnection, false_var_name: str = "FalseVarName"
):
    """Test function for writing by name using the ADS client class."""
    try:
        target.write_by_name(false_var_name, 1)
        return False
    except pyads.ADSError:
        return True
