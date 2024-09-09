#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2024-09-08
# version ='1.0'
# ---------------------------------------------------------------------------
"""ADSConnection class to manage the connection to an ADS target device"""
# ---------------------------------------------------------------------------


from typing import Any, Union
import pyads
import json
import logging
import re

from prometheus_client import Counter

logger = logging.getLogger(__name__)


ERROR_STRUCTURE = (
    ("status", pyads.PLCTYPE_BOOL, 1),
    ("code", pyads.PLCTYPE_DINT, 1),
    ("source", pyads.PLCTYPE_STRINGvalidate_ams_net_id, 1),
)

class AMSNetIDFormatError(Exception):
    """Custom exception for invalid AMS Net ID format."""
    
    def __init__(self, message: str):
        # Initialize the base Exception with the custom message
        super().__init__(message)
        self.message = message

def verify_ams_net_id(ams_net_id: str) -> bool:
    """Verify if the ams_net_id follows the format 'x.x.x.x.x.x' where x is an integer between 0 and 255."""
    
    # Regular expression to match 6 groups of integers (0-255) separated by dots
    pattern = r'^(\d{1,3}\.){5}\d{1,3}$'

    # First check if the format is correct with 6 parts separated by '.'
    if not re.match(pattern, ams_net_id):
        raise AMSNetIDFormatError('Invalid ams_net_id format, ensure that format is 6 parts separated by periods.')
    
    # Split the ams_net_id by dots and check each part is within the range 0-255
    parts = ams_net_id.split('.')
    if not all(0 <= int(part) <= 255 for part in parts):
        raise AMSNetIDFormatError('Invalid ams_net_id format, ensure that numerical values are integers within range 0-255')

# class MonitoredConnection(pyads.Connection):



#     def __init__(self, adsAddress: str, adsPort: str):
#         super().__init__(adsAddress, adsPort)
#         self.logger = logging.getLogger(__name__)

#     def open(self):
#         if self.is_open:
#             return
#         self.logger.debug(f"Opening connection to {self.ip_address}")
#         super().open()
#         self.open_events.labels(self.ams_net_id).inc()

#     def close(self):
#         if not self.is_open:
#             return
#         self.logger.debug(f"Closing connection to {self.ip_address}")
#         super().close()
#         self.close_events.labels(self.ams_net_id).inc()

#     def read_by_name(self, varName: str) -> Any:

#         return super().read_by_name(varName)

#     def write_by_name(self, varName: str, value: Any) -> None:
#         self.logger.debug(f"Writing {value} to variable {varName}")
#         self.write_events.labels(self.ams_net_id).inc()
#         super().write_by_name(varName, value)

#     def __repr__(self):
#         return f"MonitoredConnection(ams_net_id={self.ams_net_id}, ip_address={self.ip_address}, port={self.ams_port})"

class ADSConnection(pyads.Connection):
    """Class to manage an ADS client connection"""
    
    # Class-level metrics to be shared across instances
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

    def __init__(
        self,
        adsAddress: str,
        adsPort: str = pyads.PORT_TC3PLC1,
        name: str = None,
        verify_is_open: bool = False
    ):
        self.name = name

        # Verify adsAddress
        verify_ams_net_id(adsAddress)

        target_name = f"'{self.name}' " if self.name else ""
        logging.info(
            f"Creating connection to ADS target {target_name}at {adsAddress}:{adsPort}"
        )

        # Initialize the parent class (pyads.Connection)
        super().__init__(adsAddress, adsPort)

        # Ensure connection is open if requested
        if verify_is_open:
            self._ensure_open()

    def _ensure_open(self):
        """Ensure the connection is open using a context manager."""
        if not self.is_open:
            with self:
                assert self.is_open

    def write_by_name(self, varName: str, value: Any, verify: bool = False) -> None:
        """Write a value to a PLC variable."""
        with self:  # Using context manager to ensure connection is open
            super().write_by_name(varName, value)
            if verify:
                assert super().read_by_name(varName) == value

    def write_list_by_name(self, variables: dict, verify: bool = False) -> None:
        """Write multiple values to PLC variables."""
        with self:
            super().write_list_by_name(variables)

    def read_by_name(self, varName: str):
        """Read a PLC variable by name."""
        with self:
            return super().read_by_name(varName)

    def read_list_by_name(self, varNames: Union[str, list, tuple, set]):
        """Read multiple PLC variables by their names."""
        with self:
            return super().read_list_by_name(varNames)

    def read_errors(self, varName: str, number_of_errors=1):
        """Read error messages."""
        return json.dumps(
            self.read_structure_by_name(
                varName, structure_def=ERROR_STRUCTURE, array_size=number_of_errors
            )
        )

    def read_device_info(self):
        """Read device information."""
        with self:
            return super().read_device_info()

    def get_all_symbols(self):
        """Read all symbols from the client."""
        with self:
            return super().get_all_symbols()

    def set_timeout(self, timeout: int) -> None:
        """Set the timeout for the connection."""
        super().set_timeout(timeout)

    def open(self):
        if self.is_open:
            return
        logger.debug(f"Opening connection to {self.ip_address}")
        super().open()
        self.open_events.labels(self.ams_net_id).inc()

    def close(self):
        if not self.is_open:
            return
        logger.debug(f"Closing connection to {self.ip_address}")
        super().close()
        self.close_events.labels(self.ams_net_id).inc()

    def __repr__(self):
        return f"ADSTarget(adsAddress={self.ams_net_id}, adsPort={self.ams_net_port}, name={self.name})"

    def __enter__(self):
        """Open the connection when entering the context."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Close the connection when exiting the context."""
        self.close()


