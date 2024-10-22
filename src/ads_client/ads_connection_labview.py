from __future__ import annotations
import logging

from ads_client import ADSConnection

from ads_client.ads_connection import logger


def get_connection_object(
    ams_net_id: str = None, ip_address: str = None, ams_net_port: int = None
):
    """
    Get a connection object to a PLC.
    """
    return LabviewADSConnection(
        ams_net_id=ams_net_id,
        ip_address=ip_address,
        ams_net_port=ams_net_port,
    )


def read_from_plc(
    var_name: str, target: LabviewADSConnection = None, ams_net_id: str = None
):
    """
    Read a variable by name from a PLC.
    """
    if target is None:
        target = LabviewADSConnection(ams_net_id=ams_net_id)
        if ams_net_id is not None:
            logger.warning("Both target and ams_net_id are provided. Using target.")

    with target as plc:
        return plc.read_by_name(var_name)


class LabviewADSConnection(ADSConnection):
    pass
