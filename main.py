#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-01-01
# version ='0.0.1'
# ---------------------------------------------------------------------------
"""a_short_project_description"""
# ---------------------------------------------------------------------------

import logging
from logging.config import dictConfig

# Import the load_configs function
from config_loader import load_configs

LOGGING_CONFIG_FILEPATH = "config/logging.yaml"
APP_CONFIG_FILEPATH = "config/application.toml"

# Load user configurations using the config_loader module
configs = load_configs([APP_CONFIG_FILEPATH, LOGGING_CONFIG_FILEPATH])

# Configure logging using the specified logging configuration
dictConfig(configs["logging"])


def main():
    logging.info(configs["application"])


def test_ads_client():
    """Test the ADS client class."""
    import pyads.testserver
    from src.ads_client import ADSTarget
    import pyads

    # pyads_testserver = pyads.testserver.AdsTestServer()
    # handler = pyads.testserver.AdvancedHandler()

    # handler.add_variable(
    #     pyads.testserver.PLCVariable(
    #         "var1", bytes(8), ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL"
    #     )
    # )
    # handler.add_variable(
    #     pyads.testserver.PLCVariable(
    #         "var2", bytes(8), ads_type=pyads.constants.ADST_REAL64, symbol_type="LREAL"
    #     )
    # )
    # with pyads_testserver:
    client = ADSTarget(adsAddress="127.0.0.1.1.1", adsPort=48898)
    with client.connection:
        assert client.connection.is_open
        variables = (("var1", 1), ("var2", 2))
        client.batch_write_by_name(variables)
        varNames = ["var1", "var2"]
        data = client.readVariables(["var1", "var2"])
        print(data)


if __name__ == "__main__":
    # main()
    test_ads_client()