# class ADSConnection(pyads.Connection):
#     """Class to manage an ADS client connection"""
#     open_events = Counter(
#         name="ads_client_connection_open_events",
#         documentation="Number of times the connection was opened",
#         labelnames=["ams_net_id"],
#     )
#     close_events = Counter(
#         name="ads_client_connection_close_events",
#         documentation="Number of times the connection was closed",
#         labelnames=["ams_net_id"],
#     )
#     write_events = Counter(
#         name="ads_client_connection_write_events",
#         documentation="Number of times a variable was written",
#         labelnames=["ams_net_id"],
#     )
#     read_events = Counter(
#         name="ads_client_connection_read_events",
#         documentation="Number of times a variable was read",
#         labelnames=["ams_net_id"],
#     )
#     def __init__(
#         self,
#         adsAddress: str = None,
#         adsPort: str = pyads.PORT_TC3PLC1,
#         name: str = None,
#         verify_is_open: bool = False
#     ):
#         self.name = name

#         target_name = ("'" + self.name + "' ") if self.name else ""
#         logging.info(
#             f"Creating connection to ADS target {target_name}at {adsAddress}:{adsPort}"
#         )

#         super().__init__(adsAddress, adsPort)


#     def _ensure_connection(self):
#         if verify_is_open:
#             with self:
#                 assert self.is_open

#     def write_by_name(self, varName: str, value: Any, verify: bool = False) -> None:
#         """Write appropriate values to different types of PLC tags
#         Uses the context manager to open and close the connection during the write operation
#         """
#         if self.is_open:
#             super().write_by_name(varName, value)
#             if verify:
#                 assert super().read_by_name(varName) == value
#         else:
#             with self:
#                 super().write_by_name(varName, value)
#                 if verify:
#                     assert super().read_by_name(varName) == value

#     def write_list_by_name(self, variables: dict, verify: bool = False) -> None:
#         """Write appropriate values to different types of PLC tags"""
#         with self.connection:
#             super().write_list_by_name(variables)

#     def read_by_name(self, varName: str):
#         """Read PLC tags using ads address and plc tag name"""
#         if self.is_open:
#             return super().read_by_name(varName)
#         else:
#             with self:
#                 return super().read_by_name(varName)

#     def read_list_by_name(self, varNames: Union[str, list, tuple, set]):
#         """Read one or multiple PLC tags using ads address and plc tag names"""
#         with self:
#             return super().read_list_by_name(varNames)

#     def read_errors(self, varName: str, numberOfErrors=1):
#         """Read error messages from the client"""
#         return json.dumps(
#             self.read_structure_by_name(
#                 varName, structure_def=ERROR_STRUCTURE, array_size=numberOfErrors
#             )
#         )

#     def read_device_info(self):
#         """Read device information from the client"""
#         with self.connection:
#             return self.read_device_info()

#     def get_all_symbols(self):
#         """Read all symbols from the client"""
#         with self.connection:
#             return self.get_all_symbols()

#     def set_timeout(self, timeout: int) -> None:
#         """Set the timeout for the connection"""
#         self.set_timeout(timeout)

#     def open(self):
#         if self.is_open:
#             return
#         logger.debug(f"Opening connection to {self.ip_address}")
#         super().open()
#         self.open_events.labels(self.ams_net_id).inc()

#     def close(self):
#         if not self.is_open:
#             return
#         logger.debug(f"Closing connection to {self.ip_address}")
#         super().close()
#         self.close_events.labels(self.ams_net_id).inc()

#     def __repr__(self):
#         return f"ADSTarget(adsAddress={self.adsAddress}, adsPort={self.adsPort}, name={self.name})"

#     def __enter__(self):
#         self.open()
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.close()
