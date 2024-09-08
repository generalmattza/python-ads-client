#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-09-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""ADSTarget class to manage the connection to an ADS target device"""
# ---------------------------------------------------------------------------


from typing import Any, Union
import pyads
import json
import logging
from prometheus_client import Counter

logger = logging.getLogger(__name__)


ERROR_STRUCTURE = (
    ("status", pyads.PLCTYPE_BOOL, 1),
    ("code", pyads.PLCTYPE_DINT, 1),
    ("source", pyads.PLCTYPE_STRING, 1),
)


class MonitoredConnection(pyads.Connection):

    open_events = Counter(
        name="ads_client_connection_open_events",
        documentation="Number of times the connection was opened",
        labelnames=["ams_net_id"],
    )
    close_events = Counter(
        name="ads_client_connection_close_events",
        documentation="Number of times the connection was closed",
        labelnames=["ams_net_id"],
    )
    write_events = Counter(
        name="ads_client_connection_write_events",
        documentation="Number of times a variable was written",
        labelnames=["ams_net_id"],
    )
    read_events = Counter(
        name="ads_client_connection_read_events",
        documentation="Number of times a variable was read",
        labelnames=["ams_net_id"],
    )

    def __init__(self, adsAddress: str, adsPort: str):
        super().__init__(adsAddress, adsPort)
        self.logger = logging.getLogger(__name__)

    def open(self):
        if self.is_open:
            return
        self.logger.info(f"Opening connection to {self.ip_address}")
        super().open()
        self.open_events.labels(self.ams_net_id).inc()

    def close(self):
        if not self.is_open:
            return
        self.logger.info(f"Closing connection to {self.ip_address}")
        super().close()
        self.close_events.labels(self.ams_net_id).inc()

    def read_by_name(self, varName: str) -> Any:
        self.logger.info(f"Reading variable {varName}")
        self.read_events.labels(self.ams_net_id).inc()
        return super().read_by_name(varName)

    def write_by_name(self, varName: str, value: Any) -> None:
        self.logger.info(f"Writing {value} to variable {varName}")
        self.write_events.labels(self.ams_net_id).inc()
        super().write_by_name(varName, value)

    def __repr__(self):
        return f"MonitoredConnection(ams_net_id={self.ams_net_id}, ip_address={self.ip_address}, port={self.ams_port})"


class ADSTarget:
    """Class to manage an ADS client connection"""

    def __init__(
        self,
        adsAddress: str = None,
        adsPort: str = pyads.PORT_TC3PLC1,
        name: str = None,
    ):
        self.adsAddress = adsAddress
        self.adsPort = adsPort
        self.name = name
        self.connection = self.create_connection(adsAddress, adsPort)

    def create_connection(
        self, adsAddress=None, adsPort=None, verify_is_open=False
    ) -> MonitoredConnection:
        """Creates a ads connection to Beckhoff PLC using the ads address."""
        if adsAddress is None and self.adsAddress is None:
            raise ValueError(
                "Cannot open ADS connection: No ads address provided. Specify a valid ads address."
            )
        if adsPort is None and self.adsPort is None:
            raise ValueError(
                "Cannot open ADS connection: No port provided. Specify a valid port."
            )
        adsAddress = adsAddress if adsAddress else self.adsAddress
        adsPort = adsPort if adsPort else self.adsPort

        logging.info(
            f"Creating connection to ADS target {("'" + self.name + "' ") if self.name else ""}at {adsAddress}:{adsPort}"
        )

        connection = MonitoredConnection(adsAddress, adsPort)

        if verify_is_open:
            with connection:
                assert connection.is_open

        return connection

    def write_by_name(self, varName: str, value: Any, verify: bool = False) -> None:
        """Write appropriate values to different types of PLC tags
        Uses the context manager to open and close the connection during the write operation
        """
        if self.connection.is_open:
            self.connection.write_by_name(varName, value)
            if verify:
                assert self.connection.read_by_name(varName) == value
        else:
            with self.connection as conn:
                conn.write_by_name(varName, value)
                if verify:
                    assert conn.read_by_name(varName) == value

    def batch_write_by_name(
        self, variables: Union[tuple, list, set], verify: bool = False
    ) -> None:
        """Write appropriate values to different types of PLC tags"""
        with self.connection:
            if isinstance(variables, (list, tuple, set)):
                for variable in variables:
                    if len(variable) != 2:
                        raise ValueError(
                            "Variable must be a tuple with the variable name and value"
                        )
                    self.write_by_name(*variable, verify)
            else:
                raise TypeError(
                    "'variables' arg must be a list, tuple, or set of tuples with the variable name and value"
                )
            return True

    def read_by_name(self, varName: str):
        """Read PLC tags using ads address and plc tag name"""
        if self.connection.is_open:
            return self.connection.read_by_name(varName)
        else:
            with self.connection as conn:
                return conn.read_by_name(varName)

    def batch_read_by_name(self, varNames: Union[str, list, tuple, set]):
        """Read one or multiple PLC tags using ads address and plc tag names"""
        with self.connection:
            # Check if varNames is a string (single variable)
            if isinstance(varNames, str):
                # Read a single variable
                return self.read_by_name(varNames)
            # If varNames is a container (list, tuple, set), iterate over it
            elif isinstance(varNames, (list, tuple, set)):
                # Read multiple variables
                return {varName: self.read_by_name(varName) for varName in varNames}
            else:
                raise TypeError("varNames must be a string or a container of strings")

    def read_errors(self, varName: str, numberOfErrors=1):
        """Read error messages from the client"""
        return json.dumps(
            self.connection.read_structure_by_name(
                varName, structure_def=ERROR_STRUCTURE, array_size=numberOfErrors
            )
        )


    def read_device_info(self):
        """Read device information from the client"""
        with self.connection:
            return self.connection.read_device_info()
        
