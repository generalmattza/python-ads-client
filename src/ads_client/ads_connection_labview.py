from __future__ import annotations
import json
from typing import Optional, Any
import pyads

from ads_client import ADSConnection
from ads_client.ads_connection import logger
import ads_client.constants as constants


def get_connection_object(
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    ams_net_port: Optional[int] = None,
):
    """
    Get a connection object to a PLC.
    Can be used to parse arguments and create a connection object, if the target is not provided.
    """
    # If a target is provided, return it
    if target:
        if ams_net_id:
            logger.warning("Both target and ams_net_id are provided. Using target.")
        return target
    # If ams_net_id is provided, create a connection object
    if ams_net_id:
        return LabviewADSConnection(
            ams_net_id=ams_net_id,
            ip_address=ip_address,
            ams_net_port=ams_net_port,
        )
    # If no target or ams_net_id is provided, return None
    logger.warning("No target or ams_net_id provided. No connection object created.")
    return None


def close_connection(target: LabviewADSConnection):
    """
    Close the connection to a PLC.
    """
    target.close()


def write_magnet_structure(
    varName: str,
    value: Any,
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
):
    """Write magnet driver clusters to the PLC"""
    if target := get_connection_object(target, ams_net_id):
        target.write_structure_by_name(
            varName, value, structure_def=constants.MAGNET_STRUCTURE
        )


def write_tdklocal_structure(
    varName: str,
    value: Any,
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
    number_of_supplies: Optional[int] = 1,
):
    """Write TDK Local clusters to the PLC"""
    if target := get_connection_object(target, ams_net_id):
        target.write_structure_by_name(
            varName,
            value,
            structure_def=constants.TDKLOCAL_STRUCTURE,
            array_size=number_of_supplies,
        )


def write_hwconfig_structure(
    varName: str,
    value: Any,
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
):
    """Write hardware configuration clusters to the PLC"""
    if target := get_connection_object(target, ams_net_id):
        target.write_structure_by_name(
            varName, value, structure_def=constants.TDK_STRUCTURE
        )


def read_error_from_plc(
    varName: str,
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
    number_of_errors: Optional[int] = 1,
):
    """
    Read errors from a PLC.
    """
    if target := get_connection_object(target, ams_net_id):
        errors = target.read_structure_by_name(
            varName,
            structure_def=constants.ERROR_STRUCTURE,
            array_size=number_of_errors,
        )
        return json.dumps(errors)


def read_errors_from_plc(
    target: Optional[LabviewADSConnection] = None,
    ams_net_id: Optional[str] = None,
    number_of_errors: Optional[int] = 1,
):
    """
    Read errors from a PLC.
    """
    if target := get_connection_object(target, ams_net_id):
        with target:
            errors = [
                target.read_by_name(f"LV.aErrors[{i}]", pyads.PLCTYPE_STRING)
                for i in range(number_of_errors)
            ]
            return json.dumps(errors)


def read_from_plc(
    var_name: str, target: LabviewADSConnection = None, ams_net_id: str = None
):
    """
    Read a variable by name from a PLC.
    """
    if target := get_connection_object(target, ams_net_id):
        with target:
            return target.read_by_name(var_name)


class LabviewADSConnection(ADSConnection):
    pass
