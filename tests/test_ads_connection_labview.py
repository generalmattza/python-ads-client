from ads_client.ads_connection_labview import (
    LabviewADSConnection,
    get_connection_object,
)

from conftest import (
    PYADS_TESTSERVER_ADS_ADDRESS,
    PYADS_TESTSERVER_IP_ADDRESS,
    PYADS_TESTSERVER_ADS_PORT,
)


def test_get_connection_object(testserver_advanced):
    """Test getting a connection object to a PLC."""
    connection_object = get_connection_object(
        ams_net_id=PYADS_TESTSERVER_ADS_ADDRESS,
        ip_address=PYADS_TESTSERVER_IP_ADDRESS,
        ams_net_port=PYADS_TESTSERVER_ADS_PORT,
    )
    assert isinstance(connection_object, LabviewADSConnection)
    assert connection_object.ams_net_id == PYADS_TESTSERVER_ADS_ADDRESS
    assert connection_object.ip_address == PYADS_TESTSERVER_IP_ADDRESS
    assert connection_object.ams_net_port == PYADS_TESTSERVER_ADS_PORT
    assert connection_object.is_open is False

    with connection_object:
        assert connection_object.is_open is True
        assert connection_object.ams_net_id == PYADS_TESTSERVER_ADS_ADDRESS
        assert connection_object.ip_address == PYADS_TESTSERVER_IP_ADDRESS
        assert connection_object.ams_net_port == PYADS_TESTSERVER_ADS_PORT
