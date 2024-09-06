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


def openADSConnection(adsAddress, port=pyads.PORT_TC3PLC1):
    """Open an ads connection to Beckhoff PLC using the ads address."""
    plc = pyads.Connection(adsAddress, port)
    # TODO Run some checks to ensure the connection is open
    return plc


class ADSTarget:
    """Class to manage the ADS target connection"""

    def __init__(self, adsAddress=None, adsPort=pyads.PORT_TC3PLC1):
        self.adsAddress = adsAddress
        self.adsPort = adsPort
        self._adsTarget = None

    def createConnection(self, adsAddress=None, adsPort=pyads.PORT_TC3PLC1):
        """Creates an ads connection to Beckhoff PLC using the ads address."""
        if adsAddress is None and self.adsAddress is None:
            raise ValueError(
                "Cannot open ADS connection: No ads address provided. Specify a valid ads address."
            )
        if adsPort is None and self.port is None:
            raise ValueError(
                "Cannot open ADS connection: No port provided. Specify a valid port."
            )

        adsAddress = adsAddress if adsAddress else self.adsAddress
        adsTarget = pyads.Connection(adsAddress, adsPort)
        return adsTarget

    def close(self):
        """Close PLC connection."""
        self.adsTarget.close()

    def open(self):
        """Open PLC connection."""
        self.adsTarget.open()

    @property
    def adsTarget(self):
        if self._adsTarget is None:
            logger.info("No ADS target exists. Opening new ADS connection to target")
            self._adsTarget = self.createConnection()
        return self._adsTarget

    @adsTarget.setter
    def adsTarget(self, adsConnection):
        self._adsTarget = adsConnection

    @property
    def is_open(self):
        """Check if the connection is open."""
        return self.adsTarget.is_open

    def __enter__(self):
        return self.adsTarget

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.adsTarget.close()


class ADSClient:
    """Class to manage an ADS client connection"""

    def __init__(self, adsAddress=None, adsPort=pyads.PORT_TC3PLC1):
        self.adsAddress = adsAddress
        self.adsPort = adsPort

    def openConnection(self, adsAddress=None, adsPort=pyads.PORT_TC3PLC1):
        """Open an ads connection to Beckhoff PLC using the ads address."""
        if adsAddress is None and self.adsAddress is None:
            raise ValueError(
                "Cannot open ADS connection: No ads address provided. Specify a valid ads address."
            )
        if adsPort is None and self.port is None:
            raise ValueError(
                "Cannot open ADS connection: No port provided. Specify a valid port."
            )

        adsAddress = adsAddress if adsAddress else self.adsAddress
        self.adsTarget = ADSTarget(adsAddress, adsPort)
        self.adsTarget.open()

    def _writeVariable(self, adsTarget, varName, value, checkValue=True):
        """Write appropriate values to different types of PLC tags"""
        adsTarget.write_by_name(varName, value)
        if checkValue:
            assert adsTarget.read_by_name(varName) == value
        return True

    def writeVariables(self, *varNames, value, checkValue=True):
        """Write appropriate values to different types of PLC tags"""
        try:
            with self.adsTarget as adsTarget:
                if isinstance(varNames, str):
                    self._writeVariable(adsTarget, varNames, value, checkValue)
                elif isinstance(varNames, (list, tuple, set)):
                    for varName in varNames:
                        self._writeVariable(adsTarget, varName, value, checkValue)
                return True
        except Exception as e:
            return f"Something went wrong {e}"

    def _readVariable(self, adsTarget, varName):
        """Read PLC tags using ads address and plc tag name"""
        return adsTarget.read_by_name(varName)

    def readVariables(self, varNames):
        """Read one or multiple PLC tags using ads address and plc tag names"""
        try:
            with self.adsTarget as adsTarget:
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
