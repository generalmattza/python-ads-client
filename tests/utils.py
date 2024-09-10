import logging

logger = logging.getLogger("testing")


def _testfunc_read_by_name(target, variable_list):
    """Function for testing single reading by name using the ADS client class."""
    for var_name in variable_list:
        target.read_by_name(var_name)


def _testfunc_write_by_name(target, variable_list, verify=False):
    """Function for testing single writing by name using the ADS client class."""
    for var_name, value in variable_list.items():
        target.write_by_name(var_name, value, verify=verify)


def _testfunc_get_all_symbols(target):
    """Test function for getting all symbols using the ADS client class."""
    all_symbols = target.get_all_symbols()
    symbol_dict = {symbol.name: symbol for symbol in all_symbols}

    logger.debug("get_all_symbols:")
    for name, symbol in symbol_dict.items():
        logger.debug(f"{name}: {symbol}")


def _testfunc_get_all_symbol_values(target):
    """Test function for getting all symbol values using the ADS client class."""
    all_symbols = target.get_all_symbols()
    symbol_values = {
        symbol.name: target.read_by_name(symbol.name) for symbol in all_symbols
    }
    for name, symbol in symbol_values.items():
        logger.debug(f"get_all_symbol_values: {name}: {symbol}")


def _testfunc_read_device_info(target):
    """Test function for reading device info using the ADS client class."""
    logger.debug(f"read_device_info: {target.read_device_info()}")
