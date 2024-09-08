#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Created By  : Matthew Davidson
# Created Date: 2023-01-23
# version ='1.0'
# ---------------------------------------------------------------------------
"""a_short_module_description"""
# ---------------------------------------------------------------------------
"""

Author  : Eric Cessford
Date    : 4 / 26 / 2023

Python / LabVIEW interface that is intended to be called by LabVIEW to 
    - Read      : readFromPLC()
                : readErrorFromPLC()
                : readMagnetsFromPLC()
    - Write     : writeToPLC()
                : writeMagnetsToPLC()
"""

import pyads
import json, yaml
import logging

logger = logging.getLogger(__name__)


def openADSConnection(adsAddress, adsPort=pyads.PORT_TC3PLC1):
    """Open an ads connection to Beckhoff PLC using the ads address."""
    connection = pyads.Connection(adsAddress, adsPort)
    assert connection.is_open
    return connection


class LoggedConnection(pyads.Connection):

    def __init__(self, adsAddress, adsPort):
        super().__init__(adsAddress, adsPort)
        self.logger = logging.getLogger(__name__)
        self.open_events = 0
        self.close_events = 0

    def open(self):
        self.logger.info(f"Opening connection to {self.ip_address}")
        self.open_events += 1
        super().open()

    def close(self):
        self.logger.info(f"Closing connection to {self.ip_address}")
        self.close_events += 1
        super().close()

    def read_by_name(self, varName):
        self.logger.info(f"Reading variable {varName}")
        return super().read_by_name(varName)

    def write_by_name(self, varName, value):
        self.logger.info(f"Writing {value} to variable {varName}")
        return super().write_by_name(varName, value)

    def __repr__(self):
        return f"LoggedConnection(ip_address={self.ip_address}, port={self.ams_port}, open_events={self.open_events}, close_events={self.close_events})"


class ADSClient:
    """Class to manage an ADS client connection"""

    def __init__(self, adsAddress=None, adsPort=pyads.PORT_TC3PLC1):
        self.adsAddress = adsAddress
        self.adsPort = adsPort
        self.connection = self.createConnection(adsAddress, adsPort)

    def createConnection(self, adsAddress=None, adsPort=None):
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

        connection = LoggedConnection(adsAddress, adsPort)

        with connection:
            assert connection.is_open

        return connection

    def writeVariable(self, varName, value, checkValue=True):
        """Write appropriate values to different types of PLC tags
        Uses the context manager to open and close the connection during the write operation
        """
        with self.connection as adsTarget:
            adsTarget.write_by_name(varName, value)
            if checkValue:
                assert adsTarget.read_by_name(varName) == value
            return

    def _writeVariable(self, adsTarget, varName, value, checkValue=True) -> None:
        """Write appropriate values to different types of PLC tags
        Does not open or close the connection during the write operation"""
        adsTarget.write_by_name(varName, value)
        if checkValue:
            assert adsTarget.read_by_name(varName) == value
        return

    def writeVariables(self, variables, checkValue=True):
        """Write appropriate values to different types of PLC tags"""
        with self.connection as adsTarget:
            if isinstance(variables, (list, tuple, set)):
                for variable in variables:
                    if len(variable) != 2:
                        raise ValueError(
                            "Variable must be a tuple with the variable name and value"
                        )
                    self._writeVariable(adsTarget, *variable, checkValue)
            else:
                raise TypeError(
                    "'variables' arg must be a list, tuple, or set of tuples with the variable name and value"
                )
            return True

    def readVariable(self, varName):
        """Read PLC tags using ads address and plc tag name"""
        with self.connection as adsTarget:
            return adsTarget.read_by_name(varName)

    def _readVariable(self, adsTarget, varName):
        """Read PLC tags using ads address and plc tag name
        Does not open or close the connection during the read operation"""
        return adsTarget.read_by_name(varName)

    def readVariables(self, varNames):
        """Read one or multiple PLC tags using ads address and plc tag names"""
        try:
            with self.connection as adsTarget:
                # Check if varNames is a string (single variable)
                if isinstance(varNames, str):
                    # Read a single variable
                    return self._readVariable(adsTarget, varNames)
                # If varNames is a container (list, tuple, set), iterate over it
                elif isinstance(varNames, (list, tuple, set)):
                    # Read multiple variables
                    return {
                        varName: self._readVariable(adsTarget, varName)
                        for varName in varNames
                    }
                else:
                    raise TypeError(
                        "varNames must be a string or a container of strings"
                    )
        except Exception as e:
            return f"Something went wrong: {e}"

    # def readErrors(self,varName, adsAddress=adsAddress, numberOfErrors=1):
    #     try:
    #         plc = openADSConnection(adsAddress)
    #         plc.open()
    #         error_structure = (
    #             ("status", pyads.PLCTYPE_BOOL, 1),
    #             ("code", pyads.PLCTYPE_DINT, 1),
    #             ("source", pyads.PLCTYPE_STRING, 1),
    #         )
    #         return json.dumps(
    #             plc.read_structure_by_name(
    #                 varName, structure_def=error_structure, array_size=numberOfErrors
    #             )
    #         )
    #     except Exception as e:
    #         return f"Something went wrong {e}"
    #     finally:
    #         plc.close()


# def readMagnetsFromPLC(varName, adsAddress=adsAddress):
#     """Read magnet driver structs from the PLC"""
#     try:
#         plc = openADSConnection(adsAddress)
#         plc.open()
#         magnet_structure = (
#             ("Enable", pyads.PLCTYPE_BOOL, 1),
#             ("Driver Safety Limit Current (A)", pyads.PLCTYPE_INT, 1),
#             ("Max Driver Current (A)", pyads.PLCTYPE_INT, 1),
#             ("Feedback Max (A)", pyads.PLCTYPE_INT, 1),
#             ("Desired Current (A)", pyads.PLCTYPE_INT, 1),
#             ("On time (ms)", pyads.PLCTYPE_INT, 1),
#             ("Time offset (ms)", pyads.PLCTYPE_INT, 1),
#             ("Current (A)", pyads.PLCTYPE_REAL, 1000),
#         )
#         return json.dumps(
#             plc.read_structure_by_name(varName, structure_def=magnet_structure)
#         )
#     except Exception as e:
#         return f"Something went wrong {e}"
#     finally:
#         plc.close()


# def writeMagnetsToPLC(varName, value, adsAddress=adsAddress):
#     """Write magnet driver clusters to the PLC"""
#     try:
#         plc = openADSConnection(adsAddress)
#         plc.open()
#         magnet_structure = (
#             ("Enable", pyads.PLCTYPE_BOOL, 1),
#             ("Max Driver Current (A)", pyads.PLCTYPE_INT, 1),
#             ("Feedback Max (A)", pyads.PLCTYPE_INT, 1),
#             ("Desired Current (A)", pyads.PLCTYPE_INT, 1),
#             ("On time (ms)", pyads.PLCTYPE_INT, 1),
#             ("Time offset (ms)", pyads.PLCTYPE_INT, 1),
#             ("Current (A)", pyads.PLCTYPE_REAL, 1000),
#         )
#         plc.write_structure_by_name(
#             varName, json.loads(value), structure_def=magnet_structure
#         )
#     except Exception as e:
#         return f"Something went wrong {e}"
#     finally:
#         plc.close()
