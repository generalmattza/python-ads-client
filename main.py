#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-01-01
# version ='0.0.1'
# ---------------------------------------------------------------------------
"""a_short_project_description"""
# ---------------------------------------------------------------------------

import time
import logging
from logging.config import dictConfig

# Import the load_configs function
from config_loader import load_configs

from ads_client.ads_connection import ADSConnection

LOGGING_CONFIG_FILEPATH = "config/logging.yaml"
APP_CONFIG_FILEPATH = "config/application.toml"

# Load user configurations using the config_loader module
configs = load_configs([APP_CONFIG_FILEPATH, LOGGING_CONFIG_FILEPATH])

# Configure logging using the specified logging configuration
dictConfig(configs["logging"])


def main():
    logging.info(configs["application"])


def test_plc():
    # ams_net_id = "5.107.220.90.1.1"
    ams_net_id = "5.109.60.19.1.1"

    connection = ADSConnection(
        ams_net_id=ams_net_id, ip_address="10.10.32.24", ams_net_port=851
    )

    connection.open()

    assert connection.is_open

    while True:
        data = {
            "MAIN.nVar1": 100,
            "MAIN.nVar2": 200,
            "MAIN.nVar3": 300,
            "MAIN.nVar4": 400,
            "MAIN.bool1": True,
            "MAIN.bool2": False,
        }
        connection.write_list_by_name(data)
        time.sleep(0.1)


if __name__ == "__main__":
    # main()
    test_plc()
