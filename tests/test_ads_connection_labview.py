import pytest


from ads_client.ads_connection_labview import (
    LabviewADSConnection,
    get_connection_object,
    read_from_plc,
)

from conftest import (
    PYADS_TESTSERVER_ADS_ADDRESS,
    PYADS_TESTSERVER_IP_ADDRESS,
    PYADS_TESTSERVER_ADS_PORT,
)


@pytest.fixture
def testserver_target(testserver_advanced):
    """Fixture to create a LabviewADSConnection object for testing."""
    # Use testserver_advanced to configure the connection
    return LabviewADSConnection(
        ams_net_id=PYADS_TESTSERVER_ADS_ADDRESS, ip_address=PYADS_TESTSERVER_IP_ADDRESS
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


def test_get_connection_object_with_target(testserver_target):
    """Test get_connection_object using an existing target."""
    target = get_connection_object(target=testserver_target)
    assert isinstance(target, LabviewADSConnection)


def test_get_connection_object_with_ams_net_id(testserver_advanced):
    """Test get_connection_object with AMS Net ID but no target."""
    ams_net_id = "127.0.0.1.1.1"
    target = get_connection_object(ams_net_id=ams_net_id)
    assert isinstance(target, LabviewADSConnection)
    assert target.ams_net_id == ams_net_id


def test_read_from_plc(testserver_target):
    """Test reading a variable from the PLC."""
    var_name = "PLCVar"
    result = read_from_plc(var_name, target=testserver_target)
    assert result is not None
    # Assuming the test server mock returns a valid result for the read operation
